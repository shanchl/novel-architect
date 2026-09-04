# Novel Architect

[English](#english) | [简体中文](#简体中文)

Version: `1.0.0`

## English

`novel-architect` is a Codex skill for project-managed long-form fiction creation. It is designed for medium, long, serial, and ultra-long novels where continuity, structured memory, character state, foreshadowing, timeline, and style control matter more than simply generating the next block of prose.

### What It Does

- Creates one isolated project directory per novel.
- Maintains a novel bible, requirements, concept notes, worldbuilding, characters, relationships, outlines, plotlines, foreshadowing, timeline, chapter plans, manuscripts, summaries, long-term memory, writing rules, reviews, and change logs.
- Builds focused context packs instead of loading the entire manuscript.
- Checks continuity before and after chapter drafting.
- Enforces chapter-start gates for time handoff, information chain, domain/canon constraints, and project-specific style.
- Updates summaries, character states, plotlines, foreshadowing, timeline, and project status after each chapter.
- Supports change impact analysis before modifying established canon.
- Supports anti-AI writing-pattern checks through forbidden phrases, rhythm checks, cliche detection, repeated reaction beats, and voice consistency review.

### Directory Layout

Each novel should live in its own directory:

```text
novels/
└── novel_slug/
    ├── 00_project/
    ├── 01_concept/
    ├── 02_world/
    ├── 03_characters/
    ├── 04_story/
    ├── 05_structure/
    ├── 06_chapters/
    ├── 07_summaries/
    ├── 08_memory/
    ├── 09_writing/
    ├── 10_review/
    └── 99_archive/
```

See `references/project-structure.md` for the full file ownership model.

### Commands

The skill recognizes these workflows, whether the user types the command directly or describes the task naturally:

- `/novel create`
- `/novel plan`
- `/novel bible`
- `/novel outline`
- `/novel toc`
- `/novel chapter plan`
- `/novel write`
- `/novel continue`
- `/novel summarize`
- `/novel check`
- `/novel review`
- `/novel revise`
- `/novel memory`
- `/novel status`

See `references/workflows.md` for the detailed command behavior.

### Initialize A Novel Project

Use the helper script to create a new novel skeleton:

```bash
python D:\skills\novel-architect\scripts\init_novel.py "The Clockwork Sea" --root novels --genre "steampunk fantasy" --target-total-words 300000 --target-chapter-words 2500
```

Useful options:

```bash
--brief "An amnesiac engineer investigates the truth behind a lighthouse in an underwater city"
--protagonist "Lin Yan, former deep-sea structural engineer"
--target-readers "Readers who enjoy high-concept mystery"
--style "restrained, cinematic, tense"
--pace "medium-fast"
--romance-intensity "low"
--suspense-density "high"
--payoff-density "medium-high"
--ai-freedom "medium"
--dry-run
```

`--dry-run` prints the target path without creating files. The script rejects negative counts, refuses to create directly under a filesystem root, and normalizes unsafe slugs. Chinese titles are transliterated into pinyin slugs when possible, for example `归墟灯塔` becomes `gui-xu-deng-ta`.

### Core References

- `SKILL.md`: entrypoint and routing rules.
- `references/project-structure.md`: canonical novel project layout.
- `references/workflows.md`: `/novel` workflows, versioning, and change impact analysis.
- `references/chapter-gates.md`: chapter-start gates, information chains, and blocking review order.
- `references/memory-and-continuity.md`: memory layers, context packs, continuity checks, and post-chapter updates.
- `references/domain-checks.md`: project-specific domain and terminology checks.
- `references/writing-control.md`: style control, anti-AI pattern checks, and quality review.
- `references/schemas.md`: suggested YAML and Markdown templates.

### Validation

Validate the skill structure with:

```bash
python C:\Users\chang\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\skills\novel-architect
```

The current version has been checked with `quick_validate.py`, script syntax checks, initialization tests, edge-case slug tests, negative-input rejection tests, dry-run tests, and an independent review pass.

## 简体中文

`novel-architect` 是一个用于中长篇、长篇、连载小说和超长篇小说创作的 Codex skill。它的重点不是简单续写正文，而是用工程化方式维护小说设定、长期记忆、人物状态、伏笔、时间线、章节计划和写作风格，尽量避免长篇创作后期常见的人物混乱、剧情矛盾、伏笔遗忘和世界观不一致。

### 能力范围

- 为每部小说创建独立项目目录。
- 维护小说圣经、需求、核心概念、世界观、人物、人物关系、大纲、剧情线、伏笔、时间线、章节计划、章节正文、章节摘要、长期记忆、写作规则、审查结果和修改记录。
- 构建精简的章节上下文包，而不是直接加载整部小说正文。
- 在章节写作前后执行连续性检查。
- 写章前执行时间衔接、信息链、项目设定和项目文风门禁。
- 每章完成后更新摘要、人物状态、剧情线、伏笔、时间线和项目状态。
- 在修改既定设定前执行修改影响分析。
- 支持去 AI 化写作检查，包括禁用词、句式节奏、套路表达、重复反应、角色口吻同质化等。

### 目录结构

每部小说应放在一个独立目录中：

```text
novels/
└── novel_slug/
    ├── 00_project/
    ├── 01_concept/
    ├── 02_world/
    ├── 03_characters/
    ├── 04_story/
    ├── 05_structure/
    ├── 06_chapters/
    ├── 07_summaries/
    ├── 08_memory/
    ├── 09_writing/
    ├── 10_review/
    └── 99_archive/
```

完整文件职责见 `references/project-structure.md`。

### 命令

skill 支持以下工作流。用户可以直接输入命令，也可以用自然语言描述相同需求：

- `/novel create`
- `/novel plan`
- `/novel bible`
- `/novel outline`
- `/novel toc`
- `/novel chapter plan`
- `/novel write`
- `/novel continue`
- `/novel summarize`
- `/novel check`
- `/novel review`
- `/novel revise`
- `/novel memory`
- `/novel status`

详细命令行为见 `references/workflows.md`。

### 初始化小说项目

使用辅助脚本创建新的小说工程骨架：

```bash
python D:\skills\novel-architect\scripts\init_novel.py "归墟灯塔" --root novels --genre "科幻悬疑" --target-total-words 600000 --target-chapter-words 3200
```

常用参数：

```bash
--brief "失忆工程师在海底城市追查一座灯塔的真相"
--protagonist "林砚，前深海结构工程师"
--target-readers "喜欢强设定悬疑的读者"
--style "冷峻、克制、有画面感"
--pace "中快"
--romance-intensity "低"
--suspense-density "高"
--payoff-density "中高"
--ai-freedom "中"
--dry-run
```

`--dry-run` 只打印目标路径，不创建文件。脚本会拒绝负数字数和负章节数，拒绝直接在磁盘根目录创建项目，并会清洗不安全的 slug。中文标题会尽量转写为拼音 slug，例如 `归墟灯塔` 会生成 `gui-xu-deng-ta`。

### 核心参考文档

- `SKILL.md`：skill 入口和路由规则。
- `references/project-structure.md`：小说项目标准目录结构。
- `references/workflows.md`：`/novel` 工作流、版本归档和修改影响分析。
- `references/chapter-gates.md`：章节开头门禁、信息链和阻断式检查顺序。
- `references/memory-and-continuity.md`：记忆层级、上下文包、连续性检查和章后更新。
- `references/domain-checks.md`：项目内设定、术语、计量和专业流程检查。
- `references/writing-control.md`：写作风格控制、去 AI 化模式检查和质量审查。
- `references/schemas.md`：推荐的 YAML 和 Markdown 模板。

### 验证

使用以下命令验证 skill 结构：

```bash
python C:\Users\chang\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\skills\novel-architect
```

当前版本已通过 `quick_validate.py`、脚本语法检查、初始化测试、异常 slug 测试、负数输入拒绝测试、dry-run 测试和独立评审复查。
