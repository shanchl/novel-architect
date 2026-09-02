# Novel Architect

`novel-architect` is a Codex skill for project-managed long-form fiction creation. It is designed for medium, long, serial, and ultra-long novels where continuity, structured memory, character state, foreshadowing, timeline, and style control matter more than simply generating the next block of prose.

## What It Does

- Creates one isolated project directory per novel.
- Maintains a novel bible, requirements, concept notes, worldbuilding, characters, relationships, outlines, plotlines, foreshadowing, timeline, chapter plans, manuscripts, summaries, long-term memory, writing rules, reviews, and change logs.
- Builds focused context packs instead of loading the entire manuscript.
- Checks continuity before and after chapter drafting.
- Updates summaries, character states, plotlines, foreshadowing, timeline, and project status after each chapter.
- Supports change impact analysis before modifying established canon.
- Supports anti-AI writing-pattern checks through forbidden phrases, rhythm checks, cliché detection, repeated reaction beats, and voice consistency review.

## Directory Layout

Each novel should live in its own directory:

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

See `references/project-structure.md` for the full file ownership model.

## Commands

The skill recognizes these workflows, whether the user types the command directly or describes the task naturally:

- `/novel create`
- `/novel plan`
- `/novel bible`
- `/novel outline`
- `/novel toc`
- `/novel chapter plan`
- `/novel write`
- `/novel continue`
- `/novel summarize`
- `/novel check`
- `/novel review`
- `/novel revise`
- `/novel memory`
- `/novel status`

See `references/workflows.md` for the detailed command behavior.

## Initialize A Novel Project

Use the helper script to create a new novel skeleton:

```bash
python D:\skills\novel-architect\scripts\init_novel.py "归墟灯塔" --root novels --genre "科幻悬疑" --target-total-words 600000 --target-chapter-words 3200
```

Useful options:

```bash
--brief "失忆工程师在海底城市追查一座灯塔的真相"
--protagonist "林砚，前深海结构工程师"
--target-readers "喜欢强设定悬疑的读者"
--style "冷峻、克制、有画面感"
--pace "中快"
--romance-intensity "低"
--suspense-density "高"
--payoff-density "中高"
--ai-freedom "中"
--dry-run
```

`--dry-run` prints the target path without creating files. The script rejects negative counts, refuses to create directly under a filesystem root, and normalizes unsafe slugs.

## Core References

- `SKILL.md`: entrypoint and routing rules.
- `references/project-structure.md`: canonical novel project layout.
- `references/workflows.md`: `/novel` workflows, versioning, and change impact analysis.
- `references/memory-and-continuity.md`: memory layers, context packs, continuity checks, and post-chapter updates.
- `references/writing-control.md`: style control, anti-AI pattern checks, and quality review.
- `references/schemas.md`: suggested YAML and Markdown templates.

## Validation

Validate the skill structure with:

```bash
python C:\Users\chang\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\skills\novel-architect
```

The current version has been checked with `quick_validate.py`, script syntax checks, initialization tests, edge-case slug tests, negative-input rejection tests, dry-run tests, and an independent review pass.
