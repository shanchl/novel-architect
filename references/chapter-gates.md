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
- The chapter's new-information inventory.

If a chapter opens immediately after the previous chapter, treat the opening as "next second" continuity unless the text explicitly establishes a time jump.

Mechanical check:

- Read the previous chapter's `continuity_post_chapter_####.md`, `08_memory/scene_clock.yaml`, and the previous chapter manuscript ending before drafting.
- Compare the previous ending against the new opening for time, location, character presence, unresolved actions, available objects, and known facts.
- If the project uses relative time expressions, derive them from `day_index` and `night_index` fields in `scene_clock.yaml` or `04_story/timeline.yaml`; do not calculate from memory.
- Record any uncertain handoff in the pre-check file before prose work begins.

### New-Information Inventory

Every chapter must move the story forward. Before drafting, list the facts, turns, discoveries, decisions, pressures, or state changes this chapter introduces. Most chapters should have 2-5; a short transition may have fewer, and a major reveal chapter may have more.

Label each item:

- `new`: not previously established; the chapter may develop it fully.
- `restated`: already established; the chapter may reference or advance it, but should not re-explain it at length.

Use this inventory to prevent padding. If an item labeled `restated` grows into a full paragraph that does not add evidence, complication, reversal, emotional consequence, or a changed character stance, cut or compress it.

High-risk cases:

- Opening recaps that re-derive the previous chapter's conclusion instead of starting from it.
- Word-count expansion that adds prose without adding facts.
- Revision passes that copy an earlier line into a later chapter instead of adding the missing link.
- A specialist repeating a method description when only the new result matters.

## Information Chain Gate

For every new fact used by a character, identify:

- The fact.
- Who knows it.
- When they learned it.
- The channel: witness, report, message, sensory evidence, inference, prior relationship, institutional access, or direct action.
- Whether the channel breaks a prior promise, cover-up, secrecy rule, witness silence, authority limit, or physical impossibility.

If the answer to "how did they know this?" is missing, the chapter is not ready.

Information carriers have limits. A report cannot contain failed attempts no one recorded. A witness statement cannot reveal what the witness did not see. A sensory trace can imply direction or state only within the project's established rules.

Mechanical check:

- For every new fact in the chapter plan or draft, search `08_memory/information_ledger.yaml`, relevant character states, and recent summaries for its first known source.
- If the fact is new, add or plan an information ledger entry with `known_by`, `source_channel`, `learned_at`, and `constraints`.
- For reports, messages, testimony, sensory traces, and institutional records, write one sentence explaining what that carrier can and cannot contain.
- Compare the channel against prior concealment, promises, secrecy, professional limits, and physical access.

## Logic Failure Policy

Treat these as blocking defects:

- A chapter starts with a completed event that has not had enough story time to occur.
- A character holds an object, report, sample, message, or authority they cannot yet have.
- A character knows a fact without a channel.
- A new fact breaks a prior seal, promise, concealment, or institutional constraint without explanation.
- Two time bases are conflated, such as event time versus discovery time, death time versus exposure time, or knowing someone versus formally allying with them.

Fix blocking defects before polishing prose.

## Repetition Gate

Repetition means a whole piece of information, deduction, scene function, or emotional beat is being delivered again. It is not merely a recurring word, tool, image, dialogue tag, or character motif.

Automated n-gram or repeated-sentence checks are triage, not verdicts. Treat them as prompts to inspect whether the repeated text repeats information without new function.

Usually acceptable:

- Dialogue tags and generic action verbs.
- Recurring physical, vocal, or sensory motifs used for characterization.
- Deliberate echoes of clues, titles, messages, or promises, when the review note marks them as intentional.
- A method or rule mentioned again because it now produces a different result.
- Proper nouns, project terms, recurring evidence names, institutional names, body motifs, and stable character gestures.
- A concise reminder needed for readability, if the current scene immediately uses it to create a new decision, conflict, or inference.

Must be fixed:

- The previous chapter's closing conclusion restated at the next chapter's opening.
- The same setting, trait, rule, nickname, or institution explained again without new pressure or new information.
- The same action description repeated within a chapter.
- A key line reproduced verbatim across chapters without a deliberate echo reason.
- A deduction walked again by another character when the conclusion is unchanged and the second pass adds no new evidence.
- A recap paragraph that could be deleted without changing the current scene's available choices, conflict, or reader understanding.

When a chapter is short, expand with new information, new observation, new obstacle, new consequence, or sharper scene pressure. Do not restate known information in different words to reach a word target.

Mechanical check:

- Run `scripts/check_chapter.py <project> --chapter N` after drafting or revision. Treat n-gram output as a review queue, not an automatic failure.
- For each repeated fragment in the generated gate report, classify it as `intentional_echo`, `term_or_name`, `motif`, `necessary_reminder`, or `needs_revision`.
- A repeated fragment marked `necessary_reminder` must immediately support a new decision, conflict, inference, or emotional turn in the same scene.
- If a repeated paragraph can be removed without changing available choices, conflict, or reader understanding, revise it.

