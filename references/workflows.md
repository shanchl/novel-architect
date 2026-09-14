# Workflows

The user may use explicit commands or plain language. Treat natural-language requests as the closest command.

## Command Map

`/novel create`

- Extract title, genre, length, chapter size, chapter count, core idea, protagonist, audience, style, pace, romance intensity, suspense density, payoff density, and AI freedom.
- Create the project structure with `scripts/init_novel.py` when possible.
- Save normalized requirements in `00_project/requirements.md`.
- Save the raw request and inferred assumptions in `00_project/brief.md`.
- Initialize `00_project/status.yaml`.
- Establish `01_concept/creative_contract.md`, especially reader promise, authorship boundaries, locked decisions, and deliberate genre departures.

`/novel plan`

- Generate or refine the creative contract, core, synopsis, story engine, world bible, major character profiles and arcs, relationships, master outline, first plotlines, reader promises, foreshadowing seeds, and initial timeline.
- Ask questions only for decisions that would materially change the genre promise or user intent.

`/novel bible`

- Build or update `08_memory/novel_bible.md` as a coherent canon entrypoint from concept, world, characters, relationships, outline, plotlines, timeline, and writing style.
- Resolve contradictions explicitly, recording assumptions in `00_project/change_log.md`.

`/novel outline`

- Create or adjust the hierarchy: master outline -> volume outline -> phase outline -> chapter plan.
- Preserve existing canon unless the user requests a retcon; retcons require impact analysis.

`/novel toc`

- Generate `05_structure/chapter_toc.yaml`.
- Every chapter entry needs more than a title: goal, volume, main event, conflict, involved characters, reveal, foreshadowing, hook, and target word count.

`/novel chapter plan`

- Generate or update one `05_structure/chapter_plans/chapter_####.yaml`.
- Base it on the current outline, plotlines, due foreshadowing, timeline, and character states.

`/novel write`

- Write the next or requested chapter by following the chapter drafting workflow below. The chapter-start gates are blocking: time handoff and information chain must be coherent before prose drafting continues.

`/novel accept`

- Create and validate the chapter delta, apply it after review, then run `scripts/check_chapter.py <project> --chapter N --stage accept`.
- Acceptance advances project status only after required views are fresh and blocking risks are empty.

`/novel migrate`

- Preview `scripts/migrate_project.py <project>`, report its additive changes, and use `--apply` only when the user asked to migrate or update that project.

`/novel continue`

- Determine the current chapter from `00_project/status.yaml`, recent summaries, and existing chapter files, then continue with `/novel write`.

`/novel summarize`

- Regenerate detailed and short summaries for a chapter. Update memory only after reconciling with existing canon.

`/novel check`

- Run continuity checks across selected files. For ultra-long projects, start from structured memory and report coverage explicitly: status, novel bible, permanent memory, chapter table of contents, all active character states, all relationship entries, full timeline, all active plotlines, all unresolved foreshadowing, all state snapshots, and recent 3-5 chapter summaries.
- For broad checks, include boundary chapters around every state snapshot, chapters where relationships changed, chapters where foreshadowing was planted or paid off, timeline gaps, and any chapters named by the user. Read full manuscripts only for implicated chapters, missing summaries, exact wording disputes, or high-severity contradictions.
- Apply the gate order from `chapter-gates.md`: cross-chapter time, information chain, domain/canon constraints, narrative movement, then prose/style. Report logic and causal defects before wording defects.
- Each check report should state which files were inspected, which chapters were represented only by summaries or snapshots, what was not checked, and the residual risk.

`/novel review`

- Review chapter quality: scene causality, character agency and cost, value shifts, reader-promise movement, pacing, voice, motivation, tension, reveal control, style compliance, repeated phrasing, and ending hook. Use the creative contract and current project style as authority.

`/novel revise`

- Revise a chapter or canon file. If canon changes, run change impact analysis first. If only prose changes, update summaries if meaning changes.
- For canon-changing revisions, archive affected canon files before editing, apply edits in dependency order, update summaries and state files, then append a change-log entry with timestamp, reason, files changed, affected chapters, and any unresolved follow-up work.

`/novel memory`

- Present the current context pack or long-term memory state. Do not dump unrelated full files.

