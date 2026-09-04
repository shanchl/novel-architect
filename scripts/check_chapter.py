#!/usr/bin/env python3
"""Run deterministic chapter checks for a novel-architect project.

The script intentionally uses only the Python standard library. It is a guardrail,
not a replacement for human continuity review.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


DEFAULT_REQUIRED_PRE_SECTIONS = [
    "Time Handoff",
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


def check_gate_file(path: Path, sections: list[str], label: str) -> list[str]:
    if not path.exists():
        return [f"FAIL P0 {label}: missing {path}"]
    text = read_text(path)
    failures = []
    for section in sections:
        if not section_present(text, section):
            failures.append(f"FAIL P1 {label}: missing section '{section}' in {path}")
    if re.search(r"##+\s+Blocking Risks\s*\n\s*(?:$|##)", text, flags=re.IGNORECASE):
        failures.append(f"WARN P2 {label}: Blocking Risks section is empty in {path}")
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
            issues.append(f"WARN P2 repeated_sentence: {count}x in {chapter_path}: {sentence[:40]}")
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
            sample = " / ".join(filtered[:5])
            issues.append(f"WARN P2 cross_chapter_ngram: chapter {chapter:04d} overlaps {other.name}: {sample}")
    return issues


def check_required_outputs(project: Path, chapter: int) -> list[str]:
    chapter_id = f"{chapter:04d}"
    required = [
        project / "06_chapters" / f"chapter_{chapter_id}.md",
        project / "07_summaries" / f"chapter_{chapter_id}_summary.md",
        project / "07_summaries" / f"chapter_{chapter_id}_short.md",
        project / "04_story" / "timeline.yaml",
        project / "00_project" / "status.yaml",
    ]
    issues = []
    for path in required:
        if not path.exists():
            issues.append(f"FAIL P0 required_output: missing {path}")
    return issues


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Check a novel chapter for deterministic continuity and prose guardrails.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--ngram-size", type=int, default=6)
    args = parser.parse_args()

    project = args.project.resolve()
    chapter_id = f"{args.chapter:04d}"
    chapter_path = project / "06_chapters" / f"chapter_{chapter_id}.md"
    if not chapter_path.exists():
        print(f"FAIL P0 chapter: missing {chapter_path}")
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
    issues.extend(check_forbidden_terms(chapter_path, text, forbidden, whitelist))
    issues.extend(sentence_repetitions(chapter_path, text))
    issues.extend(cross_chapter_repetition(project, args.chapter, text, args.ngram_size, allowed_repetitions))

    if not issues:
        print("PASS")
        return 0
    for issue in issues:
        print(issue)
    return 1 if any(issue.startswith("FAIL") for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
