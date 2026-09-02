#!/usr/bin/env python3
"""Initialize an isolated long-form novel project directory."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path


FOLDERS = [
    "00_project",
    "01_concept",
    "02_world",
    "03_characters/profiles",
    "03_characters/states",
    "04_story",
    "05_structure/volumes",
    "05_structure/phases",
    "05_structure/chapter_plans",
    "06_chapters/drafts",
    "07_summaries",
    "08_memory/state_snapshots",
    "09_writing",
    "10_review",
    "99_archive",
]


def slugify(value: str) -> str:
    raw = value.strip()
    value = raw.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value, flags=re.ASCII)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if value:
        return value
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"novel-{digest}"


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def yaml_quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    escaped = "".join(ch if ch >= " " else f"\\x{ord(ch):02x}" for ch in escaped)
    return '"' + escaped + '"'


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a novel-architect project skeleton.")
    parser.add_argument("title", help="Novel display title")
    parser.add_argument("--root", default="novels", help="Directory that will contain novel projects")
    parser.add_argument("--slug", help="Filesystem-safe project slug")
    parser.add_argument("--genre", default="", help="Novel genre")
    parser.add_argument("--brief", default="", help="Raw natural-language novel brief")
    parser.add_argument("--core-idea", default="", help="Core story idea")
    parser.add_argument("--protagonist", default="", help="Initial protagonist description")
    parser.add_argument("--target-readers", default="", help="Target readers")
    parser.add_argument("--style", default="", help="Writing style")
    parser.add_argument("--pace", default="", help="Narrative pace")
    parser.add_argument("--romance-intensity", default="")
    parser.add_argument("--suspense-density", default="")
    parser.add_argument("--payoff-density", default="")
    parser.add_argument("--ai-freedom", default="")
    parser.add_argument("--target-total-words", type=non_negative_int, default=0)
    parser.add_argument("--target-chapter-words", type=non_negative_int, default=0)
    parser.add_argument("--target-chapter-count", type=non_negative_int)
    parser.add_argument("--force", action="store_true", help="Allow using an existing project directory")
    parser.add_argument("--dry-run", action="store_true", help="Print the target directory without creating files")
    args = parser.parse_args()

    slug = slugify(args.slug) if args.slug else slugify(args.title)
    root = Path(args.root).expanduser().resolve()
    project = root / slug
    if root.anchor == str(root):
        raise SystemExit(f"Refusing to create a novel project directly under filesystem root: {root}")
    if project.exists() and not args.force:
        raise SystemExit(f"Project already exists: {project}")
    if args.dry_run:
        print(project)
        return 0

    for folder in FOLDERS:
        (project / folder).mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now().isoformat(timespec="seconds")
    core_idea = args.core_idea or args.brief
    brief = f"""# {args.title}

## Raw Brief

{args.brief}

## Extracted Requirements

- Title: {args.title}
- Slug: {slug}
- Genre: {args.genre}
- Core story idea: {core_idea}
- Target total words: {args.target_total_words or ""}
- Target chapter words: {args.target_chapter_words or ""}
- Target chapter count: {args.target_chapter_count or ""}
- Protagonist: {args.protagonist}
- Target readers: {args.target_readers}
- Writing style: {args.style}
- Pace: {args.pace}
- Romance intensity: {args.romance_intensity}
- Suspense density: {args.suspense_density}
- Payoff density: {args.payoff_density}
- AI creative freedom: {args.ai_freedom}

## Assumptions

## Missing Decisions
"""
    write_if_missing(project / "00_project" / "brief.md", brief)

    requirements = f"""# Requirements

- Title: {args.title}
- Genre: {args.genre}
- Target total words: {args.target_total_words or ""}
- Target chapter words: {args.target_chapter_words or ""}
- Target chapter count: {args.target_chapter_count or ""}
- Core story idea: {core_idea}
- Protagonist: {args.protagonist}
- Target readers: {args.target_readers}
- Writing style: {args.style}
- Pace: {args.pace}
- Romance intensity: {args.romance_intensity}
- Suspense density: {args.suspense_density}
- Payoff density: {args.payoff_density}
- AI creative freedom: {args.ai_freedom}

## Inferred Assumptions

## Open Questions
"""
    write_if_missing(project / "00_project" / "requirements.md", requirements)

    chapter_count = args.target_chapter_count if args.target_chapter_count is not None else "null"
    status = f"""title: {yaml_quote(args.title)}
slug: {yaml_quote(slug)}
genre: {yaml_quote(args.genre)}
target_total_words: {args.target_total_words}
target_chapter_words: {args.target_chapter_words}
target_chapter_count: {chapter_count}
current_volume: 1
current_chapter: 0
last_completed_chapter: 0
total_words_estimate: 0
phase: "created"
open_risks: []
next_action: "plan"
updated_at: {yaml_quote(now)}
"""
    write_if_missing(project / "00_project" / "status.yaml", status)

    placeholders = {
        "00_project/change_log.md": "# Change Log\n",
        "01_concept/core.md": "# Core Concept\n",
        "01_concept/synopsis.md": "# Synopsis\n",
        "02_world/world_bible.md": "# World Bible\n",
        "02_world/terms.yaml": "terms: []\n",
        "02_world/rules.yaml": "rules: []\n",
        "03_characters/characters.yaml": "characters: []\n",
        "03_characters/relationships.yaml": "relationships: []\n",
        "04_story/master_outline.md": "# Master Outline\n",
        "04_story/plotlines.yaml": "plotlines: []\n",
        "04_story/foreshadowing.yaml": "foreshadowing: []\n",
        "04_story/timeline.yaml": "events: []\n",
        "05_structure/chapter_toc.yaml": "chapters: []\n",
        "05_structure/volumes/volume_001.md": "# Volume 001\n\n## Goal\n\n## Main Conflict\n\n## Main Characters\n\n## Protagonist Growth\n\n## Climax\n\n## Ending Climax\n\n## Foreshadowing Progress\n",
        "05_structure/phases/phase_001.md": "# Phase 001\n\n## Goal\n\n## Scope\n\n## Turning Point\n",
        "08_memory/novel_bible.md": "# Novel Bible\n",
        "08_memory/permanent.md": "# Permanent Memory\n",
        "08_memory/open_threads.md": "# Open Threads\n",
        "09_writing/style.md": "# Style\n",
        "09_writing/writing_rules.md": "# Writing Rules\n",
        "09_writing/forbidden_patterns.md": "# Forbidden Patterns\n\n- 微微一愣\n- 不禁\n- 嘴角勾起\n- 眼中闪过\n- 空气仿佛凝固\n- 倒吸一口凉气\n- 这一刻终于明白\n- 命运的齿轮\n",
        "09_writing/vocabulary.md": "# Vocabulary\n",
        "09_writing/prompts.md": "# Novel-Specific Prompts\n",
    }
    for rel_path, content in placeholders.items():
        write_if_missing(project / rel_path, content)

    print(project, file=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
