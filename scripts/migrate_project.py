#!/usr/bin/env python3
"""Additively migrate an existing novel-architect project to the current schema."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

from project_templates import NEW_PROJECT_FILES, PROJECT_SCHEMA_VERSION, project_schema


def version_tuple(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value)
    return tuple(int(part) for part in match.groups()) if match else None


def status_int(text: str, key: str, default: int = 0) -> int:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(\d+)\s*$", text)
    return int(match.group(1)) if match else default


def current_version(project: Path) -> str:
    schema = project / "00_project" / "project_schema.json"
    if not schema.exists():
        return "legacy"
    try:
        return str(json.loads(schema.read_text(encoding="utf-8")).get("schema_version", "legacy"))
    except ValueError:
        return "invalid"


def planned_changes(project: Path) -> list[str]:
    changes = [rel for rel in NEW_PROJECT_FILES if not (project / rel).exists()]
    if current_version(project) != PROJECT_SCHEMA_VERSION:
        changes.append("00_project/project_schema.json")
    status = project / "00_project" / "status.yaml"
    if status.exists() and not re.search(
        rf'(?m)^project_schema_version:\s*["\']?{re.escape(PROJECT_SCHEMA_VERSION)}["\']?\s*$',
        status.read_text(encoding="utf-8"),
    ):
        changes.append("00_project/status.yaml (set project_schema_version)")
    return changes


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Migrate a novel project; dry-run by default.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--to-version", choices=[PROJECT_SCHEMA_VERSION], default=PROJECT_SCHEMA_VERSION)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    status = project / "00_project" / "status.yaml"
    if not status.exists():
        raise SystemExit(f"Not a novel-architect project: missing {status}")

    source_version = current_version(project)
    if source_version == "invalid":
        raise SystemExit("Cannot migrate: 00_project/project_schema.json is invalid JSON")
    parsed_source = version_tuple(source_version)
    if parsed_source is not None and parsed_source > version_tuple(PROJECT_SCHEMA_VERSION):
        raise SystemExit(f"Refusing to downgrade newer project schema {source_version}")
    changes = planned_changes(project)
    print(f"FROM {source_version}")
    print(f"TO {args.to_version}")
    for item in changes:
        print(f"ADD_OR_UPDATE {item}")
    if not args.apply:
        print("DRY_RUN no files changed; re-run with --apply after review")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    archive = project / "99_archive" / stamp / "schema_migration"
    status_text = status.read_text(encoding="utf-8")
    canon_baseline = status_int(status_text, "last_completed_chapter")
    if not re.search(
        rf'(?m)^project_schema_version:\s*["\']?{re.escape(PROJECT_SCHEMA_VERSION)}["\']?\s*$',
        status_text,
    ):
        archived_status = archive / "00_project" / "status.yaml"
        archived_status.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(status, archived_status)
        if re.search(r"(?m)^project_schema_version:", status_text):
            updated_status = re.sub(
                r"(?m)^project_schema_version:\s*.*$",
                f'project_schema_version: "{PROJECT_SCHEMA_VERSION}"',
                status_text,
                count=1,
            )
        else:
            updated_status = f'project_schema_version: "{PROJECT_SCHEMA_VERSION}"\n' + status_text
        status.write_text(updated_status, encoding="utf-8")

    for rel, content in NEW_PROJECT_FILES.items():
        path = project / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    schema_path = project / "00_project" / "project_schema.json"
    if not schema_path.exists():
        title_match = re.search(r'(?m)^title:\s*["\']?([^\n"\']+)', status_text)
        slug_match = re.search(r'(?m)^slug:\s*["\']?([^\n"\']+)', status_text)
        schema_path.write_text(project_schema(
            title_match.group(1).strip() if title_match else "",
            slug_match.group(1).strip() if slug_match else project.name,
            canon_baseline,
        ), encoding="utf-8")
    elif current_version(project) != PROJECT_SCHEMA_VERSION:
        archived_schema = archive / "00_project" / "project_schema.json"
        archived_schema.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(schema_path, archived_schema)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["schema_version"] = PROJECT_SCHEMA_VERSION
        schema["canon_through_chapter"] = max(int(schema.get("canon_through_chapter", 0)), canon_baseline)
        schema.setdefault("created_by", "novel-architect")
        schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MIGRATED {project}")
    if archive.exists():
        print(f"ARCHIVE {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
