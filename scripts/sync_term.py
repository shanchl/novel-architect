#!/usr/bin/env python3
"""Find or replace a term across a novel-architect project.

Default mode is dry-run. Use --replace-with plus --apply for mutation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_INCLUDE = {
    ".md", ".yaml", ".yml", ".json", ".txt"
}

SKIP_DIRS = {".git", "__pycache__", "99_archive"}


def iter_files(project: Path) -> list[Path]:
    files: list[Path] = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in DEFAULT_INCLUDE:
            files.append(path)
    return sorted(files)


def find_hits(path: Path, term: str) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    hits: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if term in line:
            hits.append((number, line.strip()))
    return hits


def replace_term(path: Path, old: str, new: str) -> int:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count:
        path.write_text(text.replace(old, new), encoding="utf-8")
    return count


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Find or replace a project term.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--term", required=True)
    parser.add_argument("--replace-with")
    parser.add_argument("--apply", action="store_true", help="Actually write replacements")
    args = parser.parse_args()

    project = args.project.resolve()
    total_hits = 0
    hit_files: list[Path] = []
    for path in iter_files(project):
        hits = find_hits(path, args.term)
        if not hits:
            continue
        hit_files.append(path)
        total_hits += len(hits)
        print(path)
        for line_number, line in hits[:20]:
            print(f"  {line_number}: {line}")
        if len(hits) > 20:
            print(f"  ... {len(hits) - 20} more")

    print(f"FILES {len(hit_files)}")
    print(f"HITS {total_hits}")

    if args.replace_with is None:
        return 0
    if not args.apply:
        print("DRY_RUN replacement not applied. Re-run with --apply to write changes.")
        return 0

    replaced = 0
    for path in hit_files:
        replaced += replace_term(path, args.term, args.replace_with)
    print(f"REPLACED {replaced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
