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


def section_empty(text: str, section: str) -> bool:
    aliases = SECTION_ALIASES.get(section, [section])
    for alias in aliases:
        pattern = rf"^##+\s+[^\n]*{re.escape(alias)}[^\n]*\n(?P<body>.*?)(?=^##+\s+|\Z)"
        match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if match:
            body = re.sub(r"<!--.*?-->", "", match.group("body"), flags=re.DOTALL).strip()
            return not body
    return False


def check_gate_file(path: Path, sections: list[str], label: str) -> list[str]:
    if not path.exists():
        return [f"FAIL P0 {label}: missing {path}"]
    text = read_text(path)
    failures = []
    for section in sections:
        if not section_present(text, section):
            failures.append(f"FAIL P1 {label}: missing section '{section}' in {path}")
    for section in ["Time Handoff", "Information Chain", "Blocking Risks"]:
        if section_present(text, section) and section_empty(text, section):
            failures.append(f"WARN P2 {label}: section '{section}' is empty in {path}")
    return failures


def check_forbidden_terms(chapter_path: Path, text: str, terms: list[str], whitelist: list[str]) -> list[str]:
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
            issues.append(f"FAIL P1 forbidden_term: found '{term}' at {chapter_path}:{line}")
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


def char_ngrams(text: str, size: int) -> set[str]:
    normalized = re.sub(r"\s+", "", text)
    return {normalized[i:i + size] for i in range(max(0, len(normalized) - size + 1))}


def cross_chapter_repetition(project: Path, chapter: int, current_text: str, size: int, allowed: list[str]) -> list[str]:
    chapter_dir = project / "06_chapters"
    current = char_ngrams(current_text, size)
    issues: list[str] = []
    for other in sorted(chapter_dir.glob("chapter_*.md")):
        match = re.search(r"chapter_(\d{4})\.md$", other.name)
        if not match:
            continue
        other_chapter = int(match.group(1))
        if other_chapter == chapter:
            continue
        if abs(other_chapter - chapter) > 5:
            continue
        overlap = sorted(current & char_ngrams(read_text(other), size))
        filtered = [
            item for item in overlap
            if not re.fullmatch(r"[，。！？、“”《》：；（）…—0-9a-zA-Z]+", item)
            and not any(allowed_item in item or item in allowed_item for allowed_item in allowed)
        ]
        if filtered:
            sample = " / ".join(filtered[:8])
            issues.append(
                f"WARN P2 cross_chapter_ngram: chapter {chapter:04d} overlaps {other.name}; "
                f"classify as intentional_echo|term_or_name|motif|necessary_reminder|needs_revision: {sample}"
            )
    return issues


def check_required_outputs(project: Path, chapter: int) -> list[str]:
    chapter_id = f"{chapter:04d}"
    required = [
        project / "06_chapters" / f"chapter_{chapter_id}.md",
        project / "07_summaries" / f"chapter_{chapter_id}_summary.md",
        project / "07_summaries" / f"chapter_{chapter_id}_short.md",
        project / "04_story" / "timeline.yaml",
        project / "08_memory" / "scene_clock.yaml",
        project / "08_memory" / "information_ledger.yaml",
        project / "00_project" / "status.yaml",
    ]
    issues = []
    for path in required:
        if not path.exists():
            issues.append(f"FAIL P0 required_output: missing {path}")
    return issues


def chapter_block(text: str, chapter: int) -> str:
    match = re.search(rf"(?ms)^(\s*-\s*)?chapter:\s*{chapter}\b.*?(?=^\s*-\s*chapter:\s*\d+\b|\Z)", text)
    return match.group(0) if match else ""