`/novel status`

- Summarize current chapter, volume, word counts, open plotlines, due foreshadowing, active continuity risks, and next recommended action.

## Chapter Drafting Workflow

1. Determine the target chapter from the request, `status.yaml`, `chapter_toc.yaml`, and existing files.
2. Build a relevance-bounded context pack using [memory-and-continuity.md](memory-and-continuity.md). In a local project, prefer `scripts/context_pack.py <project> --chapter N` and review its context audit for omissions or truncation.
3. Create or update `10_review/continuity_pre_chapter_####.md` using [chapter-gates.md](chapter-gates.md), then run the `pre` stage. It must prove the opening time, location, character knowledge, possessions, and information channels.
4. Generate a chapter writing plan using [narrative-engine.md](narrative-engine.md). Substantial scenes should identify objective, opposition, turn, choice, cost, value shift, causal handoff, and reader-question movement when those controls fit the project.
5. Draft the chapter from the chapter plan and the current project's `09_writing/` files.
6. Run quality, continuity, domain, repetition, and style checks. Use `scripts/check_chapter.py <project> --chapter N --stage draft`; it scans verbatim reuse against all existing chapters, writes `10_review/gate_chapter_####.md`, and leaves semantic novelty and continuity items explicit. Follow [repetition-control.md](repetition-control.md) rather than fixing repeated content through cosmetic synonym swaps.
7. Save the chapter manuscript in `06_chapters/chapter_####.md`.
8. Generate `07_summaries/chapter_####_summary.md` and `07_summaries/chapter_####_short.md`.
9. Prepare updated character states, timeline, plotlines, promises, foreshadowing, open threads, pacing ledger, and `10_review/continuity_post_chapter_####.md`; run the `post` gate.
10. Create `08_memory/deltas/chapter_####.json` as described in [state-transactions.md](state-transactions.md). Put complete derived-file replacements in `file_updates` and explicitly list rechecked unchanged required views in `confirmed_current`.
11. Dry-run `scripts/apply_chapter_delta.py <project> --chapter N`, inspect the target list, then apply it. The transaction archives replacements, records freshness, and advances status last.
12. Complete the manual checklist in `gate_chapter_####.md`, then run `scripts/check_chapter.py <project> --chapter N --stage accept`. Do not accept a chapter with unchecked review items, blocking results, or stale required views.
13. Write a state snapshot when either the project-defined interval is reached or a structural milestone occurs, such as a volume boundary, major reveal, irreversible identity or relationship change, or sustained location/time-period shift.

## Change Impact Analysis

Use when the user changes established canon, such as age, relationship, world rule, timeline event, power limits, secrets, or outline outcomes.

Produce an impact report covering:

- Directly affected canon files.
- Character profiles and states that must change.
- Relationship entries that must change.
- Chapter plans, manuscripts, and summaries likely affected.
- Timeline entries and age calculations affected.
- Plotlines, foreshadowing, and reveals affected.
- Recommended edit order.

Do not silently update only one file when dependent files remain inconsistent. If the user approves edits, archive important old versions first.

## Versioning Procedure

Before changing important canon files, copy the previous version under `99_archive/YYYYMMDD_HHMMSS/<relative_path>`. Important canon includes concept, synopsis, world rules, world bible, character profiles, character states, relationships, master outline, volume or phase outlines, chapter table of contents, chapter plans, plotlines, foreshadowing, timeline, permanent memory, and novel bible.

After the edit, append to `00_project/change_log.md`:

- timestamp
- user request or reason
- old file paths archived
- files changed
- affected chapters, summaries, plotlines, foreshadowing, timeline entries, and character states
- remaining risks or checks still needed

## Skill Versioning

When editing the skill itself, update the skill's semantic version before finishing:

- Patch bump for instruction, reference, script, or validation changes.
- Minor bump for new workflows, new project skeleton files, or backward-compatible capability additions.
- Major bump for incompatible project layout changes or changes that require migrating existing novels.

Keep `VERSION`, `SKILL.md` metadata, and `README.md` aligned.

Use `scripts/bump_version.py patch|minor|major` unless a different update is required. The script snapshots the previous skill files under `.version_backups/` before changing version numbers.
