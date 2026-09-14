# Schemas and Templates

These shapes are recommendations, not a rigid database. Preserve useful existing project formats when updating an established novel.

## `00_project/project_schema.json`

```json
{
  "schema_version": "1.3.0",
  "title": "",
  "slug": "",
  "canon_through_chapter": 0,
  "created_by": "novel-architect"
}
```

## `00_project/status.yaml`

```yaml
title: ""
project_schema_version: "1.3.0"
slug: ""
genre: ""
target_total_words: 0
target_chapter_words: 0
target_chapter_count: null
current_volume: 1
current_chapter: 0
last_completed_chapter: 0
total_words_estimate: 0
phase: "created"
open_risks: []
next_action: "plan"
updated_at: ""
```

## `08_memory/information_ledger.yaml`

```yaml
facts:
  - id: "IF-001"
    chapter_introduced: 1
    fact: ""
    known_by: []
    not_known_by: []
    source_channel: ""
    learned_at: ""
    evidence_file: ""
    constraints: []
    notes: ""
```

## `08_memory/scene_clock.yaml`

```yaml
time_baseline:
  label: "story_day_0"
  description: ""
chapters:
  - chapter: 1
    day_index_open: 0
    night_index_open: 0
    opening_time: ""
    opening_location: ""
    opening_anchor_event: ""
    opening_relation_to_previous: "immediate"
    day_index_close: 0
    night_index_close: 0
    ending_time: ""
    ending_location: ""
    elapsed_time: ""
    unresolved_immediate_actions: []
    next_chapter_handoff: ""
    relative_time_notes: []
```

## `10_review/continuity_pre_chapter_0001.md`

```markdown
# Continuity Pre-Check · Chapter 0001

## Time Handoff

## New-Information Inventory

## Character Locations

## Character Knowledge

## Character Possessions and Access

## Information Chain

## Domain and Canon Constraints

## Blocking Risks
```

## `10_review/continuity_post_chapter_0001.md`

```markdown
# Continuity Post-Check · Chapter 0001

## Ending State

## New Facts

## Information Learned By Character

## Objects and Evidence

## State Updates

## Timeline Updates

## Summary Updates

## Residual Risks
```

## `09_writing/repetition_registry.json`

```json
{
  "schema_version": 1,
  "entries": [
    {
      "id": "echo-example",
      "text": "",
      "category": "intentional_echo",
      "chapters": [1, 8],
      "reason": ""
    }
  ]
}
```

Valid categories are `intentional_echo`, `term_or_name`, `motif`, and `necessary_reminder`. Register exact text and explicit chapter occurrences. Do not add `needs_revision` entries or short global suppression fragments.

## `00_project/change_log.md`

```markdown
# Change Log

## YYYY-MM-DD HH:MM:SS

- Reason:
- Archived files:
- Changed files:
- Affected chapters:
- Affected summaries:
- Affected character states:
- Affected plotlines:
- Affected foreshadowing:
- Affected timeline entries:
- Remaining risks:
```

## `05_structure/chapter_toc.yaml`

```yaml
chapters:
  - chapter: 1
    title: ""
    volume: 1
    goal: ""
    main_events: []
    involved_characters: []
    state_changes: []
    core_conflict: ""
    reveals: []
    foreshadowing: []
    plot_progress: []
    climax: ""
    hook: ""
    target_words: 0
    status: "planned"
```

## `05_structure/chapter_plans/chapter_0001.yaml`

```yaml
chapter: 1
title: ""
volume: 1
target_words: 0
chapter_goal: ""
opening: ""
scenes:
  - id: "s1"
    location: ""
    time: ""
    pov: ""
    characters: []
    purpose: ""
    scene_question: ""
    character_objective: ""
    opposition: ""
    conflict: ""
    emotional_shift: ""
    choice: ""
    cost: ""
    value_before: ""
    value_after: ""
    causes_next_scene: ""
    reader_question_opened: ""
    reader_question_answered: ""
    reveal: ""
    foreshadowing: []
main_events: []
character_state_changes: []
core_conflict: ""
reveals: []
foreshadowing: []
plotline_progress: []
climax: ""
ending_hook: ""
continuity_constraints: []
```

