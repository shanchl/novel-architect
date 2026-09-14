# State Transactions and Freshness

Use this reference after chapter drafting, after canon-changing revision, when accepting a chapter, or when migrating an older project.

## Authority Order

When sources disagree, resolve them in this order unless the project explicitly declares another authority:

1. Accepted chapter text and explicitly locked user decisions.
2. Applied chapter deltas and the state event ledger.
3. Current structured state: character states, timeline, information ledger, plotlines, relationships, promises, and foreshadowing.
4. Derived summaries, snapshots, permanent memory, and novel bible.
5. Plans and outlines, which describe intent rather than completed canon.
6. Generated context packs and review reports, which are never canon.

Do not silently choose between contradictory tier-one sources. Record the conflict and ask only when the repair would materially change the story.

## Chapter Delta

Write `08_memory/deltas/chapter_####.json` once the manuscript is stable. It is the transaction manifest for changes caused by the chapter, including:

- events and state changes
- knowledge and object movement
- relationship, timeline, plotline, and reader-promise changes
- complete contents for derived files that must be replaced in `file_updates`
- unchanged required views explicitly rechecked in `confirmed_current`
- blocking risks, which must be empty before apply

Generate a starter with:

```bash
python scripts/apply_chapter_delta.py <project> --chapter N --write-template
```

Validate with the default dry-run, inspect the target list, then apply only when the chapter and derived views are ready:

```bash
python scripts/apply_chapter_delta.py <project> --chapter N
python scripts/apply_chapter_delta.py <project> --chapter N --apply
```

The apply operation validates project-contained paths, stages replacement content, archives overwritten files, updates the append-only state event log and freshness registry, and advances project status last. If replacement fails, it restores files already replaced.

Applying the identical delta twice is an idempotent no-op. A different delta for an already applied chapter is blocked; use the canon-revision workflow so the later change has its own impact analysis and archive trail.

## Freshness

`08_memory/freshness.json` records, for each checked or updated derived file:

- canon chapter covered
- source delta
- content hash
- update timestamp

An existing file is not necessarily current. The `accept` gate requires the current chapter's summary, short summary, timeline, scene clock, and information ledger to be fresh through that chapter.

## Migration

New projects use project schema `1.3.0`. For an older project, preview the additive migration before applying it:

```bash
python scripts/migrate_project.py <project>
python scripts/migrate_project.py <project> --apply
```

Migration creates only missing 1.3 files, including the empty occurrence-scoped repetition registry, adds the schema marker to project status, initializes canon coverage from `last_completed_chapter`, and archives the previous status file. It does not rewrite existing canon, convert a legacy repetition watchlist automatically, or infer narrative-engine content.
