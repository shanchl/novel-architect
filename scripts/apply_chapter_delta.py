#!/usr/bin/env python3
"""Validate or atomically apply a chapter delta. Default mode is dry-run."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from project_templates import PROJECT_SCHEMA_VERSION, chapter_delta_template


REQUIRED_LISTS = [
    "events", "state_changes", "knowledge_changes", "object_changes",
    "relationship_changes", "timeline_changes", "plotline_changes",
    "promise_changes", "file_updates", "confirmed_current", "blocking_risks",
]
MANAGED_PATHS = {
    "00_project/status.yaml", "00_project/project_schema.json",
    "08_memory/freshness.json", "08_memory/state_events.jsonl",
}


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Invalid delta JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Delta root must be an object")
    return value


def safe_target(project: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not relative or ".." in rel.parts:
        raise SystemExit(f"Unsafe delta target: {relative!r}")
    target = (project / rel).resolve()
    try:
        target.relative_to(project)
    except ValueError as exc:
        raise SystemExit(f"Delta target escapes project: {relative!r}") from exc
    if rel.parts[0].lower() in {".git", "99_archive"}:
        raise SystemExit(f"Delta cannot write managed or archive path: {relative!r}")
    return target


def required_views(chapter: int) -> list[str]:
    return [
        f"07_summaries/chapter_{chapter:04d}_summary.md",
        f"07_summaries/chapter_{chapter:04d}_short.md",
        "04_story/timeline.yaml",
        "08_memory/scene_clock.yaml",
        "08_memory/information_ledger.yaml",
    ]


def validate_delta(project: Path, chapter: int, delta: dict) -> tuple[list[tuple[str, Path, str]], list[str]]:
    errors: list[str] = []
    if delta.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if delta.get("chapter") != chapter or delta.get("canon_through_chapter") != chapter:
        errors.append("chapter and canon_through_chapter must match --chapter")
    for key in REQUIRED_LISTS:
        if not isinstance(delta.get(key), list):
            errors.append(f"{key} must be a list")
    if delta.get("blocking_risks"):
        errors.append("blocking_risks must be empty before apply")

    updates: list[tuple[str, Path, str]] = []
    seen: set[str] = set()
    for item in delta.get("file_updates", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
            errors.append("each file_updates item needs string path and content")
            continue
        rel = Path(item["path"]).as_posix()
        if rel in MANAGED_PATHS or rel.startswith("08_memory/deltas/"):
            errors.append(f"file_updates cannot replace transaction-managed path: {rel}")
            continue
        if rel in seen:
            errors.append(f"duplicate file update: {rel}")
            continue
        seen.add(rel)
        updates.append((rel, safe_target(project, rel), item["content"]))

    confirmed: set[str] = set()
    for item in delta.get("confirmed_current", []):
        rel = Path(str(item)).as_posix()
        target = safe_target(project, rel)
        if not target.is_file():
            errors.append(f"confirmed current path is not a file: {rel}")
        confirmed.add(rel)
    for rel in seen & confirmed:
        errors.append(f"path cannot be both updated and confirmed current: {rel}")
    touched = seen | confirmed
    for rel in required_views(chapter):
        if rel not in touched:
            errors.append(f"required view is neither updated nor confirmed current: {rel}")
        elif rel in confirmed and not (project / rel).exists():
            errors.append(f"confirmed current file does not exist: {rel}")
    return updates, errors


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update_status(text: str, chapter: int, timestamp: str) -> str:
    replacements = {
        "project_schema_version": f'"{PROJECT_SCHEMA_VERSION}"',
        "current_chapter": str(chapter),
        "last_completed_chapter": str(chapter),
        "phase": '"chapter_complete"',
        "next_action": f'"plan chapter {chapter + 1}"',
        "updated_at": f'"{timestamp}"',
    }
    for key, value in replacements.items():
        pattern = rf"(?m)^{re.escape(key)}:\s*.*$"
        line = f"{key}: {value}"
        text, count = re.subn(pattern, line, text, count=1)
        if not count:
            text = line + "\n" + text
    return text


def event_record(delta: dict, paths: list[str], timestamp: str, delta_digest: str) -> dict:
    return {
        key: value for key, value in delta.items() if key != "file_updates"
    } | {"applied_at": timestamp, "updated_files": paths, "delta_sha256": delta_digest}


def prior_application(project: Path, chapter: int) -> dict | None:
    events = project / "08_memory" / "state_events.jsonl"
    if not events.exists():
        return None
    for line in reversed(events.read_text(encoding="utf-8").splitlines()):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("chapter") == chapter:
            return event
    return None


def apply_delta(project: Path, chapter: int, delta_path: Path, delta: dict, updates: list[tuple[str, Path, str]]) -> Path:
    timestamp = dt.datetime.now().isoformat(timespec="seconds")
    archive_stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    archive_root = project / "99_archive" / archive_stamp / f"chapter_delta_{chapter:04d}"
    staged: list[tuple[str, Path, Path, bool]] = []
    replaced: list[tuple[Path, Path | None, bool]] = []
    metadata_paths = [
        project / "08_memory" / "freshness.json",
        project / "08_memory" / "state_events.jsonl",
        project / "00_project" / "status.yaml",
        project / "00_project" / "project_schema.json",
    ]
    metadata_originals = {path: path.read_bytes() if path.exists() else None for path in metadata_paths}
    delta_digest = sha256(delta_path)
    try:
        for rel, target, content in updates:
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=target.parent, newline="")
            with handle:
                handle.write(content)
            staged.append((rel, target, Path(handle.name), target.exists()))

        for rel, target, temporary, existed in staged:
            backup = None
            if existed:
                backup = archive_root / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            os.replace(temporary, target)
            replaced.append((target, backup, existed))

        tracked = sorted({rel for rel, _, _, _ in staged} | {Path(str(item)).as_posix() for item in delta["confirmed_current"]})
        for path, original in metadata_originals.items():
            if original is not None:
                rel = path.relative_to(project)
                backup = archive_root / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(original)
        freshness_path = project / "08_memory" / "freshness.json"
        try:
            freshness = json.loads(freshness_path.read_text(encoding="utf-8")) if freshness_path.exists() else {}
        except ValueError as exc:
            raise RuntimeError(f"invalid freshness registry: {exc}") from exc
        for rel in tracked:
            path = project / rel
            freshness[rel] = {
                "canon_through_chapter": chapter,
                "generated_from": (
                    delta_path.relative_to(project).as_posix()
                    if delta_path.is_relative_to(project)
                    else str(delta_path)
                ),
                "sha256": sha256(path),
                "updated_at": timestamp,
            }
        freshness_path.parent.mkdir(parents=True, exist_ok=True)
        freshness_path.write_text(json.dumps(freshness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        events_path = project / "08_memory" / "state_events.jsonl"
        with events_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event_record(delta, tracked, timestamp, delta_digest), ensure_ascii=False) + "\n")

        status_path = project / "00_project" / "status.yaml"
        status_path.write_text(update_status(status_path.read_text(encoding="utf-8"), chapter, timestamp), encoding="utf-8")

        schema_path = project / "00_project" / "project_schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path.exists() else {}
        schema.update({"schema_version": PROJECT_SCHEMA_VERSION, "canon_through_chapter": chapter})
        schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return archive_root
    except Exception:
        for target, backup, existed in reversed(replaced):
            if existed and backup is not None and backup.exists():
                shutil.copy2(backup, target)
            elif not existed and target.exists():
                target.unlink()
        for path, original in metadata_originals.items():
            if original is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
        raise
    finally:
        for _, _, temporary, _ in staged:
            if temporary.exists():
                temporary.unlink()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Validate or apply a chapter delta; dry-run by default.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--delta", type=Path)
    parser.add_argument("--write-template", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.chapter < 1:
        parser.error("chapter must be positive")

    project = args.project.resolve()
    delta_path = (args.delta.resolve() if args.delta else project / "08_memory" / "deltas" / f"chapter_{args.chapter:04d}.json")
    if args.write_template:
        if delta_path.exists():
            raise SystemExit(f"Refusing to overwrite existing delta: {delta_path}")
        delta_path.parent.mkdir(parents=True, exist_ok=True)
        delta_path.write_text(json.dumps(chapter_delta_template(args.chapter) | {"confirmed_current": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"TEMPLATE {delta_path}")
        return 0

    delta = read_json(delta_path)
    updates, errors = validate_delta(project, args.chapter, delta)
    if errors:
        for error in errors:
            print(f"BLOCK {error}")
        return 1
    prior = prior_application(project, args.chapter)
    digest = sha256(delta_path)
    if prior is not None:
        if prior.get("delta_sha256") == digest:
            print(f"ALREADY_APPLIED chapter={args.chapter:04d} delta is unchanged")
            return 0
        print(f"BLOCK chapter {args.chapter:04d} already has an applied delta; use the canon-revision workflow")
        return 1
    print(f"VALID chapter={args.chapter:04d} updates={len(updates)} confirmed={len(delta['confirmed_current'])}")
    for rel, _, _ in updates:
        print(f"UPDATE {rel}")
    if not args.apply:
        print("DRY_RUN no files changed; re-run with --apply after review")
        return 0
    archive = apply_delta(project, args.chapter, delta_path, delta, updates)
    print(f"APPLIED chapter={args.chapter:04d}")
    print(f"ARCHIVE {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
