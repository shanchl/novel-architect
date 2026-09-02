# Workflows

The user may use explicit commands or plain language. Treat natural-language requests as the closest command.

## Command Map

`/novel create`

- Extract title, genre, length, chapter size, chapter count, core idea, protagonist, audience, style, pace, romance intensity, suspense density, payoff density, and AI freedom.
- Create the project structure with `scripts/init_novel.py` when possible.
- Save normalized requirements in `00_project/requirements.md`.
- Save the raw request and inferred assumptions in `00_project/brief.md`.
- Initialize `00_project/status.yaml`.

`/novel plan`

- Generate or refine `01_concept/core.md`, `01_concept/synopsis.md`, `02_world/world_bible.md`, major character profiles and current states, relationships, master outline, first plotlines, foreshadowing seeds, and initial timeline.
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

- Write the next or requested chapter by following the chapter drafting workflow below.

`/novel continue`

- Determine the current chapter from `00_project/status.yaml`, recent summaries, and existing chapter files, then continue with `/novel write`.

`/novel summarize`

- Regenerate detailed and short summaries for a chapter. Update memory only after reconciling with existing canon.

`/novel check`

- Run continuity checks across selected files. For ultra-long projects, start from structured memory and report coverage explicitly: status, novel bible, permanent memory, chapter table of contents, all active character states, all relationship entries, full timeline, all active plotlines, all unresolved foreshadowing, all state snapshots, and recent 3-5 chapter summaries.
- For broad checks, include boundary chapters around every state snapshot, chapters where relationships changed, chapters where foreshadowing was planted or paid off, timeline gaps, and any chapters named by the user. Read full manuscripts only for implicated chapters, missing summaries, exact wording disputes, or high-severity contradictions.
- Each check report should state which files were inspected, which chapters were represented only by summaries or snapshots, what was not checked, and the residual risk.

`/novel review`

- Review chapter quality: scene purpose, pacing, voice, character motivation, tension, reveal control, style compliance, banned patterns, and ending hook.

`/novel revise`

- Revise a chapter or canon file. If canon changes, run change impact analysis first. If only prose changes, update summaries if meaning changes.
- For canon-changing revisions, archive affected canon files before editing, apply edits in dependency order, update summaries and state files, then append a change-log entry with timestamp, reason, files changed, affected chapters, and any unresolved follow-up work.

`/novel memory`

- Present the current context pack or long-term memory state. Do not dump unrelated full files.

`/novel status`

- Summarize current chapter, volume, word counts, open plotlines, due foreshadowing, active continuity risks, and next recommended action.

## Chapter Drafting Workflow

1. Determine the target chapter from the request, `status.yaml`, `chapter_toc.yaml`, and existing files.
2. Build a context pack using [memory-and-continuity.md](memory-and-continuity.md).
3. Generate a chapter writing plan with opening, scene list, central conflict, emotional progression, reveals, foreshadowing, climax, and ending hook.
4. Save pre-draft continuity notes in `10_review/continuity_pre_chapter_####.md` when working in files.
5. Draft the chapter from the chapter plan and writing rules.
6. Run quality and continuity checks.
7. Save the chapter manuscript in `06_chapters/chapter_####.md`.
8. Generate `07_summaries/chapter_####_summary.md` and `07_summaries/chapter_####_short.md`.
9. Update character states, timeline, plotlines, foreshadowing, open threads, and status.
10. Every 10 chapters, write a state snapshot in `08_memory/state_snapshots/`.

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
