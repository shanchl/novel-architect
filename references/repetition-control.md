# Repetition Control

Use this reference when drafting, revising, auditing, or accepting chapters in a novel long enough for earlier wording, explanations, deductions, and scene patterns to recur.

## What Counts as Repetition

Control three different layers. Passing one layer does not imply that the others pass.

1. **Verbatim reuse**: the same sentence or substantial character sequence appears again.
2. **Information reuse**: an established fact, explanation, deduction, or recap is delivered again with different wording but no changed interpretation or consequence.
3. **Functional reuse**: a scene repeats an earlier interrogation shape, entrance, reaction beat, gesture sequence, emotional turn, hook, or resolution without creating a materially different effect.

Recurring names, terms, dialogue tags, character gestures, sensory motifs, and clue echoes are not automatically defects. Judge what the passage does for the reader now.

## Deterministic Verbatim Scan

For the current chapter, run:

```bash
python scripts/scan_repetition.py <project> --chapter N --against all --format markdown
```

For a one-time baseline audit, run:

```bash
python scripts/scan_repetition.py <project> --all --format markdown --output <report-path>
```

The scanner normalizes whitespace, finds shared seeds, restores maximal or near-contiguous matches to original source positions, and reports full context. It compares a new chapter with every existing chapter by default. The default levels are:

- `P1`: at least 24 normalized characters; prioritize review.
- `P2`: at least 14 normalized characters.
- 10–13 characters: report only for adjacent chapters or a phrase occurring in at least three chapters.

These are review priorities, not automatic prose failures. Adjust thresholds only when a project's language or chapter form demonstrates a persistent precision problem.

## Semantic and Functional Audit

Mechanical matching cannot detect paraphrased repetition. Compare the draft against the recent detailed summaries, the information ledger, the pacing ledger, the current case or volume plan, and relevant earlier summaries.

For each substantial paragraph or scene, ask:

- Is this fact, rule, setting explanation, deduction, or emotional conclusion already available to the reader?
- If it is repeated, what has changed: evidence, interpretation, speaker interest, audience, decision, conflict, cost, relationship, or state?
- Does a second character truly add an independent inference, or merely walk the reader through the same reasoning again?
- Is an opening re-establishing only the minimum needed fact, or replaying the previous chapter's ending?
- Have the same arrival, interview, refusal, sensory sweep, stunned reaction, or hook mechanics appeared recently?
- If the passage were removed, would any current choice, conflict, inference, emotional turn, or reader understanding change?

If the last answer is no, compress or remove the passage. Do not repair semantic repetition by swapping synonyms while preserving the same delivery. Add a new observation, obstacle, consequence, decision, cost, interpretation, relationship shift, or sharper pressure instead.

## Classifications

Every reported candidate must receive exactly one classification in the gate report:

- `intentional_echo`: exact recurrence is itself meaningful and the new context changes or deepens it.
- `term_or_name`: the overlap is terminology or naming, not repeated delivery.
- `motif`: a controlled recurring image, gesture, sound, or phrase used for characterization or structure.
- `necessary_reminder`: the minimum reminder immediately enables a new decision, conflict, inference, or emotional turn.
- `needs_revision`: the passage repeats wording, information, or function without sufficient new work.

The resolution line must use this form so the accept gate can verify it:

```markdown
- [x] REP-012345abcdef: motif — Fixed water-system sound; this occurrence marks the return to the laboratory.
```

## Occurrence-Scoped Approval Registry

Store durable approvals in `09_writing/repetition_registry.json`. Approve concrete text in concrete chapters, not short substrings globally.

```json
{
  "schema_version": 1,
  "entries": [
    {
      "id": "echo-water-system",
      "text": "Water moved inside the wall: drip, drip, drip.",
      "category": "motif",
      "chapters": [11, 12, 18],
      "reason": "Established laboratory sound motif"
    }
  ]
}
```

Valid approval categories are `intentional_echo`, `term_or_name`, `motif`, and `necessary_reminder`. Never approve `needs_revision`. The scanner suppresses only the registered text for a registered chapter pair. A longer repeated passage that contains an approved motif must still be reported.

`repetition_watchlist.md` may remain as human-readable review history in an older project, but automated checks must not treat every Markdown bullet as a global substring whitelist. Migrate only decisions that still matter into occurrence-scoped registry entries.

## Acceptance

`check_chapter.py --stage draft|post` adds unresolved verbatim candidates to the gate report. Before `--stage accept`:

1. Repair every `needs_revision` passage and rerun the scan.
2. Complete the semantic and functional novelty checklist.
3. Give every remaining `REP-*` item a checked classification and concrete reason.
4. Add only durable, intentional recurrences to the registry; do not use it to make a noisy report disappear.

The accept gate blocks unresolved candidate IDs and unchecked novelty review items. A clean mechanical scan still requires the semantic and functional audit.
