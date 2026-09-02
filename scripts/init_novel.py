#!/usr/bin/env python3
"""Initialize an isolated long-form novel project directory."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

try:
    from pypinyin import lazy_pinyin
except ImportError:  # pragma: no cover - optional dependency
    lazy_pinyin = None


FOLDERS = [
    "00_project",
    "01_concept",
    "02_world",
    "03_characters/profiles",
    "03_characters/states",
    "04_story",
    "05_structure/volumes",
    "05_structure/phases",
    "05_structure/chapter_plans",
    "06_chapters/drafts",
    "07_summaries",
    "08_memory/state_snapshots",
    "09_writing",
    "10_review",
    "99_archive",
]


GB2312_PINYIN_RANGES = [
    (-20319, "a"), (-20317, "ai"), (-20304, "an"), (-20295, "ang"), (-20292, "ao"),
    (-20283, "ba"), (-20265, "bai"), (-20257, "ban"), (-20242, "bang"), (-20230, "bao"),
    (-20051, "bei"), (-20036, "ben"), (-20032, "beng"), (-20026, "bi"), (-20002, "bian"),
    (-19990, "biao"), (-19986, "bie"), (-19982, "bin"), (-19976, "bing"), (-19805, "bo"),
    (-19784, "bu"), (-19775, "ca"), (-19774, "cai"), (-19763, "can"), (-19756, "cang"),
    (-19751, "cao"), (-19746, "ce"), (-19741, "ceng"), (-19739, "cha"), (-19728, "chai"),
    (-19725, "chan"), (-19715, "chang"), (-19540, "chao"), (-19531, "che"), (-19525, "chen"),
    (-19515, "cheng"), (-19500, "chi"), (-19484, "chong"), (-19479, "chou"), (-19467, "chu"),
    (-19289, "chuai"), (-19288, "chuan"), (-19281, "chuang"), (-19275, "chui"),
    (-19270, "chun"), (-19263, "chuo"), (-19261, "ci"), (-19249, "cong"), (-19243, "cou"),
    (-19242, "cu"), (-19238, "cuan"), (-19235, "cui"), (-19227, "cun"), (-19224, "cuo"),
    (-19218, "da"), (-19212, "dai"), (-19038, "dan"), (-19023, "dang"), (-19018, "dao"),
    (-19006, "de"), (-19003, "deng"), (-18996, "di"), (-18977, "dian"), (-18961, "diao"),
    (-18952, "die"), (-18783, "ding"), (-18774, "diu"), (-18773, "dong"), (-18763, "dou"),
    (-18756, "du"), (-18741, "duan"), (-18735, "dui"), (-18731, "dun"), (-18722, "duo"),
    (-18710, "e"), (-18697, "en"), (-18696, "er"), (-18526, "fa"), (-18518, "fan"),
    (-18501, "fang"), (-18490, "fei"), (-18478, "fen"), (-18463, "feng"), (-18448, "fo"),
    (-18447, "fou"), (-18446, "fu"), (-18239, "ga"), (-18237, "gai"), (-18231, "gan"),
    (-18220, "gang"), (-18211, "gao"), (-18201, "ge"), (-18184, "gei"), (-18183, "gen"),
    (-18181, "geng"), (-18012, "gong"), (-17997, "gou"), (-17988, "gu"), (-17970, "gua"),
    (-17964, "guai"), (-17961, "guan"), (-17950, "guang"), (-17947, "gui"), (-17931, "gun"),
    (-17928, "guo"), (-17922, "ha"), (-17759, "hai"), (-17752, "han"), (-17733, "hang"),
    (-17730, "hao"), (-17721, "he"), (-17703, "hei"), (-17701, "hen"), (-17697, "heng"),
    (-17692, "hong"), (-17683, "hou"), (-17676, "hu"), (-17496, "hua"), (-17487, "huai"),
    (-17482, "huan"), (-17468, "huang"), (-17454, "hui"), (-17433, "hun"), (-17427, "huo"),
    (-17417, "ji"), (-17202, "jia"), (-17185, "jian"), (-16983, "jiang"), (-16970, "jiao"),
    (-16942, "jie"), (-16915, "jin"), (-16733, "jing"), (-16708, "jiong"), (-16706, "jiu"),
    (-16689, "ju"), (-16664, "juan"), (-16657, "jue"), (-16647, "jun"), (-16474, "ka"),
    (-16470, "kai"), (-16465, "kan"), (-16459, "kang"), (-16452, "kao"), (-16448, "ke"),
    (-16433, "ken"), (-16429, "keng"), (-16427, "kong"), (-16423, "kou"), (-16419, "ku"),
    (-16412, "kua"), (-16407, "kuai"), (-16403, "kuan"), (-16401, "kuang"), (-16393, "kui"),
    (-16220, "kun"), (-16216, "kuo"), (-16212, "la"), (-16205, "lai"), (-16202, "lan"),
    (-16187, "lang"), (-16180, "lao"), (-16171, "le"), (-16169, "lei"), (-16158, "leng"),
    (-16155, "li"), (-15959, "lia"), (-15958, "lian"), (-15944, "liang"), (-15933, "liao"),
    (-15920, "lie"), (-15915, "lin"), (-15903, "ling"), (-15889, "liu"), (-15878, "long"),
    (-15707, "lou"), (-15701, "lu"), (-15681, "lv"), (-15667, "luan"), (-15661, "lue"),
    (-15659, "lun"), (-15652, "luo"), (-15640, "ma"), (-15631, "mai"), (-15625, "man"),
    (-15454, "mang"), (-15448, "mao"), (-15436, "me"), (-15435, "mei"), (-15419, "men"),
    (-15416, "meng"), (-15408, "mi"), (-15394, "mian"), (-15385, "miao"), (-15377, "mie"),
    (-15375, "min"), (-15369, "ming"), (-15363, "miu"), (-15362, "mo"), (-15183, "mou"),
    (-15180, "mu"), (-15165, "na"), (-15158, "nai"), (-15153, "nan"), (-15150, "nang"),
    (-15149, "nao"), (-15144, "ne"), (-15143, "nei"), (-15141, "nen"), (-15140, "neng"),
    (-15139, "ni"), (-15128, "nian"), (-15121, "niang"), (-15119, "niao"), (-15117, "nie"),
    (-15110, "nin"), (-15109, "ning"), (-14941, "niu"), (-14937, "nong"), (-14933, "nu"),
    (-14930, "nv"), (-14929, "nuan"), (-14928, "nue"), (-14926, "nuo"), (-14922, "o"),
    (-14921, "ou"), (-14914, "pa"), (-14908, "pai"), (-14902, "pan"), (-14894, "pang"),
    (-14889, "pao"), (-14882, "pei"), (-14873, "pen"), (-14871, "peng"), (-14857, "pi"),
    (-14678, "pian"), (-14674, "piao"), (-14670, "pie"), (-14668, "pin"), (-14663, "ping"),
    (-14654, "po"), (-14645, "pu"), (-14630, "qi"), (-14594, "qia"), (-14429, "qian"),
    (-14407, "qiang"), (-14399, "qiao"), (-14384, "qie"), (-14379, "qin"), (-14368, "qing"),
    (-14355, "qiong"), (-14353, "qiu"), (-14345, "qu"), (-14170, "quan"), (-14159, "que"),
    (-14151, "qun"), (-14149, "ran"), (-14145, "rang"), (-14140, "rao"), (-14137, "re"),
    (-14135, "ren"), (-14125, "reng"), (-14123, "ri"), (-14122, "rong"), (-14112, "rou"),
    (-14109, "ru"), (-14099, "ruan"), (-14097, "rui"), (-14094, "run"), (-14092, "ruo"),
    (-14090, "sa"), (-14087, "sai"), (-14083, "san"), (-13917, "sang"), (-13914, "sao"),
    (-13910, "se"), (-13907, "sen"), (-13906, "seng"), (-13905, "sha"), (-13896, "shai"),
    (-13894, "shan"), (-13878, "shang"), (-13870, "shao"), (-13859, "she"), (-13847, "shen"),
    (-13831, "sheng"), (-13658, "shi"), (-13611, "shou"), (-13601, "shu"), (-13406, "shua"),
    (-13404, "shuai"), (-13400, "shuan"), (-13398, "shuang"), (-13395, "shui"),
    (-13391, "shun"), (-13387, "shuo"), (-13383, "si"), (-13367, "song"), (-13359, "sou"),
    (-13356, "su"), (-13343, "suan"), (-13340, "sui"), (-13329, "sun"), (-13326, "suo"),
    (-13318, "ta"), (-13147, "tai"), (-13138, "tan"), (-13120, "tang"), (-13107, "tao"),
    (-13096, "te"), (-13095, "teng"), (-13091, "ti"), (-13076, "tian"), (-13068, "tiao"),
    (-13063, "tie"), (-13060, "ting"), (-12888, "tong"), (-12875, "tou"), (-12871, "tu"),
    (-12860, "tuan"), (-12858, "tui"), (-12852, "tun"), (-12849, "tuo"), (-12838, "wa"),
    (-12831, "wai"), (-12829, "wan"), (-12812, "wang"), (-12802, "wei"), (-12607, "wen"),
    (-12597, "weng"), (-12594, "wo"), (-12585, "wu"), (-12556, "xi"), (-12359, "xia"),
    (-12346, "xian"), (-12320, "xiang"), (-12300, "xiao"), (-12120, "xie"), (-12099, "xin"),
    (-12089, "xing"), (-12074, "xiong"), (-12067, "xiu"), (-12058, "xu"), (-12039, "xuan"),
    (-11867, "xue"), (-11861, "xun"), (-11847, "ya"), (-11831, "yan"), (-11798, "yang"),
    (-11781, "yao"), (-11604, "ye"), (-11589, "yi"), (-11536, "yin"), (-11358, "ying"),
    (-11340, "yo"), (-11339, "yong"), (-11324, "you"), (-11303, "yu"), (-11097, "yuan"),
    (-11077, "yue"), (-11067, "yun"), (-11055, "za"), (-11052, "zai"), (-11045, "zan"),
    (-11041, "zang"), (-11038, "zao"), (-11024, "ze"), (-11020, "zei"), (-11019, "zen"),
    (-11018, "zeng"), (-11014, "zha"), (-10838, "zhai"), (-10832, "zhan"), (-10815, "zhang"),
    (-10800, "zhao"), (-10790, "zhe"), (-10780, "zhen"), (-10764, "zheng"), (-10587, "zhi"),
    (-10544, "zhong"), (-10533, "zhou"), (-10519, "zhu"), (-10331, "zhua"),
    (-10329, "zhuai"), (-10328, "zhuan"), (-10322, "zhuang"), (-10315, "zhui"),
    (-10309, "zhun"), (-10307, "zhuo"), (-10296, "zi"), (-10281, "zong"), (-10274, "zou"),
    (-10270, "zu"), (-10262, "zuan"), (-10260, "zui"), (-10256, "zun"), (-10254, "zuo"),
]


def gb2312_pinyin(ch: str) -> str:
    try:
        encoded = ch.encode("gb2312")
    except UnicodeEncodeError:
        return ""
    if len(encoded) != 2:
        return ""
    code = encoded[0] * 256 + encoded[1] - 65536
    for threshold, syllable in reversed(GB2312_PINYIN_RANGES):
        if code >= threshold:
            return syllable
    return ""


def transliterate_title(value: str) -> str:
    if lazy_pinyin is not None:
        return " ".join(lazy_pinyin(value, errors="default"))

    tokens: list[str] = []
    ascii_buffer: list[str] = []

    def flush_ascii_buffer() -> None:
        if ascii_buffer:
            tokens.append("".join(ascii_buffer))
            ascii_buffer.clear()

    for ch in value:
        if ch.isascii():
            if ch.isalnum() or ch in " _-":
                ascii_buffer.append(ch)
            else:
                flush_ascii_buffer()
                tokens.append(" ")
            continue
        flush_ascii_buffer()
        tokens.append(gb2312_pinyin(ch))

    flush_ascii_buffer()
    return " ".join(token for token in tokens if token)


def slugify(value: str) -> str:
    raw = value.strip()
    value = transliterate_title(raw).lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value, flags=re.ASCII)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if value:
        return value
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"novel-{digest}"


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def yaml_quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    escaped = "".join(ch if ch >= " " else f"\\x{ord(ch):02x}" for ch in escaped)
    return '"' + escaped + '"'


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a novel-architect project skeleton.")
    parser.add_argument("title", help="Novel display title")
    parser.add_argument("--root", default="novels", help="Directory that will contain novel projects")
    parser.add_argument("--slug", help="Filesystem-safe project slug")
    parser.add_argument("--genre", default="", help="Novel genre")
    parser.add_argument("--brief", default="", help="Raw natural-language novel brief")
    parser.add_argument("--core-idea", default="", help="Core story idea")
    parser.add_argument("--protagonist", default="", help="Initial protagonist description")
    parser.add_argument("--target-readers", default="", help="Target readers")
    parser.add_argument("--style", default="", help="Writing style")
    parser.add_argument("--pace", default="", help="Narrative pace")
    parser.add_argument("--romance-intensity", default="")
    parser.add_argument("--suspense-density", default="")
    parser.add_argument("--payoff-density", default="")
    parser.add_argument("--ai-freedom", default="")
    parser.add_argument("--target-total-words", type=non_negative_int, default=0)
    parser.add_argument("--target-chapter-words", type=non_negative_int, default=0)
    parser.add_argument("--target-chapter-count", type=non_negative_int)
    parser.add_argument("--force", action="store_true", help="Allow using an existing project directory")
    parser.add_argument("--dry-run", action="store_true", help="Print the target directory without creating files")
    args = parser.parse_args()

    slug = slugify(args.slug) if args.slug else slugify(args.title)
    root = Path(args.root).expanduser().resolve()
    project = root / slug
    if root.anchor == str(root):
        raise SystemExit(f"Refusing to create a novel project directly under filesystem root: {root}")
    if project.exists() and not args.force:
        raise SystemExit(f"Project already exists: {project}")
    if args.dry_run:
        print(project)
        return 0

    for folder in FOLDERS:
        (project / folder).mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now().isoformat(timespec="seconds")
    core_idea = args.core_idea or args.brief
    brief = f"""# {args.title}