## `04_story/reader_promises.yaml`

```yaml
promises:
  - id: "RP-001"
    type: "mystery"
    promise: ""
    importance: "major"
    reader_knows: []
    expected_experience: ""
    preparation_ids: []
    legitimate_misdirection: []
    payoff_prerequisites: []
    target_window: []
    status: "open"
    payoff_mode: ""
    actual_payoff_chapter: null
    aftermath_required: []
    overdue_risk: ""
```

## `04_story/character_arcs.yaml`

```yaml
arcs:
  - id: "ARC-001"
    character: ""
    starting_stance: ""
    want: ""
    need: ""
    misbelief: ""
    pressure_points: []
    planned_tests: []
    choices: []
    costs: []
    turning_points: []
    current_stage: ""
    end_state_range: ""
```

## `08_memory/deltas/chapter_0001.json`

```json
{
  "schema_version": 1,
  "chapter": 1,
  "canon_through_chapter": 1,
  "summary": "",
  "events": [],
  "state_changes": [],
  "knowledge_changes": [],
  "object_changes": [],
  "relationship_changes": [],
  "timeline_changes": [],
  "plotline_changes": [],
  "promise_changes": [],
  "file_updates": [
    {"path": "03_characters/states/example.yaml", "content": "...complete new file content..."}
  ],
  "confirmed_current": [],
  "blocking_risks": [],
  "updated_at": ""
}
```

## `07_summaries/chapter_0001_summary.md`

```markdown
# Chapter 0001 Summary

## Events

## Major Character Actions

## New Information

## Relationship Changes

## Plotline Progress

## New Foreshadowing

## Advanced Foreshadowing

## Resolved Questions

## State Updates Needed
```

## `07_summaries/chapter_0001_short.md`

```markdown
用 50 至 100 字记录本章核心事件、状态变化和钩子，供下一章快速加载。
```

## `03_characters/states/<character_slug>.yaml`

```yaml
name: ""
location: ""
current_goal: ""
mental_state: ""
physical_state: ""
abilities: []
knowledge:
  knows: []
  does_not_know: []
relationships: []
injuries_or_special_status: []
last_seen_chapter: 0
updated_at: ""
```

## `03_characters/relationships.yaml`

```yaml
relationships:
  - id: ""
    character_a: ""
    character_b: ""
    current_relationship: ""
    true_relationship: ""
    history: []
    hidden_relationship: false
    changed_in_chapters: []
    future_planned_changes: []
```

## `04_story/plotlines.yaml`

```yaml
plotlines:
  - id: "PL-001"
    name: ""
    type: "main"
    created_chapter: 0
    current_status: ""
    known_information: []
    related_characters: []
    next_step: ""
    expected_resolution_chapter: null
    completed: false
```

## `04_story/foreshadowing.yaml`

```yaml
foreshadowing:
  - id: "FS-001"
    content: ""
    planted_chapter: 0
    related_characters: []
    importance: "medium"
    status: "planted"
    planned_progress_chapters: []
    expected_payoff_chapter: null
    actual_payoff_chapter: null
    notes: ""
```

Allowed status values: `planted`, `advancing`, `resolved`, `abandoned`.

## `04_story/timeline.yaml`

```yaml
time_baseline:
  label: "story_day_0"
  description: ""
events:
  - id: "TL-001"
    chapter: 1
    day_index: 0
    night_index: 0
    story_date: ""
    event_time: ""
    order: 1
    event: ""
    relative_to_previous: ""
    anchor_event: ""
    characters: []
    character_ages: {}
    season: ""
    travel_time: ""
    major: false
    notes: ""
```

## Character Profile Markdown

```markdown
# Character Name

## Identity
- Name:
- Aliases:
- Role:
- Age:
- Appearance:

## Psychology
- Personality:
- Strengths:
- Flaws:
- Desire:
- Fear:
- Secret:
- Core goal:

## Capabilities
- Abilities:
- Weaknesses:

## Background

## Character Arc

## Current Canon Notes

## Relationships

## Important Events
```