def check_time_indices(project: Path, chapter: int, chapter_text: str) -> list[str]:
    issues: list[str] = []
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
            issues.append(f"WARN P2 scene_clock: no chapter {chapter:04d} entry in {scene_clock}")
        else:
            for field in ["day_index_open", "night_index_open", "day_index_close", "night_index_close"]:
                if not re.search(rf"^\s*{field}:\s*-?\d+\b", scene_chapter, flags=re.MULTILINE):
                    issues.append(f"WARN P2 scene_clock: chapter {chapter:04d} missing numeric {field}")

    if timeline.exists() and relative_used:
        if not timeline_chapter:
            issues.append(
                f"WARN P2 relative_time: chapter uses {', '.join(relative_used[:6])} but has no timeline entry"
            )
        else:
            for field in ["day_index", "night_index"]:
                if not re.search(rf"^\s*{field}:\s*-?\d+\b", timeline_chapter, flags=re.MULTILINE):
                    issues.append(
                        f"WARN P2 relative_time: chapter uses {', '.join(relative_used[:6])} "
                        f"but timeline chapter entry lacks numeric {field}"
                    )
    return issues


def report_markdown(project: Path, chapter: int, issues: list[str]) -> str:
    chapter_id = f"{chapter:04d}"
    status = "PASS" if not issues else ("FAIL" if any(item.startswith("FAIL") for item in issues) else "WARN")
    now = dt.datetime.now().isoformat(timespec="seconds")
    issue_lines = "\n".join(f"- {issue}" for issue in issues) if issues else "- PASS"
    return f"""# Gate Report · Chapter {chapter_id}

- Project: `{project}`
- Generated: `{now}`
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

## Repetition Triage

Classify every repeated sentence or n-gram warning as one of:

- `intentional_echo`
- `term_or_name`
- `motif`
- `necessary_reminder`
- `needs_revision`

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


def write_report(project: Path, chapter: int, issues: list[str], report_path: Path | None) -> Path:
    if report_path is None:
        report_path = project / "10_review" / f"gate_chapter_{chapter:04d}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_markdown(project, chapter, issues), encoding="utf-8")
    return report_path


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Check a novel chapter for deterministic continuity and prose guardrails.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--ngram-size", type=int, default=6)
    parser.add_argument("--no-report", action="store_true", help="Do not write 10_review/gate_chapter_####.md")
    parser.add_argument("--report-path", type=Path, help="Custom report output path")
    args = parser.parse_args()

    project = args.project.resolve()
    chapter_id = f"{args.chapter:04d}"
    chapter_path = project / "06_chapters" / f"chapter_{chapter_id}.md"
    if not chapter_path.exists():
        print(f"FAIL P0 chapter: missing {chapter_path}")
        if not args.no_report:
            report = write_report(project, args.chapter, [f"FAIL P0 chapter: missing {chapter_path}"], args.report_path)
            print(f"REPORT {report}")
        return 1

    text = read_text(chapter_path)
    forbidden = parse_markdown_terms(project / "09_writing" / "forbidden_patterns.md")
    extra_forbidden, whitelist = parse_guardrails(project / "09_writing" / "term_guardrails.yaml")
    forbidden.extend(extra_forbidden)
    allowed_repetitions = parse_markdown_terms(project / "09_writing" / "repetition_watchlist.md")

    issues: list[str] = []
    issues.extend(check_gate_file(project / "10_review" / f"continuity_pre_chapter_{chapter_id}.md", DEFAULT_REQUIRED_PRE_SECTIONS, "pre_gate"))
    post_path = project / "10_review" / f"continuity_post_chapter_{chapter_id}.md"
    if post_path.exists():
        issues.extend(check_gate_file(post_path, DEFAULT_REQUIRED_POST_SECTIONS, "post_gate"))
    else:
        issues.append(f"WARN P2 post_gate: missing {post_path}")
    issues.extend(check_required_outputs(project, args.chapter))
    issues.extend(check_time_indices(project, args.chapter, text))
    issues.extend(check_forbidden_terms(chapter_path, text, forbidden, whitelist))
    issues.extend(sentence_repetitions(chapter_path, text))
    issues.extend(cross_chapter_repetition(project, args.chapter, text, args.ngram_size, allowed_repetitions))

    if not args.no_report:
        report = write_report(project, args.chapter, issues, args.report_path)
        print(f"REPORT {report}")

    if not issues:
        print("PASS")
        return 0
    for issue in issues:
        print(issue)
    return 1 if any(issue.startswith("FAIL") for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
