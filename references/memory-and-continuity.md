# Memory and Continuity

Long novels require deliberate context loading. The goal is to carry stable canon forward without loading the entire manuscript.

## Memory Layers

Permanent memory, loaded for every planning, drafting, and continuity task:

- `01_concept/creative_contract.md`
- `01_concept/core.md`
- `01_concept/synopsis.md` when concise enough, otherwise relevant sections only
- `04_story/master_outline.md`
- `04_story/story_engine.yaml`
- `08_memory/novel_bible.md` when it exists and is current
- `08_memory/permanent.md`
- protagonist profile and state
- hard world rules from `02_world/rules.yaml`
- current project status

Structured long-term memory, loaded as needed:

- relevant character profiles and current states
- relationships involving current characters
- relevant world bible sections and terms
- timeline entries near the current chapter
- active plotlines
- active or due reader promises
- relevant character arcs
- foreshadowing entries due soon or touched by the chapter
- state snapshots near the current chapter

Short-term memory, prioritized for drafting:

- current chapter plan
- current volume outline
- previous 3-5 chapter summaries
- current unresolved threads
- current character states for involved characters
- current information ledger and scene clock when they exist
- current POV and character-voice constraints

## Context Pack

For each chapter, assemble a compact context pack containing:

- story identity: title, genre, target reader, current volume, current chapter, and authorship boundaries
- non-negotiable canon: premise, theme, core conflict, world hard rules
- active cast: role, current location, goal, knowledge, emotional state, relationship state
- recent events: previous 3-5 chapter short summaries, plus detailed summaries when needed
- immediate handoff: the full manuscripts of the previous two chapters when drafting or revising a new chapter; always load both in full so opening time/location, voice, and unresolved scene momentum are protected
- chapter mandate: chapter goal, events, conflict, reveal, foreshadowing, hook, target word count
- continuity watchlist: due plotlines, reader promises, due foreshadowing, character-arc pressure, timeline constraints, forbidden outcomes
- style pack: relevant writing rules, banned phrases, character voice notes

Avoid older raw manuscript loading unless checking exact wording, revising a specific passage, or summarizing a chapter that lacks a summary. The previous two chapters are the standing exception for ordinary drafting and revision. Reduce that number only when an explicit context budget requires it and record the omission.

Use a character budget and report every missing, truncated, or omitted source. Never load all historical summaries or all character states merely because they exist. Select recent summaries and retrieve older material through character names, plotline IDs, promise IDs, foreshadowing IDs, timeline windows, or terms present in the chapter plan.

In local projects, prefer the deterministic helper:

```bash
python scripts/context_pack.py <project> --chapter N
```

It writes `10_review/context_pack_chapter_####.md` by default. It includes the creative contract, story engine, novel bible, current outline context, previous manuscripts, recent summaries, selected state, active narrative threads, continuity records, and writing controls within a declared budget. Use `--characters`, `--recent-summaries`, and `--max-chars` when the automatic selection needs adjustment; `--all-character-states` is an explicit exceptional mode.

## Pre-Draft Continuity Check

Before drafting, follow `chapter-gates.md` and check logic before prose:

- Chapter handoff: previous chapter ending time/location and new chapter opening time/location match or explicitly jump.
- Character location: every involved character can plausibly appear in the planned scene.
- Character knowledge: no one acts on information they have not learned.
- Character possessions/access: no one holds an object, report, sample, message, body, authority, or conclusion they cannot yet possess.
- Information chain: every new fact has a source channel and does not break earlier secrecy, promises, or institutional limits.
- Character motivation: actions follow goals, fear, relationship pressure, or a clearly introduced trigger.
- Timeline: event order, dates, age, season, travel time, and recovery time are plausible.
- World rules: abilities, technology, institutions, and terminology follow established limits.
- Plot discipline: the chapter does not solve later key conflicts too early.
- Foreshadowing: due setup is advanced or intentionally delayed with a reason.

Record risks and decisions in the pre-chapter review file when working in a project directory.

## Post-Chapter Updates

After a chapter is saved, update:

- Detailed summary: events, actions, new information, relationship changes, plot movement, new/progressed/resolved foreshadowing, solved problems.
- Short summary: 50-100 Chinese characters or an equivalent concise quick-load summary.
- Character states: location, current goal, mental state, ability changes, knowledge, relationships, injuries, special status.
- Timeline: chapter date/time, event order, season, travel, major events.
- Plotlines: status, known information, next step, estimated resolution, completion.
- Foreshadowing: new planted items, progressed items, resolved items, abandoned items with reason.
- Open threads: unresolved promises, mysteries, conflicts, and reader expectations.
- Information ledger: who learned what, when, by what channel, and what remains unknown.
- Scene clock: chapter end time/location and any delayed consequences.
- Project status: last written chapter, total words when known, next recommended step.
- Pacing ledger: pressure, information gain, emotional movement, payoff activity, irreversible change, and scene mode.
- Freshness registry: update through the applied chapter delta rather than by hand.

## Continuity Report Shape

When reporting issues, group them by:

- Character consistency
- Time consistency
- World consistency
- Plot consistency
- Relationship consistency
- Foreshadowing and unresolved threads

For each issue include severity, evidence files, affected chapter or state entry, and a concrete repair option.