## Cross-Chapter Callback Gate

Avoid references that require the reader to remember an earlier line exactly. If a later scene depends on earlier information, make the current scene self-contained:

- State the necessary fact in the current scene, then advance it.
- Let another character derive the same conclusion through their own evidence.
- Compress the callback into a clause instead of quoting the earlier scene.

Use "as I said before" or equivalent recall framing only when the act of recalling is itself character-relevant. A callback is acceptable when it changes meaning in the new scene, exposes a character's interpretation, or turns an old clue into new action.

## Canon Consistency Gate

Automated checks cannot catch these failures. Run this list manually before accepting a chapter:

- **Unintroduced labels:** a term, codename, number, case label, tool, institution, or shorthand appears as if established. Search `02_world/`, `03_characters/`, `04_story/`, `07_summaries/`, and `08_memory/`; if it has no antecedent, introduce it in context or make it self-explanatory.
- **Contradicted results:** an earlier chapter established a result, but the new chapter says it cannot be done or never happened. Search recent summaries and the information ledger for the earlier result; state why it was partial, insufficient, invalidated, or about a different question.
- **Capability leaks:** a newly introduced ability, tool, loophole, or procedure would have erased an existing clue or solved an earlier problem. Search earlier chapter summaries for places the capability would apply; add a limit, make the inconsistency a deduction, or change the capability.
- **Motivation leaks:** a character gives away information they would protect, or withholds information they should share, without a stated reason. Check the character's current goal, fear, relationship pressure, and known risks in their state file.
- **Physical-process gaps:** an observable trace is attributed to an administrative, legal, magical, or procedural act that cannot physically create it. Check the applicable world rule or domain note; add the physical artifact or change the deduction.
- **Early reveal confirmation:** atmosphere or a casual line accidentally proves a mystery scheduled for later payoff. Compare the line against `04_story/foreshadowing.yaml`, plotlines, and planned reveals before finalizing.
- **Counting errors:** numbers in prose contradict the objects, days, people, words, clues, or steps they point at. Derive counts from timeline, scene clock, lists, or state files; do not trust memory.
- **Relative-time drift:** expressions such as yesterday, last night, two days ago, later that morning, and the next evening disagree across chapters. Convert both passages to `day_index` and `night_index` before rewriting prose.
- **Unspoken inference shared as knowledge:** one character builds on another character's interior deduction even though it was never spoken or otherwise transmitted. Check dialogue/action transmission before allowing the shared knowledge.
- **Specialist handling errors:** a professional character handles evidence, magic, tools, records, bodies, samples, or artifacts in a way that violates the project's established rules without cost. Compare the action to project rules and make the breach visible if intentional.
- **Terminology drift:** the same object, body part, method, institution, spell, technology, or role receives a new name without reason. Search all project memory and summaries; update terms or record an intentional alias.
- **Evidence-type mismatch:** a conclusion is credited to a method that cannot support it under project rules. Match the conclusion to the correct evidence stream and record the channel in the information ledger.
- **List inconsistency:** a character enumerates a set of clues, staged items, suspects, causes, costs, or steps, then another passage repeats the set with a different item count or a mismatched member. Check that every listed item belongs to the claimed category.
- **Identity-marker collision:** a nickname, species trait, title, body mark, costume, or role is used to identify one character but also applies to another. Compare character profiles and aliases; use an individual difference or explain why the context singles out one person.
- **False contradiction:** two accounts of the same fact may differ because of speaker role, self-interest, audience, or deliberate concealment. Treat as a contradiction only after checking whether both can coexist in character.

For project-specific hard gates, create or update `10_review/canon_gates_project.md` inside the novel project. Keep the skill generic; store genre, world, profession, species, magic, technology, and prose-voice specifics in the project.

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

## Summary Sync

A chapter edit that changes an established fact, term, setting rule, character state, reveal, object, or event is not complete until summaries and structured memory match it.

After such edits, search the project for the old wording or stale fact and update affected files in:

- `07_summaries/`
- `08_memory/`
- `10_review/`
- `03_characters/`
- `04_story/`
- `05_structure/`

Short summaries are high-risk because later chapters often load them instead of old manuscripts.

Only update `00_project/status.yaml` after the manuscript, summary, timeline, involved character states, and post-chapter gate have been checked.

## Gate Report

After drafting, revising, or running a chapter check, write the current deterministic and manual review state to `10_review/gate_chapter_####.md`.

The report should include:

- Deterministic script results.
- Time handoff status.
- Information-chain risks.
- Canon-consistency checklist results.
- Repetition triage and decisions.
- Summary/state/timeline sync status.
- Remaining blocking risks.

The report is the durable review artifact. A terminal exit code alone is not enough for long-form work.
