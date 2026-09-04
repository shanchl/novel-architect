#!/usr/bin/env python3
"""Bump novel-architect skill version in VERSION, SKILL.md, and README.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
SKILL_FILE = ROOT / "SKILL.md"
README_FILE = ROOT / "README.md"


def parse_version(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        raise SystemExit(f"Invalid semantic version: {value!r}")
    return tuple(int(part) for part in match.groups())


def bump(version: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if part == "major":
        return major + 1, 0, 0
    if part == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def replace_once(text: str, pattern: str, replacement: str, path: Path) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Expected one version match in {path}")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump skill semantic version.")
    parser.add_argument("part", nargs="?", choices=["major", "minor", "patch"], default="patch")
    args = parser.parse_args()

    current = parse_version(VERSION_FILE.read_text(encoding="utf-8"))
    new_version = ".".join(str(part) for part in bump(current, args.part))

    VERSION_FILE.write_text(new_version + "\n", encoding="utf-8")

    skill = SKILL_FILE.read_text(encoding="utf-8")
    skill = replace_once(skill, r"^  version: \d+\.\d+\.\d+$", f"  version: {new_version}", SKILL_FILE)
    skill = replace_once(skill, r"^Current version: `\d+\.\d+\.\d+`\.$", f"Current version: `{new_version}`.", SKILL_FILE)
    SKILL_FILE.write_text(skill, encoding="utf-8")

    readme = README_FILE.read_text(encoding="utf-8")
    readme = replace_once(readme, r"^Version: `\d+\.\d+\.\d+`$", f"Version: `{new_version}`", README_FILE)
    README_FILE.write_text(readme, encoding="utf-8")

    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
