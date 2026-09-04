# Chapter Gates

Use these gates before drafting, revising, or accepting a chapter in an established long-form novel project.

The check order is mandatory because logic failures invalidate prose fixes:

1. Cross-chapter time handoff.
2. Information chain.
3. Domain and canon constraints.
4. Repetition, diction, and project-specific style.

Do not skip the first two gates because the current chapter reads well in isolation.

## Chapter Start Gate

Before writing a new chapter, create or update `10_review/continuity_pre_chapter_####.md`.

It must state:

- Previous chapter ending time and location.
- New chapter opening time and location.
- Whether the opening is immediate, delayed, or a flashback.
- Every involved character's current location.
- What each involved character currently knows.
- What each involved character currently possesses or can access.
- Which events have not happened yet and therefore cannot be referenced as completed.
- Any object, report, message, witness, body, sample, authority, or conclusion that would be impossible at this moment.

If a chapter opens immediately after the previous chapter, treat the opening as "next second" continuity unless the text explicitly establishes a time jump.

## Information Chain Gate

For every new fact used by a character, identify:

- The fact.
- Who knows it.
- When they learned it.
- The channel: witness, report, message, sensory evidence, inference, prior relationship, institutional access, or direct action.
- Whether the channel breaks a prior promise, cover-up, secrecy rule, witness silence, authority limit, or physical impossibility.

If the answer to "how did they know this?" is missing, the chapter is not ready.

Information carriers have limits. A report cannot contain failed attempts no one recorded. A witness statement cannot reveal what the witness did not see. A sensory trace can imply direction or state only within the project's established rules.

## Logic Failure Policy

Treat these as blocking defects:

- A chapter starts with a completed event that has not had enough story time to occur.
- A character holds an object, report, sample, message, or authority they cannot yet have.
- A character knows a fact without a channel.
- A new fact breaks a prior seal, promise, concealment, or institutional constraint without explanation.
- Two time bases are conflated, such as event time versus discovery time, death time versus exposure time, or knowing someone versus formally allying with them.

Fix blocking defects before polishing prose.

## Post-Chapter Gate

After drafting or revising, create or update `10_review/continuity_post_chapter_####.md`.

It must state:

- Final chapter ending time, location, and hook.
- New facts introduced.
- Facts revealed to each character.
- Objects or evidence gained, lost, moved, registered, or concealed.
- Character state changes.
- Timeline updates needed.
- Summary updates needed.
- Open contradictions or residual risks.

Only update `00_project/status.yaml` after the manuscript, summary, timeline, involved character states, and post-chapter gate have been checked.
