# Project Structure

Each novel lives in one isolated directory. The canonical layout is:

```text
novels/
└── novel_slug/
    ├── 00_project/
    ├── 01_concept/
    ├── 02_world/
    ├── 03_characters/
    ├── 04_story/
    ├── 05_structure/
    ├── 06_chapters/
    ├── 07_summaries/
    ├── 08_memory/
    ├── 09_writing/
    ├── 10_review/
    └── 99_archive/
```

Use Markdown for human-readable canon and JSON/YAML for structured state. Prefer adding small focused files over one giant document.

## Folder Responsibilities

`00_project/`

- `project_schema.json`: project schema version and canon coverage for migration and freshness checks.
- `requirements.md`: normalized novel requirements extracted from the user's natural-language brief.
- `brief.md`: raw user request, extracted assumptions, target audience, length, chapter size, tone, freedom level.
- `status.yaml`: current chapter, volume, word counts, last completed operations, open risks.
- `change_log.md`: important changes, reasons, impact, and affected files.

`01_concept/`

- `core.md`: one-sentence story, premise, themes, core conflict, selling points, story goal.
- `synopsis.md`: expandable whole-book synopsis.
- `creative_contract.md`: intended reader experience, genre promise, emotional destination, AI freedom, locked decisions, and avoid list.

`02_world/`

- `world_bible.md`: geography, history, social structure, factions, systems, rules.
- `terms.yaml`: names, special items, abilities, places, terminology.
- `rules.yaml`: hard constraints that continuity checks should enforce.

`03_characters/`

- `characters.yaml`: index of important characters.
- `profiles/<character_slug>.md`: full profile for each major character.
- `states/<character_slug>.yaml`: current location, goals, knowledge, relationships, injuries, powers, mental state.
- `relationships.yaml`: relationship network and planned changes.

`04_story/`

- `master_outline.md`: whole-book outline.
- `story_engine.yaml`: dramatic question, recurring source of pressure, protagonist drivers, escalation ladder, irreversible choices, and climax prerequisites.
- `reader_promises.yaml`: expectations created for the reader and their preparation, target windows, payoff modes, and aftermath.
- `character_arcs.yaml`: wants, needs, misbeliefs, tests, choices, costs, and turning points for major arcs.
- `pacing_ledger.yaml`: per-chapter pressure, information, emotion, relationship movement, payoff, and scene-mode diagnostics.
- `plotlines.yaml`: main line, growth lines, romance, mystery, factions, side plots.
- `foreshadowing.yaml`: planted, advancing, resolved, or abandoned setups.
- `timeline.yaml`: event order, dates, ages, season, travel time.

`05_structure/`

- `volumes/volume_###.md`: volume goals, conflict, main characters, climax, growth, foreshadowing.
- `phases/phase_###.md`: optional act or stage outlines inside or across volumes.
- `chapter_toc.yaml`: structured chapter table of contents.
- `chapter_plans/chapter_####.yaml`: required plan before drafting each chapter.

`06_chapters/`

- `chapter_####.md`: final chapter manuscript.
- `drafts/`: optional partial drafts or alternatives.

`07_summaries/`

- `chapter_####_summary.md`: detailed summary.
- `chapter_####_short.md`: 50-100 Chinese character or concise-language quick summary.

`08_memory/`

- `novel_bible.md`: consolidated canon entrypoint for the current novel only.
- `permanent.md`: always-load facts: core concept, themes, hard rules, protagonist essentials, master outline.
- `state_snapshots/snapshot_chapter_####.md`: at the project-defined interval or a major structural turning point.
- `open_threads.md`: unresolved questions, promises, conflicts, and pending reveals.
- `information_ledger.yaml`: who knows each important fact, when they learned it, and through which channel.
- `scene_clock.yaml`: opening and ending time/location for chapters, used for next-chapter handoff checks.
- `deltas/chapter_####.json`: one transaction manifest for the state changes and derived-file updates caused by a chapter.
- `state_events.jsonl`: append-only record of applied chapter deltas without embedded replacement contents.
- `freshness.json`: derived-file hashes, source deltas, and the latest canon chapter each file covers.

`09_writing/`

- `style.md`: prose style and narration.
- `writing_rules.md`: chapter-level craft rules.
- `forbidden_patterns.md`: banned phrases and AI-like patterns.
- `vocabulary.md`: preferred terms, diction, character voice notes.
- `prompts.md`: novel-specific prompt guidance.
- `pov_voices.yaml`: viewpoint knowledge boundaries, attention bias, diction, metaphor sources, and narrative distance.
- `repetition_registry.json`: occurrence-scoped approvals for intentional verbatim echoes; never a global short-substring whitelist.

`10_review/`

- `continuity_pre_chapter_####.md`: pre-draft checks.
- `continuity_post_chapter_####.md`: post-draft checks.
- `context_pack_chapter_####.md`: generated working context for a chapter task.
- `gate_chapter_####.md`: generated deterministic and manual gate report for a chapter.
- `canon_gates_project.md`: project-specific hard gates derived from this novel's world, procedures, terminology, species, technology, magic, institutions, or prose constraints.
- `quality_chapter_####.md`: prose and chapter quality review.
- `impact_analysis_YYYYMMDD_HHMMSS.md`: dependency analysis for canon changes.

`99_archive/`

- Store timestamped copies of important canon files before major changes, preserving relative paths when useful.

## Naming

Use lowercase slugs for directories and file stems. Use zero-padded chapter numbers: `chapter_0001.md`, `chapter_0001.yaml`.

When the user gives a Chinese title, keep the display title in `00_project/brief.md` and use a safe slug for filenames.
