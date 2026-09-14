"""Shared project schema and templates for novel-architect projects."""

from __future__ import annotations

import json


PROJECT_SCHEMA_VERSION = "1.3.0"


def project_schema(title: str = "", slug: str = "", canon_through_chapter: int = 0) -> str:
    return json.dumps(
        {
            "schema_version": PROJECT_SCHEMA_VERSION,
            "title": title,
            "slug": slug,
            "canon_through_chapter": canon_through_chapter,
            "created_by": "novel-architect",
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


NEW_PROJECT_FILES = {
    "01_concept/creative_contract.md": """# Creative Contract

## Reader Promise

## Genre Experience

## Emotional Destination

## Authorship Boundaries

- AI freedom:
- Locked decisions:
- Suggest-only areas:

## Non-Negotiables

## Avoid
""",
    "04_story/story_engine.yaml": """story_engine:
  central_dramatic_question: ""
  narrative_engine: ""
  protagonist:
    want: ""
    need: ""
    misbelief: ""
    fear: ""
    moral_line: ""
  core_stakes:
    external: ""
    internal: ""
    relational: ""
  escalation_ladder: []
  irreversible_choices: []
  climax_preconditions: []
""",
    "04_story/reader_promises.yaml": """promises: []
""",
    "04_story/character_arcs.yaml": """arcs: []
""",
    "04_story/pacing_ledger.yaml": """chapters: []
""",
    "09_writing/pov_voices.yaml": """voices: []
""",
    "09_writing/repetition_registry.json": """{
  "schema_version": 1,
  "entries": []
}
""",
    "08_memory/state_events.jsonl": "",
    "08_memory/freshness.json": "{}\n",
}


def chapter_delta_template(chapter: int) -> dict:
    return {
        "schema_version": 1,
        "chapter": chapter,
        "canon_through_chapter": chapter,
        "summary": "",
        "events": [],
        "state_changes": [],
        "knowledge_changes": [],
        "object_changes": [],
        "relationship_changes": [],
        "timeline_changes": [],
        "plotline_changes": [],
        "promise_changes": [],
        "file_updates": [],
        "confirmed_current": [],
        "blocking_risks": [],
        "updated_at": "",
    }
