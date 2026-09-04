# Schemas and Templates

These shapes are recommendations, not a rigid database. Preserve useful existing project formats when updating an established novel.

## `00_project/status.yaml`

```yaml
title: ""
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
chapters:
  - chapter: 1
    opening_time: ""
    opening_location: ""
    ending_time: ""
    ending_location: ""
    elapsed_time: ""
    unresolved_immediate_actions: []
    next_chapter_handoff: ""
```

## `10_review/continuity_pre_chapter_0001.md`

```markdown
# Continuity Pre-Check · Chapter 0001

## Time Handoff

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
    conflict: ""
    emotional_shift: ""
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
events:
  - id: "TL-001"
    chapter: 1
    story_date: ""
    event_time: ""
    order: 1
    event: ""
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
