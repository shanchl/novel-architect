#!/usr/bin/env python3
"""Build a focused context pack for a novel-architect chapter task."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path


MAX_TEXT_CHARS = 12000


def read_if_exists(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return f"_Missing: `{path}`_\n"
    text = path.read_text(encoding="utf-8")
    if limit is not None and len(text) > limit:
        return text[:limit] + f"\n\n_[Truncated at {limit} characters.]_\n"
    return text


def section(title: str, body: str) -> str:
    return f"\n## {title}\n\n{body.strip()}\n"


def existing_short_summaries(project: Path) -> list[Path]:
    return sorted((project / "07_summaries").glob("chapter_*_short.md"))


def previous_chapter_paths(project: Path, chapter: int, count: int) -> list[Path]:
    paths: list[Path] = []
    for number in range(max(1, chapter - count), chapter):
        path = project / "06_chapters" / f"chapter_{number:04d}.md"
        if path.exists():
            paths.append(path)
    return paths


def character_state_paths(project: Path, names: list[str]) -> list[Path]:
    states_dir = project / "03_characters" / "states"
    if not names:
        return sorted(states_dir.glob("*.yaml"))
    selected: list[Path] = []
    lowered = [name.lower() for name in names]
    for path in sorted(states_dir.glob("*.yaml")):
        stem = path.stem.lower()
        text = path.read_text(encoding="utf-8").lower()
        if any(name in stem or name in text for name in lowered):
            selected.append(path)
    return selected


def build_pack(project: Path, chapter: int, characters: list[str], previous_full: int) -> str:
    chapter_id = f"{chapter:04d}"
    now = dt.datetime.now().isoformat(timespec="seconds")
    parts = [
        f"# Context Pack · Chapter {chapter_id}\n\n- Project: `{project}`\n- Generated: `{now}`\n",
        section("Project Status", read_if_exists(project / "00_project" / "status.yaml")),
        section("Core Concept", read_if_exists(project / "01_concept" / "core.md", MAX_TEXT_CHARS)),
        section("Permanent Memory", read_if_exists(project / "08_memory" / "permanent.md", MAX_TEXT_CHARS)),
        section("Hard World Rules", read_if_exists(project / "02_world" / "rules.yaml", MAX_TEXT_CHARS)),
        section("Open Threads", read_if_exists(project / "08_memory" / "open_threads.md", MAX_TEXT_CHARS)),
        section("Chapter Plan", read_if_exists(project / "05_structure" / "chapter_plans" / f"chapter_{chapter_id}.yaml", MAX_TEXT_CHARS)),
    ]

    short_blocks = []
    for path in existing_short_summaries(project):
        short_blocks.append(f"### {path.name}\n\n{read_if_exists(path, 1200).strip()}")
    parts.append(section("All Short Summaries", "\n\n".join(short_blocks) if short_blocks else "_No short summaries found._"))

    prev_summary = project / "07_summaries" / f"chapter_{chapter - 1:04d}_summary.md"
    if chapter > 1:
        parts.append(section("Previous Detailed Summary", read_if_exists(prev_summary, MAX_TEXT_CHARS)))

    state_blocks = []
    for path in character_state_paths(project, characters):
        state_blocks.append(f"### {path.name}\n\n```yaml\n{read_if_exists(path, 5000).strip()}\n```")
    parts.append(section("Relevant Character States", "\n\n".join(state_blocks) if state_blocks else "_No character states found._"))

    parts.extend([
        section("Information Ledger", f"```yaml\n{read_if_exists(project / '08_memory' / 'information_ledger.yaml', MAX_TEXT_CHARS).strip()}\n```"),
        section("Scene Clock", f"```yaml\n{read_if_exists(project / '08_memory' / 'scene_clock.yaml', MAX_TEXT_CHARS).strip()}\n```"),
        section("Timeline", f"```yaml\n{read_if_exists(project / '04_story' / 'timeline.yaml', MAX_TEXT_CHARS).strip()}\n```"),
        section("Project-Specific Canon Gates", read_if_exists(project / "10_review" / "canon_gates_project.md", MAX_TEXT_CHARS)),
        section("Writing Style", read_if_exists(project / "09_writing" / "style.md", MAX_TEXT_CHARS)),
        section("Writing Rules", read_if_exists(project / "09_writing" / "writing_rules.md", MAX_TEXT_CHARS)),
        section("Forbidden Patterns", read_if_exists(project / "09_writing" / "forbidden_patterns.md", MAX_TEXT_CHARS)),
        section("Vocabulary", read_if_exists(project / "09_writing" / "vocabulary.md", MAX_TEXT_CHARS)),
    ])

    manuscript_blocks = []
    for path in previous_chapter_paths(project, chapter, previous_full):
        manuscript_blocks.append(f"### {path.name}\n\n{read_if_exists(path).strip()}")
    parts.append(section("Previous Full Manuscripts", "\n\n".join(manuscript_blocks) if manuscript_blocks else "_No previous manuscripts found._"))

    parts.append(section("Use Notes", "\n".join([
        "- Use this pack for chapter planning, drafting, revision, or review.",
        "- If a blocking continuity question remains unresolved, inspect the source file directly before writing prose.",
        "- Do not treat this generated pack as project canon; update the source files instead.",
    ])))
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Build a focused context pack for a chapter.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--characters", nargs="*", default=[], help="Optional character names/slugs to include")
    parser.add_argument("--previous-full", type=int, default=2, help="How many previous chapter manuscripts to include")
    parser.add_argument("--stdout", action="store_true", help="Print instead of writing 10_review/context_pack_chapter_####.md")
    parser.add_argument("--output", type=Path, help="Custom output path")
    args = parser.parse_args()

    project = args.project.resolve()
    text = build_pack(project, args.chapter, args.characters, args.previous_full)
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
