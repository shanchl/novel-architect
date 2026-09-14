#!/usr/bin/env python3
"""Run deterministic chapter checks for a novel-architect project.

This script uses only the Python standard library. It catches cheap,
mechanical problems and writes a durable gate report; it does not replace
manual continuity review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path

from scan_repetition import gate_issue as repetition_gate_issue
from scan_repetition import scan_chapter as scan_chapter_repetition


DEFAULT_REQUIRED_PRE_SECTIONS = [
    "Time Handoff",
    "New-Information Inventory",
    "Character Locations",
    "Character Knowledge",
    "Character Possessions and Access",
    "Information Chain",
    "Domain and Canon Constraints",
    "Blocking Risks",
]

DEFAULT_REQUIRED_POST_SECTIONS = [
    "Ending State",
    "New Facts",
    "Information Learned By Character",
    "Objects and Evidence",
    "State Updates",
    "Timeline Updates",
    "Summary Updates",
    "Residual Risks",
]

SECTION_ALIASES = {
    "Time Handoff": ["Time Handoff", "时间衔接", "时间咬合", "承接点"],
    "New-Information Inventory": ["New-Information Inventory", "新增信息清单", "新信息清单", "本章新增信息"],
    "Character Locations": ["Character Locations", "人物位置", "角色位置", "地点"],
    "Character Knowledge": ["Character Knowledge", "人物知情", "角色知情", "信息状态"],
    "Character Possessions and Access": ["Character Possessions and Access", "持有物", "权限", "物件与权限"],
    "Information Chain": ["Information Chain", "信息链", "信息来源"],
    "Domain and Canon Constraints": ["Domain and Canon Constraints", "设定约束", "领域约束", "术语一致性"],
    "Blocking Risks": ["Blocking Risks", "阻断风险", "硬伤", "残留风险"],
    "Ending State": ["Ending State", "结尾状态", "章节结束状态"],
    "New Facts": ["New Facts", "新增事实", "本章确立的事实"],
    "Information Learned By Character": ["Information Learned By Character", "角色获知信息", "人物获知信息"],
    "Objects and Evidence": ["Objects and Evidence", "物件与证据", "证据状态"],
    "State Updates": ["State Updates", "状态更新"],
    "Timeline Updates": ["Timeline Updates", "时间线更新"],
    "Summary Updates": ["Summary Updates", "摘要更新"],
    "Residual Risks": ["Residual Risks", "残留风险"],
}

RELATIVE_TIME_PATTERNS = [
    "昨天", "昨夜", "昨晚", "前天", "大前天", "今天", "今日", "今晚", "今夜", "明天", "明日",
    "后天", "三天前", "两天前", "两日前", "三日前", "上一夜", "这一夜", "同一夜", "天亮",
    "天快亮", "清晨", "黄昏", "傍晚", "半夜", "next day", "yesterday", "last night",
    "two days ago", "three days ago",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def parse_markdown_terms(path: Path) -> list[str]:
    if not path.exists():
        return []
    terms: list[str] = []
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value:
                terms.append(value)
    return terms


def parse_guardrails(path: Path) -> tuple[list[str], list[str]]:
    forbidden: list[str] = []
    whitelist: list[str] = []
    if not path.exists():
        return forbidden, whitelist
    mode = ""
    for line in read_text(path).splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("forbidden"):
            mode = "forbidden"
            continue
        if lower.startswith("whitelist") or lower.startswith("allowed"):
            mode = "whitelist"
            continue
        if stripped.startswith("- "):
            value = stripped[2:].strip().strip('"')
            if not value:
                continue
            if mode == "whitelist":
                whitelist.append(value)
            else:
                forbidden.append(value)
    return forbidden, whitelist


def section_present(text: str, section: str) -> bool:
    aliases = SECTION_ALIASES.get(section, [section])
    for alias in aliases:
        pattern = rf"^##+\s+.*{re.escape(alias)}.*$"
        if re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE):
            return True
    return False


def section_body(text: str, section: str) -> str | None:
    aliases = SECTION_ALIASES.get(section, [section])
    for alias in aliases:
        pattern = rf"^##+\s+[^\n]*{re.escape(alias)}[^\n]*\n(?P<body>.*?)(?=^##+\s+|\Z)"
        match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r"<!--.*?-->", "", match.group("body"), flags=re.DOTALL).strip()
    return None


def section_empty(text: str, section: str) -> bool:
    body = section_body(text, section)
    if body is None:
        return False
    without_unchecked = re.sub(r"(?m)^\s*-\s*\[\s\]\s*.*$", "", body).strip()
    normalized = without_unchecked.strip().lower()
    return not without_unchecked or normalized in {"todo", "tbd", "待补", "待定", "...", "…"}


def check_gate_file(path: Path, sections: list[str], label: str) -> list[str]:
    if not path.exists():
        return [f"FAIL P0 {label}: missing {path}"]
    text = read_text(path)
    failures = []
    for section in sections:
        if not section_present(text, section):
            failures.append(f"FAIL P1 {label}: missing section '{section}' in {path}")
    for section in sections:
        if section_present(text, section) and section_empty(text, section):
            failures.append(f"FAIL P1 {label}: section '{section}' is empty in {path}")
    return failures


def check_forbidden_terms(
    chapter_path: Path, text: str, terms: list[str], whitelist: list[str], severity: str = "WARN P2"
) -> list[str]:
    issues: list[str] = []
    for term in sorted(set(terms), key=len, reverse=True):
        if not term:
            continue
        search_start = 0
        while True:
            index = text.find(term, search_start)
            if index == -1:
                break
            window = text[max(0, index - 12): index + len(term) + 12]
            if any(allowed in window for allowed in whitelist):
                search_start = index + len(term)
                continue
            line = line_number(text, index)
            issues.append(f"{severity} forbidden_term: found '{term}' at {chapter_path}:{line}")
            search_start = index + len(term)
    return issues


def sentence_repetitions(chapter_path: Path, text: str) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[。！？!?])", text) if len(s.strip()) >= 8]
    counts = Counter(sentences)
    issues = []
    for sentence, count in counts.items():
        if count > 1:
            issues.append(f"WARN P2 repeated_sentence: {count}x in {chapter_path}: {sentence[:60]}")
    return issues


def check_required_outputs(project: Path, chapter: int, stage: str) -> list[str]:
    chapter_id = f"{chapter:04d}"
    required = [project / "06_chapters" / f"chapter_{chapter_id}.md"]
    if stage in {"post", "accept"}:
        required.extend([
            project / "07_summaries" / f"chapter_{chapter_id}_summary.md",
            project / "07_summaries" / f"chapter_{chapter_id}_short.md",
            project / "04_story" / "timeline.yaml",
            project / "08_memory" / "scene_clock.yaml",
            project / "08_memory" / "information_ledger.yaml",
        ])
    if stage == "accept":
        required.extend([
            project / "00_project" / "status.yaml",
            project / "08_memory" / "deltas" / f"chapter_{chapter_id}.json",
            project / "08_memory" / "freshness.json",
        ])
    issues = []
    for path in required:
        if not path.exists():
            issues.append(f"FAIL P0 required_output: missing {path}")
        elif path.suffix != ".jsonl" and not read_text(path).strip():
            issues.append(f"FAIL P1 required_output: empty {path}")
    return issues


def check_freshness(project: Path, chapter: int) -> list[str]:
    freshness = project / "08_memory" / "freshness.json"
    if not freshness.exists():
        return [f"FAIL P0 freshness: missing {freshness}"]
    try:
        import json
        data = json.loads(read_text(freshness))
    except (ValueError, OSError) as exc:
        return [f"FAIL P1 freshness: invalid JSON in {freshness}: {exc}"]
    required = [
        f"07_summaries/chapter_{chapter:04d}_summary.md",
        f"07_summaries/chapter_{chapter:04d}_short.md",
        "04_story/timeline.yaml",
        "08_memory/scene_clock.yaml",
        "08_memory/information_ledger.yaml",
    ]
    issues = []
    for rel in required:
        entry = data.get(rel, {})
        if int(entry.get("canon_through_chapter", -1)) < chapter:
            issues.append(f"FAIL P1 freshness: {rel} is not current through chapter {chapter:04d}")
            continue
        path = project / rel
        if path.exists() and entry.get("sha256"):
            import hashlib
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != entry["sha256"]:
                issues.append(f"FAIL P1 freshness: {rel} changed after its freshness record")
    return issues


def check_manual_gate_report(path: Path) -> list[str]:
    if not path.exists():
        return [f"FAIL P0 manual_gate: missing {path}"]
    text = read_text(path)
    issues: list[str] = []
    if not re.search(r"(?m)^## Narrative Movement\s*$", text):
        issues.append(f"FAIL P1 manual_gate: missing Narrative Movement section in {path}")
    if not re.search(r"(?m)^## Repetition and Novelty Audit\s*$", text):
        issues.append(f"FAIL P1 manual_gate: missing Repetition and Novelty Audit section in {path}")
    repetition_ids = sorted(set(re.findall(r"\bREP-[0-9a-f]{12}\b", section_body(text, "Deterministic Results") or "")))
    for repetition_id in repetition_ids:
        resolution = re.search(
            rf"(?mi)^\s*-\s*\[x\]\s*{re.escape(repetition_id)}:\s*"
            r"(intentional_echo|term_or_name|motif|necessary_reminder|needs_revision)\s*[—-]\s*\S.+$",
            text,
        )
        if not resolution:
            issues.append(
                f"FAIL P1 manual_gate: {repetition_id} lacks a checked classification and reason in {path}"
            )
    unchecked = re.findall(r"(?m)^\s*-\s*\[\s\]\s+(.+)$", text)
    if unchecked:
        issues.append(f"FAIL P1 manual_gate: {len(unchecked)} unchecked review items remain in {path}")
    return issues


def chapter_block(text: str, chapter: int) -> str:
    match = re.search(rf"(?ms)^\s*(?:-\s*)?chapter:\s*{chapter}\b.*?(?=^\s*(?:-\s*)?chapter:\s*\d+\b|\Z)", text)
    return match.group(0) if match else ""


def check_time_indices(project: Path, chapter: int, chapter_text: str, strict: bool = False) -> list[str]:
    issues: list[str] = []
    severity = "FAIL P1" if strict else "WARN P2"
    relative_used = [term for term in RELATIVE_TIME_PATTERNS if term in chapter_text]
    scene_clock = project / "08_memory" / "scene_clock.yaml"
    timeline = project / "04_story" / "timeline.yaml"

    scene_block = read_text(scene_clock) if scene_clock.exists() else ""
    timeline_text = read_text(timeline) if timeline.exists() else ""
    scene_chapter = chapter_block(scene_block, chapter)
    timeline_chapter = chapter_block(timeline_text, chapter)

    if scene_clock.exists() and "time_baseline:" not in scene_block:
        issues.append(f"WARN P2 scene_clock: missing time_baseline in {scene_clock}")
    if timeline.exists() and "time_baseline:" not in timeline_text:
        issues.append(f"WARN P2 timeline: missing time_baseline in {timeline}")

    if scene_clock.exists():
        if not scene_chapter:
            issues.append(f"{severity} scene_clock: no chapter {chapter:04d} entry in {scene_clock}")
        else:
            for field in ["day_index_open", "night_index_open", "day_index_close", "night_index_close"]:
                if not re.search(rf"^\s*{field}:\s*-?\d+\b", scene_chapter, flags=re.MULTILINE):
                    issues.append(f"{severity} scene_clock: chapter {chapter:04d} missing numeric {field}")

    if timeline.exists() and relative_used:
        if not timeline_chapter:
            issues.append(f"{severity} relative_time: chapter uses {', '.join(relative_used[:6])} but has no timeline entry")
        else:
            for field in ["day_index", "night_index"]:
                if not re.search(rf"^\s*{field}:\s*-?\d+\b", timeline_chapter, flags=re.MULTILINE):
                    issues.append(
                        f"{severity} relative_time: chapter uses {', '.join(relative_used[:6])} "
                        f"but timeline chapter entry lacks numeric {field}"
                    )
    return issues


def report_markdown(project: Path, chapter: int, stage: str, issues: list[str]) -> str:
    chapter_id = f"{chapter:04d}"
    status = "PASS" if not issues else ("FAIL" if any(item.startswith("FAIL") for item in issues) else "WARN")
    now = dt.datetime.now().isoformat(timespec="seconds")
    issue_lines = "\n".join(f"- {issue}" for issue in issues) if issues else "- PASS"
    repetition_ids = sorted(set(re.findall(r"\bREP-[0-9a-f]{12}\b", "\n".join(issues))))
    repetition_resolutions = "\n".join(
        f"- [ ] {item}: <classification> — <reason and action>" for item in repetition_ids
    ) or "- [ ] No unresolved verbatim-reuse candidate remains."
    return f"""# Gate Report · Chapter {chapter_id}

