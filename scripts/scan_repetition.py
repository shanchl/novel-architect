#!/usr/bin/env python3
"""Find review-worthy verbatim reuse across novel chapters.

The scanner is deliberately a triage tool. It restores matches to original
source locations and uses occurrence-scoped approvals; it does not decide
whether an echo is artistically justified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


CHAPTER_RE = re.compile(r"chapter_(\d{4})\.md$")
MEANINGFUL_RE = re.compile(r"[0-9A-Za-z\u3400-\u9fff]")
VALID_CATEGORIES = {"intentional_echo", "term_or_name", "motif", "necessary_reminder"}
BOUNDARY_PUNCTUATION = "，。！？!?、；：‘’“”\"'《》〈〉（）()【】[]…—-_*#~`"


@dataclass(frozen=True)
class NormalizedText:
    raw: str
    text: str
    offsets: tuple[int, ...]

    def raw_bounds(self, start: int, end: int) -> tuple[int, int]:
        if start >= end or not self.offsets:
            return 0, 0
        return self.offsets[start], self.offsets[end - 1] + 1


@dataclass(frozen=True)
class Block:
    current_start: int
    current_end: int
    other_start: int
    other_end: int
    exact_chars: int


@dataclass
class Match:
    id: str
    severity: str
    current_chapter: int
    current_line: int
    other_chapter: int
    other_line: int
    length: int
    similarity: float
    occurrence_chapters: list[int]
    text: str
    current_context: str
    other_context: str
    approved: bool = False
    approval_id: str = ""
    approval_category: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalize(raw: str) -> NormalizedText:
    chars: list[str] = []
    offsets: list[int] = []
    for index, char in enumerate(raw):
        if char.isspace():
            continue
        chars.append(char)
        offsets.append(index)
    return NormalizedText(raw=raw, text="".join(chars), offsets=tuple(offsets))


def chapter_number(path: Path) -> int | None:
    match = CHAPTER_RE.search(path.name)
    return int(match.group(1)) if match else None


def load_chapters(project: Path) -> dict[int, NormalizedText]:
    result: dict[int, NormalizedText] = {}
    for path in sorted((project / "06_chapters").glob("chapter_*.md")):
        number = chapter_number(path)
        if number is not None:
            result[number] = normalize(read_text(path))
    return result


def meaningful(fragment: str) -> bool:
    count = len(MEANINGFUL_RE.findall(fragment))
    return count >= 4 and count * 2 >= len(fragment)


def canonical_fragment(fragment: str) -> str:
    return normalize(fragment).text.strip(BOUNDARY_PUNCTUATION)


def seed_positions(text: str, size: int, occurrence_cap: int = 24) -> dict[str, list[int]]:
    positions: dict[str, list[int]] = {}
    for index in range(max(0, len(text) - size + 1)):
        seed = text[index:index + size]
        if not meaningful(seed):
            continue
        bucket = positions.setdefault(seed, [])
        if len(bucket) <= occurrence_cap:
            bucket.append(index)
    return {seed: items for seed, items in positions.items() if len(items) <= occurrence_cap}


def extend_exact(a: str, b: str, a_pos: int, b_pos: int, seed_size: int) -> Block:
    left = 0
    while a_pos - left > 0 and b_pos - left > 0 and a[a_pos - left - 1] == b[b_pos - left - 1]:
        left += 1
    right = seed_size
    while a_pos + right < len(a) and b_pos + right < len(b) and a[a_pos + right] == b[b_pos + right]:
        right += 1
    return Block(a_pos - left, a_pos + right, b_pos - left, b_pos + right, left + right)


def remove_contained(blocks: set[Block]) -> list[Block]:
    ordered = sorted(
        blocks,
        key=lambda item: (-(item.current_end - item.current_start), item.current_start, item.other_start),
    )
    kept: list[Block] = []
    for block in ordered:
        if any(
            prior.current_start <= block.current_start
            and prior.current_end >= block.current_end
            and prior.other_start <= block.other_start
            and prior.other_end >= block.other_end
            for prior in kept
        ):
            continue
        kept.append(block)
    return kept


def merge_nearby(blocks: list[Block], max_gap: int) -> list[Block]:
    pending = sorted(blocks, key=lambda item: (item.current_start, item.other_start))
    merged: list[Block] = []
    for block in pending:
        choices: list[tuple[int, int]] = []
        for index, prior in enumerate(merged):
            current_gap = block.current_start - prior.current_end
            other_gap = block.other_start - prior.other_end
            if 0 <= current_gap <= max_gap and 0 <= other_gap <= max_gap:
                choices.append((current_gap + other_gap, index))
        if not choices:
            merged.append(block)
            continue
        _, index = min(choices)
        prior = merged[index]
        merged[index] = Block(
            prior.current_start,
            block.current_end,
            prior.other_start,
            block.other_end,
            prior.exact_chars + block.exact_chars,
        )
    return remove_contained(set(merged))


def matching_blocks(current: str, other: str, seed_size: int, merge_gap: int) -> list[Block]:
    current_index = seed_positions(current, seed_size)
    other_index = seed_positions(other, seed_size)
    blocks: set[Block] = set()
    for seed in current_index.keys() & other_index.keys():
        for current_pos in current_index[seed]:
            for other_pos in other_index[seed]:
                blocks.add(extend_exact(current, other, current_pos, other_pos, seed_size))
    return merge_nearby(remove_contained(blocks), merge_gap)


def line_number(raw: str, index: int) -> int:
    return raw.count("\n", 0, index) + 1


def compact_context(raw: str, start: int, end: int, padding: int = 36) -> str:
    value = raw[max(0, start - padding):min(len(raw), end + padding)]
    return re.sub(r"\s+", " ", value).strip()


def load_registry(project: Path) -> list[dict]:
    path = project / "09_writing" / "repetition_registry.json"
    if not path.exists():
        return []
    try:
        data = json.loads(read_text(path))
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid repetition registry {path}: {exc}") from exc
    entries = data.get("entries", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        raise ValueError(f"invalid repetition registry {path}: entries must be a list")
    return [entry for entry in entries if isinstance(entry, dict)]


def approval_for(text: str, chapter_a: int, chapter_b: int, entries: list[dict]) -> tuple[str, str]:
    pair = {chapter_a, chapter_b}
    for entry in entries:
        category = str(entry.get("category", ""))
        chapters = entry.get("chapters", entry.get("approved_occurrences", []))
        approved_text = canonical_fragment(str(entry.get("text", "")))
        if category not in VALID_CATEGORIES or not approved_text or not isinstance(chapters, list):
            continue
        try:
            approved_chapters = {int(item) for item in chapters}
        except (TypeError, ValueError):
            continue
        # A registry entry can cover a smaller reported fragment, but it must not
        # hide a larger repeated passage which merely contains an approved motif.
        if pair <= approved_chapters and text in approved_text:
            return str(entry.get("id", "")), category
    return "", ""


def scan_chapter(
    project: Path,
    chapter: int,
    *,
    against: str = "all",
    seed_size: int = 10,
    review_length: int = 14,
    high_length: int = 24,
    merge_gap: int = 4,
    include_approved: bool = False,
    chapters: dict[int, NormalizedText] | None = None,
) -> list[Match]:
    if seed_size < 6 or review_length < seed_size or high_length < review_length:
        raise ValueError("require 6 <= seed_size <= review_length <= high_length")
    corpus = chapters or load_chapters(project)
    if chapter not in corpus:
        raise ValueError(f"missing chapter_{chapter:04d}.md")
    registry = load_registry(project)
    current = corpus[chapter]
    results: list[Match] = []
    for other_chapter, other in sorted(corpus.items()):
        if other_chapter == chapter or (against == "previous" and other_chapter > chapter):
            continue
        for block in matching_blocks(current.text, other.text, seed_size, merge_gap):
            length = block.current_end - block.current_start
            old_span = block.other_end - block.other_start
            similarity = block.exact_chars / max(length, old_span)
            fragment = current.text[block.current_start:block.current_end]
            canonical = canonical_fragment(fragment)
            length = len(canonical)
            if length < seed_size or not meaningful(canonical):
                continue
            occurrence_chapters = sorted(number for number, item in corpus.items() if canonical in item.text)
            nearby = abs(chapter - other_chapter) <= 1
            if length < review_length and not nearby and len(occurrence_chapters) < 3:
                continue
            current_start, current_end = current.raw_bounds(block.current_start, block.current_end)
            other_start, other_end = other.raw_bounds(block.other_start, block.other_end)
            approval_id, approval_category = (
                approval_for(canonical, chapter, other_chapter, registry)
                if similarity == 1.0 else ("", "")
            )
            approved = bool(approval_id or approval_category)
            if approved and not include_approved:
                continue
            match_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
            results.append(Match(
                id=f"REP-{match_id}",
                severity="P1" if length >= high_length else "P2",
                current_chapter=chapter,
                current_line=line_number(current.raw, current_start),
                other_chapter=other_chapter,
                other_line=line_number(other.raw, other_start),
                length=length,
                similarity=round(similarity, 3),
                occurrence_chapters=occurrence_chapters,
                text=current.raw[current_start:current_end],
                current_context=compact_context(current.raw, current_start, current_end),
                other_context=compact_context(other.raw, other_start, other_end),
                approved=approved,
                approval_id=approval_id,
                approval_category=approval_category,
            ))
    unique: dict[tuple[int, int, str], Match] = {}
    for item in results:
        key = (item.current_chapter, item.other_chapter, canonical_fragment(item.text))
        prior = unique.get(key)
        if prior is None or item.length > prior.length:
            unique[key] = item
    return sorted(unique.values(), key=lambda item: (-item.length, item.other_chapter, item.current_line))


def gate_issue(item: Match) -> str:
    sample = re.sub(r"\s+", " ", item.text).strip()
    if len(sample) > 80:
        sample = sample[:77] + "..."
    return (
        f"WARN {item.severity} cross_chapter_reuse: {item.id} "
        f"ch{item.current_chapter:04d}:{item.current_line} <-> ch{item.other_chapter:04d}:{item.other_line}; "
        f"{item.length} chars, similarity={item.similarity:.2f}; "
        "classify as intentional_echo|term_or_name|motif|necessary_reminder|needs_revision; "
        f"text='{sample}'"
    )


def markdown_report(project: Path, matches: list[Match], scope: str) -> str:
    lines = [
        "# Cross-Chapter Repetition Scan",
        "",
        f"- Project: `{project}`",
        f"- Scope: `{scope}`",
        f"- Findings: `{len(matches)}`",
        "- Meaning: candidates for review, not automatic prose defects",
        "",
    ]
    if not matches:
        lines.append("PASS — no review-worthy verbatim reuse found.")
        return "\n".join(lines) + "\n"
    for item in matches:
        lines.extend([
            f"## {item.id} · {item.severity} · {item.length} chars",
            "",
            f"- Locations: `ch{item.current_chapter:04d}:{item.current_line}` ↔ `ch{item.other_chapter:04d}:{item.other_line}`",
            f"- Similarity: `{item.similarity:.2f}`",
            f"- Occurs in chapters: `{', '.join(f'{n:04d}' for n in item.occurrence_chapters)}`",
            f"- Approval: `{item.approval_category or 'unresolved'}` `{item.approval_id}`".rstrip(),
            "- Classification required: `intentional_echo | term_or_name | motif | necessary_reminder | needs_revision`",
            "",
            f"> Current: {item.current_context}",
            "",
            f"> Other: {item.other_context}",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Scan novel chapters for review-worthy verbatim reuse.")
    parser.add_argument("project", type=Path)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--chapter", type=int)
    target.add_argument("--all", action="store_true", dest="scan_all")
    parser.add_argument("--against", choices=["all", "previous"], default="all")
    parser.add_argument("--seed-length", type=int, default=10)
    parser.add_argument("--review-length", type=int, default=14)
    parser.add_argument("--high-length", type=int, default=24)
    parser.add_argument("--merge-gap", type=int, default=4)
    parser.add_argument("--include-approved", action="store_true")
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    chapters = load_chapters(project)
    try:
        if args.scan_all:
            matches: list[Match] = []
            for number in sorted(chapters):
                matches.extend(scan_chapter(
                    project, number, against="previous", seed_size=args.seed_length,
                    review_length=args.review_length, high_length=args.high_length,
                    merge_gap=args.merge_gap, include_approved=args.include_approved, chapters=chapters,
                ))
            scope = "all chapters, each pair once"
        else:
            matches = scan_chapter(
                project, args.chapter, against=args.against, seed_size=args.seed_length,
                review_length=args.review_length, high_length=args.high_length,
                merge_gap=args.merge_gap, include_approved=args.include_approved, chapters=chapters,
            )
            scope = f"chapter {args.chapter:04d} against {args.against}"
    except ValueError as exc:
        parser.error(str(exc))

    omitted = max(0, len(matches) - args.max_results)
    matches = matches[:args.max_results]
    if args.format == "json":
        output = json.dumps(
            {"project": str(project), "scope": scope, "findings": [asdict(item) for item in matches], "omitted": omitted},
            ensure_ascii=False, indent=2,
        ) + "\n"
    elif args.format == "markdown":
        output = markdown_report(project, matches, scope)
        if omitted:
            output += f"\n> {omitted} additional findings omitted by --max-results.\n"
    else:
        lines = [gate_issue(item) for item in matches]
        if omitted:
            lines.append(f"WARN P2 repetition_scan_truncated: {omitted} additional findings omitted")
        output = "\n".join(lines) + ("\n" if lines else "PASS\n")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"REPORT {args.output.resolve()}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
