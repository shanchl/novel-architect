# Narrative Engine

Continuity prevents breakage; the narrative engine preserves reader momentum. Use this reference for concept work, outlining, chapter planning, developmental review, and structural revision. Do not force every field onto experimental fiction; keep only the controls that serve the project's creative contract.

## Creative Contract

`01_concept/creative_contract.md` records the experience the user wants to create and the decisions the assistant may make. Establish:

- Reader promise: why the intended reader should continue.
- Genre experience: expected pleasures and any deliberate departures.
- Emotional destination: how the ending should feel, without requiring a fixed plot solution.
- Authorship boundaries: AI freedom, locked decisions, and suggest-only areas.
- Non-negotiables and material to avoid.

When a proposed improvement conflicts with this contract, present it as an option rather than silently applying it.

## Story Engine

`04_story/story_engine.yaml` defines what repeatedly generates consequential action:

- central dramatic question
- protagonist want, need, misbelief, fear, and moral line
- external, internal, and relational stakes
- escalation ladder
- irreversible choices already made or planned
- climax preconditions

A story engine is not a synopsis. It explains why pressure keeps producing new choices. Revisit it when several consecutive chapters depend on coincidence, passive observation, or interchangeable obstacles.

## Scene Causality

Each substantial scene should answer enough of these questions to prove its function:

- What does the viewpoint character want now?
- What actively resists that objective?
- What new fact, action, or reversal changes the available choices?
- What choice does the character make?
- What does the choice cost?
- Which value changes between scene entry and exit: safety, trust, knowledge, status, intimacy, freedom, hope, or another project-defined value?
- How does the outcome cause or constrain the next scene?
- Which reader question is opened, advanced, answered, or transformed?

Do not require a dramatic reversal in a quiet connective scene. Require a meaningful change or necessary setup whose later use is identified.

## Reader Promises and Payoffs

Use `04_story/reader_promises.yaml` for mysteries, emotional promises, relationship expectations, ability or progression promises, announced goals, and thematic questions. A promise entry should track:

- ID, type, promise, and importance.
- What the reader currently knows and expects.
- Supporting clues or preparation already delivered.
- Legitimate misdirection and its basis.
- Prerequisites for a fair payoff.
- Target window, current status, and overdue risk.
- Payoff mode: confirmation, reversal, escalation, partial payoff, or transformation.
- Aftermath that must affect later choices or state.

Foreshadowing is evidence or preparation; a reader promise is the expectation created by the text. Link them by ID when they overlap, but do not merge them blindly.

## Character Arcs and Agency

Use `04_story/character_arcs.yaml` for major arcs. Track the character's starting stance, want, need, misbelief, pressure points, planned tests, choices, costs, turning points, and end-state range.

At chapter review, ask whether major characters caused meaningful change, resisted pressure in character-specific ways, or updated their stance. A character may deliberately fail to change; record the reinforced misbelief or increased cost rather than inventing progress.

## Pacing Ledger

Use `04_story/pacing_ledger.yaml` as a diagnostic view, not a formula. Record per chapter:

- conflict pressure
- information gain
- emotional intensity
- relationship movement
- promise setup and payoff
- irreversible change
- dominant scene mode

Inspect runs of chapters, not isolated scores. Flag prolonged flatness, identical hook types, repeated scene modes, unrelieved escalation, or payoff drought. Vary rhythm according to the creative contract instead of maximizing every dimension.

## POV and Voice

Use `09_writing/pov_voices.yaml` to record each viewpoint's knowledge boundary, attention bias, diction, metaphor sources, avoidance patterns, narrative distance, and voice exceptions. POV review should detect knowledge leaks and interchangeable narration while preserving intentional stylistic convergence.