## Raw Brief

{args.brief}

## Extracted Requirements

- Title: {args.title}
- Slug: {slug}
- Genre: {args.genre}
- Core story idea: {core_idea}
- Target total words: {args.target_total_words or ""}
- Target chapter words: {args.target_chapter_words or ""}
- Target chapter count: {args.target_chapter_count or ""}
- Protagonist: {args.protagonist}
- Target readers: {args.target_readers}
- Writing style: {args.style}
- Pace: {args.pace}
- Romance intensity: {args.romance_intensity}
- Suspense density: {args.suspense_density}
- Payoff density: {args.payoff_density}
- AI creative freedom: {args.ai_freedom}

## Assumptions

## Missing Decisions
"""
    write_if_missing(project / "00_project" / "brief.md", brief)

    requirements = f"""# Requirements

- Title: {args.title}
- Genre: {args.genre}
- Target total words: {args.target_total_words or ""}
- Target chapter words: {args.target_chapter_words or ""}
- Target chapter count: {args.target_chapter_count or ""}
- Core story idea: {core_idea}
- Protagonist: {args.protagonist}
- Target readers: {args.target_readers}
- Writing style: {args.style}
- Pace: {args.pace}
- Romance intensity: {args.romance_intensity}
- Suspense density: {args.suspense_density}
- Payoff density: {args.payoff_density}
- AI creative freedom: {args.ai_freedom}