- Project: `{project}`
- Generated: `{now}`
- Stage: `{stage}`
- Deterministic status: `{status}`

## Deterministic Results

{issue_lines}

## Time Handoff

- [ ] Previous chapter ending time/location checked against this chapter opening.
- [ ] `scene_clock.yaml` day/night indices checked.
- [ ] Relative time expressions derive from the project time baseline.

## Information Chain

- [ ] Each new fact has a source channel.
- [ ] Reports, messages, witness statements, records, sensory traces, and institutional access stay within carrier limits.
- [ ] No prior seal, promise, concealment, or authority limit is broken without explanation.

## Canon Consistency

- [ ] New labels have antecedents or local explanation.
- [ ] Capabilities/tools/procedures do not erase earlier problems without a limit.
- [ ] Counts match objects, days, people, clues, steps, or listed members.
- [ ] Character knowledge does not include unspoken interior inference.
- [ ] Terminology and identity markers do not drift or collide.

## Narrative Movement

- [ ] Scene outcomes cause or constrain later action.
- [ ] Important choices preserve character agency and carry an appropriate cost.
- [ ] Reader promises are prepared, advanced, paid off, or intentionally delayed.
- [ ] Intentional low-agency, quiet, or anticlimactic movement is documented.

## Repetition and Novelty Audit

