#!/usr/bin/env python3
"""Build a relevance-bounded context pack for a novel chapter task."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


DEFAULT_MAX_CHARS = 120_000
DEFAULT_RECENT_SUMMARIES = 5


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clip_complete_lines(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    cut = text.rfind("\n", 0, max(1, limit))
    if cut < 1:
        cut = limit
    return text[:cut] + f"\n\n_[Truncated at {cut} characters on a line boundary.]_\n", True


class PackBuilder:
    def __init__(self, project: Path, chapter: int, max_chars: int) -> None:
        self.project = project
        self.chapter = chapter
        self.max_chars = max_chars
        self.parts: list[str] = []
        self.sources: list[str] = []
        self.missing: list[str] = []
        self.truncated: list[str] = []

    @property
    def remaining(self) -> int:
        return self.max_chars - sum(len(part) for part in self.parts)

    def add_text(self, title: str, body: str, source: str, per_section_limit: int = 12_000) -> None:
        available = min(per_section_limit, max(0, self.remaining - len(title) - 100))
        if available < 200:
            self.truncated.append(f"{source} (omitted: context budget exhausted)")
            return
        clipped, was_truncated = clip_complete_lines(body.strip(), available)
        self.parts.append(f"\n## {title}\n\n{clipped.strip()}\n")
        self.sources.append(source)
        if was_truncated:
            self.truncated.append(source)

    def add_file(self, title: str, path: Path, per_section_limit: int = 12_000) -> None:
        rel = path.relative_to(self.project).as_posix()
        if not path.exists():
            self.missing.append(rel)
            return
        self.add_text(title, read_text(path), rel, per_section_limit)

    def render(self) -> str:
        header = [
            "# Context Pack · Chapter %04d" % self.chapter,
            "",
            f"- Project: `{self.project}`",
            f"- Generated: `{dt.datetime.now().isoformat(timespec='seconds')}`",
            f"- Character budget: `{self.max_chars}`",
            "- Canon status: generated working context; source project files remain authoritative.",
        ]
        body = "\n".join(header) + "\n" + "\n".join(self.parts)
        audit = ["\n## Context Audit\n", "### Included Sources", *[f"- `{item}`" for item in self.sources]]
        audit.extend(["\n### Missing Sources", *([f"- `{item}`" for item in self.missing] or ["- None"])])
        audit.extend(["\n### Truncated or Omitted", *([f"- `{item}`" for item in self.truncated] or ["- None"])])
        audit.extend([
            "\n### Use Notes",
            "- Resolve blocking continuity questions against source files before drafting.",
            "- Do not edit this pack as canon; update source files or a chapter delta.",
        ])
        return body.rstrip() + "\n" + "\n".join(audit).rstrip() + "\n"


def scalar(text: str, key: str, default: str = "") -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*[\"']?([^\n\"']+)", text)
    return match.group(1).strip() if match else default


def query_terms(plan_text: str, explicit: list[str]) -> list[str]:
    terms = {item.strip().lower() for item in explicit if len(item.strip()) >= 2}
    for item in re.findall(r"[\"']([^\"']{2,40})[\"']", plan_text):
        terms.add(item.strip().lower())
    for item in re.findall(r"\b(?:PL|FS|IF|ARC|RP)-\d+\b", plan_text, flags=re.IGNORECASE):
        terms.add(item.lower())
    for match in re.finditer(r"(?m)^[ \t]*(?:characters|involved_characters|pov):[ \t]*([^\n]*)$", plan_text):
        for item in re.split(r"[,\[\]]", match.group(1)):
            value = item.strip().strip("\"'")
            if len(value) >= 2:
                terms.add(value.lower())
    for match in re.finditer(
        r"(?ms)^[ \t]*(?:characters|involved_characters):[ \t]*\n(?P<body>(?:[ \t]+-[ \t]+[^\n]+\n?)+)",
        plan_text,
    ):
        for item in re.findall(r"(?m)^\s+-\s+([^\n]+)", match.group("body")):
            value = item.strip().strip("\"'")
            if len(value) >= 2:
                terms.add(value.lower())
    return sorted(terms)


def recent_summary_paths(project: Path, chapter: int, count: int) -> list[Path]:
    candidates: list[tuple[int, Path]] = []
    for path in (project / "07_summaries").glob("chapter_*_short.md"):
        match = re.fullmatch(r"chapter_(\d{4})_short\.md", path.name)
        if match and int(match.group(1)) < chapter:
            candidates.append((int(match.group(1)), path))
    return [path for _, path in sorted(candidates)[-count:]]


def previous_chapter_paths(project: Path, chapter: int, count: int) -> list[Path]:
    return [
        path
        for number in range(max(1, chapter - count), chapter)
        if (path := project / "06_chapters" / f"chapter_{number:04d}.md").exists()
    ]


def relevant_state_paths(project: Path, terms: list[str], include_all: bool) -> list[Path]:
    paths = sorted((project / "03_characters" / "states").glob("*.yaml"))
    if include_all:
        return paths
    if not terms:
        return []
    return [path for path in paths if any(term in (path.stem + "\n" + read_text(path)).lower() for term in terms)]


def relevant_yaml(
    path: Path, terms: list[str], chapter: int, max_blocks: int = 12, fallback_last: int = 0
) -> str:
    if not path.exists():
        return ""
    text = read_text(path)
    matches = list(re.finditer(r"(?m)^  - ", text))
    if not matches:
        return text
    header = text[:matches[0].start()].rstrip()
    blocks = [
        text[match.start(): matches[index + 1].start() if index + 1 < len(matches) else len(text)].rstrip()
        for index, match in enumerate(matches)
    ]
    scored: list[tuple[int, int, str]] = []
    for index, block in enumerate(blocks):
        lower = block.lower()
        score = sum(4 for term in terms if term in lower)
        if re.search(r"status:\s*[\"']?(?:active|open|planted|advancing)", lower):
            score += 2
        if re.search(r"completed:\s*false", lower):
            score += 2
        if re.search(rf"(?:chapter|expected_\w+_chapter|planned_\w+_chapters):[^\n]*\b{chapter}\b", lower):
            score += 3
        if score:
            scored.append((score, -index, block))
    chosen = [item[2] for item in sorted(scored, reverse=True)[:max_blocks]]
    if not chosen and fallback_last:
        chosen = blocks[-fallback_last:]
    suffix = "\n" + "\n".join(chosen) if chosen else "\n  # No active or chapter-relevant entries selected."
    return header + suffix


def current_volume_path(project: Path, status_text: str) -> Path:
    volumes = project / "05_structure" / "volumes"
    volume = int(scalar(status_text, "current_volume", "1") or 1)
    default = volumes / f"volume_{volume:03d}.md"
    if default.exists():
        return default
    current_case = int(scalar(status_text, "current_case", str(volume)) or volume)
    case_matches = sorted(volumes.glob(f"case_{current_case:03d}_*.md"))
    if case_matches:
        return case_matches[0]
    markdown_files = sorted(volumes.glob("*.md"))
    return markdown_files[0] if len(markdown_files) == 1 else default


def build_pack(
    project: Path,
    chapter: int,
    characters: list[str],
    previous_full: int,
    recent_summaries: int,
    max_chars: int,
    all_character_states: bool,
) -> str:
    chapter_id = f"{chapter:04d}"
    builder = PackBuilder(project, chapter, max_chars)
    status_path = project / "00_project" / "status.yaml"
    status_text = read_text(status_path) if status_path.exists() else ""
    plan_path = project / "05_structure" / "chapter_plans" / f"chapter_{chapter_id}.yaml"
    plan_text = read_text(plan_path) if plan_path.exists() else ""
    terms = query_terms(plan_text, characters)

    builder.add_file("Project Status", status_path, 4_000)
    series_structure = project / "00_project" / "series_structure.md"
    if series_structure.exists():
        builder.add_file("Project Structure Override", series_structure, 8_000)
    builder.add_file("Chapter Plan", plan_path, 16_000)
    builder.add_file("Creative Contract", project / "01_concept" / "creative_contract.md", 8_000)
    builder.add_file("Core Concept", project / "01_concept" / "core.md", 8_000)
    builder.add_file("Story Engine", project / "04_story" / "story_engine.yaml", 10_000)
    builder.add_file("Hard World Rules", project / "02_world" / "rules.yaml", 10_000)
    builder.add_file("Project-Specific Canon Gates", project / "10_review" / "canon_gates_project.md", 8_000)
    builder.add_file("Writing Style", project / "09_writing" / "style.md", 8_000)
    builder.add_file("Writing Rules", project / "09_writing" / "writing_rules.md", 8_000)
    builder.add_file("Forbidden Patterns", project / "09_writing" / "forbidden_patterns.md", 5_000)
    builder.add_file("Vocabulary", project / "09_writing" / "vocabulary.md", 8_000)
    builder.add_file("Novel-Specific Prompts", project / "09_writing" / "prompts.md", 8_000)
    builder.add_file("POV and Voices", project / "09_writing" / "pov_voices.yaml", 8_000)

    for path in previous_chapter_paths(project, chapter, previous_full):
        builder.add_file(f"Previous Manuscript · {path.stem}", path, 30_000)

    builder.add_file("Novel Bible", project / "08_memory" / "novel_bible.md", 12_000)
    builder.add_file("Permanent Memory", project / "08_memory" / "permanent.md", 10_000)
    builder.add_file("Master Outline", project / "04_story" / "master_outline.md", 10_000)
    builder.add_file("Current Volume or Case", current_volume_path(project, status_text), 10_000)

    summaries = recent_summary_paths(project, chapter, recent_summaries)
    if summaries:
        summary_text = "\n\n".join(f"### {path.name}\n\n{read_text(path).strip()}" for path in summaries)
        builder.add_text("Recent Short Summaries", summary_text, f"latest {len(summaries)} short summaries", 8_000)

    if chapter > 1:
        builder.add_file("Previous Detailed Summary", project / "07_summaries" / f"chapter_{chapter - 1:04d}_summary.md", 12_000)

    states = relevant_state_paths(project, terms, all_character_states)
    if states:
        state_text = "\n\n".join(f"### {path.name}\n\n```yaml\n{read_text(path).strip()}\n```" for path in states)
        builder.add_text("Relevant Character States", state_text, f"{len(states)} selected character state files", 16_000)

    for title, rel in [
        ("Relevant Relationships", "03_characters/relationships.yaml"),
        ("Active Plotlines", "04_story/plotlines.yaml"),
        ("Due Reader Promises", "04_story/reader_promises.yaml"),
        ("Due Foreshadowing", "04_story/foreshadowing.yaml"),
        ("Relevant Character Arcs", "04_story/character_arcs.yaml"),
    ]:
        path = project / rel
        if path.exists():
            builder.add_text(title, relevant_yaml(path, terms, chapter), rel, 10_000)
        else:
            builder.missing.append(rel)

    builder.add_file("Open Threads", project / "08_memory" / "open_threads.md", 8_000)
    for title, rel, relevant_chapter, blocks, limit in [
        ("Information Ledger", "08_memory/information_ledger.yaml", chapter, 12, 12_000),
        ("Scene Clock", "08_memory/scene_clock.yaml", max(1, chapter - 1), 2, 8_000),
        ("Timeline", "04_story/timeline.yaml", max(1, chapter - 1), 8, 12_000),
    ]:
        path = project / rel
        if path.exists():
            builder.add_text(
                title,
                relevant_yaml(path, terms, relevant_chapter, max_blocks=blocks, fallback_last=blocks),
                rel,
                limit,
            )
        else:
            builder.missing.append(rel)

    return builder.render()


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Build a relevance-bounded context pack for a chapter.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=positive_int, required=True)
    parser.add_argument("--characters", nargs="*", default=[], help="Relevant character names or slugs")
    parser.add_argument("--all-character-states", action="store_true", help="Include every character state")
    parser.add_argument("--previous-full", type=positive_int, default=2)
    parser.add_argument("--recent-summaries", type=positive_int, default=DEFAULT_RECENT_SUMMARIES)
    parser.add_argument("--max-chars", type=positive_int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    text = build_pack(
        project, args.chapter, args.characters, args.previous_full,
        args.recent_summaries, args.max_chars, args.all_character_states,
    )
    if args.stdout:
        print(text, end="")
        return 0
    output = args.output or project / "10_review" / f"context_pack_chapter_{args.chapter:04d}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