## Inferred Assumptions

## Open Questions
"""
    write_if_missing(project / "00_project" / "requirements.md", requirements)

    chapter_count = args.target_chapter_count if args.target_chapter_count is not None else "null"
    status = f"""title: {yaml_quote(args.title)}
slug: {yaml_quote(slug)}
genre: {yaml_quote(args.genre)}
target_total_words: {args.target_total_words}
target_chapter_words: {args.target_chapter_words}
target_chapter_count: {chapter_count}
current_volume: 1
current_chapter: 0
last_completed_chapter: 0
total_words_estimate: 0
phase: "created"
open_risks: []
next_action: "plan"
updated_at: {yaml_quote(now)}
"""
    write_if_missing(project / "00_project" / "status.yaml", status)

    placeholders = {
        "00_project/change_log.md": "# Change Log\n",
        "01_concept/core.md": "# Core Concept\n",
        "01_concept/synopsis.md": "# Synopsis\n",
        "02_world/world_bible.md": "# World Bible\n",
        "02_world/terms.yaml": "terms: []\n",
        "02_world/rules.yaml": "rules: []\n",
        "03_characters/characters.yaml": "characters: []\n",
        "03_characters/relationships.yaml": "relationships: []\n",
        "04_story/master_outline.md": "# Master Outline\n",
        "04_story/plotlines.yaml": "plotlines: []\n",
        "04_story/foreshadowing.yaml": "foreshadowing: []\n",
        "04_story/timeline.yaml": "events: []\n",
        "05_structure/chapter_toc.yaml": "chapters: []\n",
        "05_structure/volumes/volume_001.md": "# Volume 001\n\n## Goal\n\n## Main Conflict\n\n## Main Characters\n\n## Protagonist Growth\n\n## Climax\n\n## Ending Climax\n\n## Foreshadowing Progress\n",
        "05_structure/phases/phase_001.md": "# Phase 001\n\n## Goal\n\n## Scope\n\n## Turning Point\n",
        "08_memory/novel_bible.md": "# Novel Bible\n",
        "08_memory/permanent.md": "# Permanent Memory\n",
        "08_memory/open_threads.md": "# Open Threads\n",
        "09_writing/style.md": "# Style\n",
        "09_writing/writing_rules.md": "# Writing Rules\n",
        "09_writing/forbidden_patterns.md": "# Forbidden Patterns\n\n- 微微一愣\n- 不禁\n- 嘴角勾起\n- 眼中闪过\n- 空气仿佛凝固\n- 倒吸一口凉气\n- 这一刻终于明白\n- 命运的齿轮\n",
        "09_writing/vocabulary.md": "# Vocabulary\n",
        "09_writing/prompts.md": "# Novel-Specific Prompts\n",
    }
    for rel_path, content in placeholders.items():
        write_if_missing(project / rel_path, content)

    print(project, file=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