- [ ] No prior conclusion, exposition block, deduction, or reminder is repeated without a new consequence.
- [ ] Repeated scene structures, reaction beats, gestures, and hooks have been differentiated or justified.
- [ ] Every necessary reminder immediately enables a new decision, conflict, inference, or emotional turn.
- [ ] Every substantial scene adds information, changes interpretation, forces a choice, imposes a cost, or changes state.

Resolve each deterministic candidate with exactly one classification:
`intentional_echo | term_or_name | motif | necessary_reminder | needs_revision`.

{repetition_resolutions}

## Sync Status

- [ ] Detailed summary updated.
- [ ] Short summary updated.
- [ ] Character states updated.
- [ ] Timeline updated.
- [ ] Information ledger updated.
- [ ] Scene clock updated.
- [ ] Project status updated only after the above files are current.

## Remaining Blocking Risks

- [ ] None, or documented with repair plan.
"""


def write_report(
    project: Path,
    chapter: int,
    stage: str,
    issues: list[str],
    report_path: Path | None,
    preserve_manual: bool = False,
) -> Path:
    if report_path is None:
        report_path = project / "10_review" / f"gate_chapter_{chapter:04d}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    generated = report_markdown(project, chapter, stage, issues)
    if preserve_manual and report_path.exists():
        existing = read_text(report_path)
        marker = "## Time Handoff"
        if marker in existing and marker in generated:
            generated = generated.split(marker, 1)[0] + marker + existing.split(marker, 1)[1]
    report_path.write_text(generated, encoding="utf-8")
    return report_path


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Check a novel chapter for deterministic continuity and prose guardrails.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--stage", choices=["pre", "draft", "post", "accept"], default="post")
    parser.add_argument("--ngram-size", type=int, default=10)
    parser.add_argument("--no-report", action="store_true", help="Do not write 10_review/gate_chapter_####.md")
    parser.add_argument("--report-path", type=Path, help="Custom report output path")
    args = parser.parse_args()

    project = args.project.resolve()
    chapter_id = f"{args.chapter:04d}"
    if args.chapter < 1 or args.ngram_size < 6:
        parser.error("chapter must be positive and ngram-size must be at least 6")
    pre_path = project / "10_review" / f"continuity_pre_chapter_{chapter_id}.md"
    if args.stage == "pre":
        issues = check_gate_file(pre_path, DEFAULT_REQUIRED_PRE_SECTIONS, "pre_gate")
        if not args.no_report:
            print(f"REPORT {write_report(project, args.chapter, args.stage, issues, args.report_path)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    chapter_path = project / "06_chapters" / f"chapter_{chapter_id}.md"
    if not chapter_path.exists():
        print(f"FAIL P0 chapter: missing {chapter_path}")
        if not args.no_report:
            report = write_report(project, args.chapter, args.stage, [f"FAIL P0 chapter: missing {chapter_path}"], args.report_path)
            print(f"REPORT {report}")
        return 1

    text = read_text(chapter_path)
    forbidden = parse_markdown_terms(project / "09_writing" / "forbidden_patterns.md")
    hard_forbidden, whitelist = parse_guardrails(project / "09_writing" / "term_guardrails.yaml")
    issues: list[str] = []
    issues.extend(check_gate_file(pre_path, DEFAULT_REQUIRED_PRE_SECTIONS, "pre_gate"))
    post_path = project / "10_review" / f"continuity_post_chapter_{chapter_id}.md"
    if args.stage in {"post", "accept"}:
        issues.extend(check_gate_file(post_path, DEFAULT_REQUIRED_POST_SECTIONS, "post_gate"))
    issues.extend(check_required_outputs(project, args.chapter, args.stage))
    issues.extend(check_time_indices(project, args.chapter, text, strict=args.stage in {"post", "accept"}))
    issues.extend(check_forbidden_terms(chapter_path, text, forbidden, whitelist))
    issues.extend(check_forbidden_terms(chapter_path, text, hard_forbidden, whitelist, severity="FAIL P1"))
    issues.extend(sentence_repetitions(chapter_path, text))
    try:
        issues.extend(
            repetition_gate_issue(item)
            for item in scan_chapter_repetition(project, args.chapter, seed_size=args.ngram_size)
        )
    except ValueError as exc:
        issues.append(f"FAIL P1 repetition_scan: {exc}")
    if args.stage == "accept":
        issues.extend(check_freshness(project, args.chapter))
        manual_report = args.report_path or project / "10_review" / f"gate_chapter_{chapter_id}.md"
        issues.extend(check_manual_gate_report(manual_report))

    if not args.no_report:
        report = write_report(
            project, args.chapter, args.stage, issues, args.report_path,
            preserve_manual=args.stage == "accept",
        )
        print(f"REPORT {report}")

    if not issues:
        print("PASS")
        return 0
    for issue in issues:
        print(issue)
    return 1 if any(issue.startswith("FAIL") for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
