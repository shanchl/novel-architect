---
name: novel-architect
description: Manage long-form novel projects with isolated story bibles, structured memory, outlines, chapter plans, drafting, summaries, continuity checks, and change impact analysis. Use for novella, serial, long novel, or million-word fiction workflows, not for one-off short prose.
metadata:
  short-description: Long-form novel engineering and memory
  version: 1.0.0
---

# Novel Architect

Use this skill when the user wants to create, plan, continue, revise, audit, or maintain a medium, long, or ultra-long novel. Treat each novel as an isolated project with its own files, memory, style rules, and state. Never mix settings, characters, summaries, or prompts between novels.

This skill's core job is continuity and project control, not merely prose generation. Maintain a novel bible, structured long-term memory, chapter plans, summaries, character state, plotlines, foreshadowing, timeline, writing rules, review results, and change logs.

## Skill Version

Current version: `1.0.0`.

When changing this skill's instruction files, references, scripts, or default project skeletons, increment the patch version before finishing the edit unless the user explicitly requests a different semantic-version bump. Keep `VERSION`, this frontmatter metadata, and `README.md` aligned.

## First Decisions

- If the user provides a novel project path, use that path.
- If they provide only a title or idea, create or update a project under a `novels/<novel_slug>/` workspace unless they choose another location.
- If they invoke a `/novel ...` command, map it to the matching workflow in [references/workflows.md](references/workflows.md).
- If the request involves creating a new novel directory, prefer running `scripts/init_novel.py`.
- If information is missing, infer a reasonable draft plan and flag assumptions instead of forcing the user through a form.
- Use the user's language for plans, prose, summaries, and review notes unless they request another language.
- Keep the skill generic for long-form novel work. Do not encode a specific novel title, premise, genre, species system, forensic method, magic system, technology tree, or prose voice into the skill itself; store those constraints inside the individual novel project.

## Operating Rules

- Load only the current novel's files. Do not import details from other novel directories unless the user explicitly asks for crossover or migration.
- Do not load an entire novel manuscript as context. Build a focused context pack from the bible, relevant state files, current plan, and recent summaries.
- Before writing or revising a chapter, run the chapter gates: cross-chapter time handoff first, information chain second, domain/canon constraints third, prose/style checks last.
- After finishing a chapter, update summaries, character state, timeline, plotlines, foreshadowing, project status, and review files.
- When changing established canon, run change impact analysis before editing dependent files.
- Preserve prior versions of important canon files in `99_archive/` or record enough change history to explain what changed, why, and what was affected.
- Treat de-AI writing control as project-specific style enforcement. Load and obey the current novel's `09_writing/style.md`, `writing_rules.md`, `forbidden_patterns.md`, `vocabulary.md`, and `prompts.md`; do not substitute a generic prose style.

## References

Read only the references needed for the current task:

- For directory layout and file ownership, read [references/project-structure.md](references/project-structure.md).
- For `/novel` commands and end-to-end procedures, read [references/workflows.md](references/workflows.md).
- For chapter-start gates, information chains, and write/revise blocking checks, read [references/chapter-gates.md](references/chapter-gates.md).
- For context packs, memory layers, continuity checks, and post-chapter updates, read [references/memory-and-continuity.md](references/memory-and-continuity.md).
- For project-specific domain constraints such as technical systems, procedural evidence, terminology, measurements, or nonhuman embodiment, read [references/domain-checks.md](references/domain-checks.md).
- For prose style, anti-AI-pattern controls, chapter quality review, and revision rules, read [references/writing-control.md](references/writing-control.md).
- For recommended JSON/YAML shapes and Markdown templates, read [references/schemas.md](references/schemas.md).
