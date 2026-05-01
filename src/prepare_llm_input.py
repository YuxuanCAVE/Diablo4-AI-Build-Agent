from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from convert_d2core_raw import (
    DEFAULT_RAW_PATH,
    DEFAULT_REFERENCE_DIR,
    convert_variant,
    load_raw_build,
    load_references,
    resolve_path,
)
from generate_candidate_pool import generate_candidate_pool


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_OUTPUT = ROOT_DIR / "outputs" / "build_analysis_input.json"
DEFAULT_CANDIDATE_OUTPUT = ROOT_DIR / "outputs" / "build_candidate_pool.json"


ANALYSIS_RULES = [
    "Only use data present in this JSON.",
    "Do not invent missing skills, gear, aspects, uniques, affixes, glyphs, legendary nodes, or mechanics.",
    "If data is missing or auto-inferred, clearly say 当前数据不足 or 根据当前数据推测.",
    "Prioritize description, selected_mods, affix_details, sockets, bonus, and legendary_bonus fields over name-only guesses.",
    "Explain for normal players, not only expert theorycrafters.",
    "Suggestions are allowed only when the supporting fields are cited.",
]

REPORT_SECTIONS = [
    "Build Overview",
    "Core Mechanism",
    "Skill Synergy",
    "Gear Dependency",
    "Affix and Stat Tendencies",
    "Paragon and Glyph Logic",
    "Strengths",
    "Weaknesses",
    "Beginner Friendliness",
    "Missing Gear Alternatives",
    "Final Recommendation",
]

CANDIDATE_RULES = [
    "Candidates are relevance matches, not proven upgrades.",
    "Do not recommend items outside current_build or candidate_pool.",
    "Separate possible output upgrades, survival upgrades, budget/downgrade options, and risky tests.",
    "For every suggestion, explain what may be gained and what may be lost.",
    "If a comparison requires real damage or defense formulas not present in the data, say it needs testing.",
]

CANDIDATE_SECTIONS = [
    "Potential Aspect Tests",
    "Potential Unique Tests",
    "Potential Affix Tests",
    "Potential Glyph or Legendary Node Tests",
    "Likely Core Pieces Not To Replace",
    "Risks and Required Testing",
]


ADDITIVE_DAMAGE_PATTERNS = {
    "CriticalDamage": ["暴击伤害", "Critical Damage", "CritDamage"],
    "VulnerableDamage": ["易伤伤害", "Vulnerable Damage", "Damage_to_Vulnerable"],
    "FireDamage": ["火焰伤害", "Fire Damage", "DamageType_Fire"],
    "ShadowDamage": ["暗影伤害", "Shadow Damage", "DamageType_Shadow"],
    "PhysicalDamage": ["物理伤害", "Physical Damage", "DamageType_Physical"],
    "CoreSkillDamage": ["核心技能", "Core Skill", "SkillRankBonus_Generic_Category_Core"],
    "CloseDamage": ["近距", "Close Damage"],
    "EliteDamage": ["精英", "Elite"],
}

DEFENSE_LAYER_PATTERNS = {
    "Life": ["生命", "Life"],
    "Armor": ["护甲", "Armor"],
    "Resistance": ["抗性", "Resistance"],
    "Fortify": ["强固", "Fortify"],
    "Barrier": ["屏障", "Barrier"],
    "Damage Reduction": ["伤害减免", "Damage Reduction", "DamageReduction"],
    "Dodge": ["闪避", "Dodge"],
}

UPTIME_PATTERNS = {
    "Cooldown Reduction": ["冷却", "Cooldown", "CDR"],
    "Attack Speed": ["攻击速度", "Attack Speed", "AttackSpeed"],
    "Buff Duration": ["持续时间", "Buff Duration", "Duration"],
    "Skill Duration": ["技能持续", "Skill Duration"],
    "Movement Speed": ["移动速度", "Movement Speed"],
}

RESOURCE_PATTERNS = {
    "resource_generation": ["资源生成", "生成", "Resource Generation"],
    "resource_cost_reduction": ["消耗降低", "消耗减免", "Resource Cost Reduction", "Cost Reduction"],
    "resource_spenders": ["消耗:", "愤怒消耗", "Resource Cost"],
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_current_build(raw_path: Path, reference_dir: Path, variant_index: int) -> dict[str, Any]:
    raw = load_raw_build(raw_path)
    refs = load_references(reference_dir)
    variants = raw.get("variants") or []

    if not variants:
        raise ValueError("No variants found in raw build.")
    if variant_index < 0 or variant_index >= len(variants):
        raise ValueError(f"Variant index out of range: {variant_index}. Available: 0-{len(variants) - 1}.")

    return convert_variant(raw, variants[variant_index], variant_index, refs)


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    return str(value)


def unique(values: list[str] | set[str]) -> list[str]:
    return sorted({value for value in values if value})


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def collect_stat_keywords(build: dict[str, Any], pattern_map: dict[str, list[str]]) -> list[str]:
    text = flatten_text(build)
    return unique([name for name, patterns in pattern_map.items() if contains_any(text, patterns)])


def extract_multiplicative_sources(build: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    search_groups = [
        ("aspect", build.get("aspects") or []),
        ("unique", build.get("uniques") or []),
        ("glyph", build.get("glyphs") or []),
        ("legendary_node", build.get("legendary_nodes") or []),
    ]

    for source_type, items in search_groups:
        for item in items:
            text = flatten_text(
                [
                    item.get("description"),
                    item.get("bonus"),
                    item.get("legendary_bonus"),
                ]
            )
            if "[x]" not in text and "x" not in text.lower():
                continue

            condition = "unknown"
            if "易伤" in text:
                condition = "while enemy is Vulnerable or related condition is active"
            elif "暗影形态" in text:
                condition = "while Shadow Form or related buff is active"
            elif "控制" in text or "不可阻挡" in text:
                condition = "while crowd-control or unstoppable condition is met"
            elif "恶魔形态" in text:
                condition = "while Demon Form or Demonology condition is active"

            sources.append(
                {
                    "source": source_type,
                    "name": item.get("name") or item.get("key") or "",
                    "key": item.get("key") or "",
                    "condition": condition,
                    "value_type": "[x]",
                    "evidence": text[:240],
                }
            )

    return sources


def has_vulnerable_application(build: dict[str, Any]) -> bool:
    text = flatten_text(
        [
            skill.get("description")
            for skill in build.get("core_skills") or []
        ]
        + [
            mod.get("description")
            for skill in build.get("core_skills") or []
            for mod in skill.get("selected_mods") or []
        ]
        + [
            node.get("description")
            for node in build.get("legendary_nodes") or []
        ]
    )
    return "易伤" in text


def build_trigger_mechanics(build: dict[str, Any]) -> dict[str, Any]:
    text = flatten_text(build)
    has_crit_chance = contains_any(text, ["暴击几率", "CritChance", "Critical Strike Chance"])
    has_crit_damage = contains_any(text, ["暴击伤害", "CritDamage", "Critical Strike Damage"])
    has_vulnerable_damage = contains_any(text, ["易伤伤害", "Vulnerable Damage", "Damage_to_Vulnerable"])
    vulnerable_application = has_vulnerable_application(build)
    has_overpower_damage = contains_any(text, ["压制伤害", "Overpower Damage"])
    guaranteed_overpower = contains_any(text, ["必定压制", "guaranteed overpower"])
    has_lucky_hit = contains_any(text, ["幸运一击", "Lucky Hit", "LuckyHit"])

    return {
        "critical": {
            "has_crit_chance": has_crit_chance,
            "has_crit_damage": has_crit_damage,
            "reliable_trigger": "unknown" if has_crit_damage and not has_crit_chance else "likely_supported" if has_crit_chance else "not_detected",
        },
        "vulnerable": {
            "has_vulnerable_damage": has_vulnerable_damage,
            "has_vulnerable_application": vulnerable_application,
            "warning": "" if vulnerable_application else "存在易伤相关收益，但当前数据不足以证明稳定易伤覆盖",
        },
        "overpower": {
            "has_overpower_damage": has_overpower_damage,
            "has_guaranteed_overpower": guaranteed_overpower,
            "warning": "" if guaranteed_overpower or not has_overpower_damage else "存在压制词条，但未发现稳定压制触发机制",
        },
        "lucky_hit": {
            "has_lucky_hit_effect": has_lucky_hit,
            "role": "resource / control / proc" if has_lucky_hit else "not_detected",
        },
    }


def build_resource_loop(build: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {
        "resource_generation": [],
        "resource_cost_reduction": [],
        "resource_spenders": [],
    }
    for section, patterns in RESOURCE_PATTERNS.items():
        matches: list[str] = []
        for skill in build.get("core_skills") or []:
            text = flatten_text(skill)
            if contains_any(text, patterns):
                matches.append(skill.get("name") or skill.get("key") or "unknown skill")
        for gear in build.get("gear") or []:
            text = flatten_text(gear.get("affix_details") or [])
            if contains_any(text, patterns):
                matches.append(gear.get("slot") or gear.get("name") or "unknown gear")
        result[section] = unique(matches)
    return result


def build_mechanic_rules() -> dict[str, Any]:
    return {
        "_source_files": [
            "data/reference/characteristic.json",
            "data/reference/indepth_dmg_calculater.json",
        ],
        "stat_rules": {
            "core_stats": {
                "Strength": "提供护甲，并可能按职业提供额外收益。",
                "Intelligence": "提供全抗性，并可能按职业提供额外收益。",
                "Willpower": "提供治疗效果和压制伤害，并可能按职业提供额外收益。",
                "Dexterity": "提供闪避率，并可能按职业提供额外收益。",
            },
            "offensive_stats": [
                "Weapon Damage",
                "Weapon Speed",
                "Critical Chance",
                "Critical Damage",
                "Vulnerable Damage",
                "Elemental Damage",
                "Overpower Damage",
                "Skill Ranks",
            ],
            "defensive_stats": [
                "Maximum Life",
                "Armor",
                "Resistance",
                "Dodge",
                "Barrier",
                "Damage Reduction",
                "Healing Received",
            ],
            "utility_stats": [
                "Cooldown Reduction",
                "Resource Generation",
                "Movement Speed",
                "Crowd Control Duration",
                "Skill Duration",
            ],
        },
        "damage_bucket_notes": {
            "additive_damage": {
                "summary": "许多条件伤害词条属于加法伤害倾向，实际价值取决于触发条件、覆盖率和已有加法池大小。",
                "analysis_hint": "不要只因为词条数值更大就判断它一定更强，需要说明覆盖率和触发条件。",
            },
            "multiplicative_damage": {
                "summary": "带 [x] 的来源通常表示乘法收益，但仍需要满足对应条件。",
                "analysis_hint": "优先检查当前 Build 是否能稳定满足乘法来源的条件。",
            },
            "main_stat": {
                "summary": "主属性可提高技能伤害或相关职业收益，但它不是单独替代所有乘法来源的万能指标。",
                "analysis_hint": "解释主属性时应结合职业、技能标签和装备词条。",
            },
        },
        "trigger_rules": {
            "critical": "暴击伤害需要暴击几率支撑；只有暴击伤害但缺少暴击率时，收益稳定性不足。",
            "vulnerable": "存在易伤伤害不等于稳定易伤覆盖，需要找到易伤施加来源。",
            "overpower": "压制伤害需要压制触发来源，否则可能只是低频收益。",
            "lucky_hit": "幸运一击实际触发率通常由技能幸运一击几率和特效触发率共同决定。",
            "conditional_damage": "条件伤害的实际价值取决于条件覆盖率，例如目标是否稳定处于易伤、控制或特定状态。",
        },
        "analysis_limits": [
            "当前版本不计算真实 DPS，只做机制解释和构筑倾向分析。",
            "不要声称某个候选一定更强，除非输入中包含足够的计算和实测依据。",
            "不要把加法伤害和乘法伤害视为同等收益。",
            "讨论条件伤害时必须提到覆盖率或触发条件。",
            "讨论暴击、压制、易伤、幸运一击时必须提到触发可靠性。",
        ],
    }


def build_mechanic_summary(current_build: dict[str, Any]) -> dict[str, Any]:
    damage_types = unique(
        {
            skill.get("damage_type")
            for skill in current_build.get("core_skills") or []
            if skill.get("damage_type")
        }
    )
    skill_tags = unique(
        {
            tag
            for skill in current_build.get("core_skills") or []
            for tag in skill.get("tags") or []
            if tag
        }
    )

    return {
        "damage_types": damage_types,
        "skill_tags": skill_tags,
        "additive_damage_keywords": collect_stat_keywords(current_build, ADDITIVE_DAMAGE_PATTERNS),
        "multiplicative_sources": extract_multiplicative_sources(current_build),
        "trigger_mechanics": build_trigger_mechanics(current_build),
        "defense_layers": collect_stat_keywords(current_build, DEFENSE_LAYER_PATTERNS),
        "resource_loop": build_resource_loop(current_build),
        "uptime_dependencies": collect_stat_keywords(current_build, UPTIME_PATTERNS),
        "mechanic_rules": build_mechanic_rules(),
        "warnings": [
            "当前 mechanic_summary 是解释辅助，不是完整数值模拟器。",
            "trigger_mechanics 和 resource_loop 来自文本/字段扫描，结论需要结合实际游戏测试。",
        ],
    }


def build_analysis_input(current_build: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": "analyze_diablo4_build",
        "language": "zh-CN",
        "rules": ANALYSIS_RULES,
        "report_sections": REPORT_SECTIONS,
        "mechanic_summary": build_mechanic_summary(current_build),
        "current_build": current_build,
        "_notes": [
            "This is the primary file to send to an LLM for build analysis.",
            "Reference descriptions are embedded only for items used by the current build.",
            "The LLM should analyze, not calculate exact optimization.",
        ],
    }


def build_candidate_input(
    current_build: dict[str, Any],
    reference_dir: Path,
    limit: int,
    include_used: bool,
) -> dict[str, Any]:
    candidate_data = generate_candidate_pool(
        build=current_build,
        reference_dir=reference_dir,
        limit=limit,
        include_used=include_used,
    )
    return {
        "task": "explore_diablo4_build_candidates",
        "language": "zh-CN",
        "rules": CANDIDATE_RULES,
        "report_sections": CANDIDATE_SECTIONS,
        "current_build_summary": {
            "source_url": current_build.get("source_url") or "",
            "class": current_build.get("class") or "",
            "build_name": current_build.get("build_name") or "",
            "build_type": current_build.get("build_type") or [],
            "season": current_build.get("season") or "",
        },
        "build_profile": candidate_data["build_profile"],
        "candidate_pool": candidate_data["candidate_pool"],
        "_notes": [
            "This is optional. Use it together with build_analysis_input.json when exploring alternatives.",
            "Candidates are filtered from local reference data by class, keywords, tags, and current build mechanics.",
            "This file intentionally does not claim candidates are upgrades.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare one or two JSON files for practical LLM build analysis."
    )
    parser.add_argument("--raw", default=str(DEFAULT_RAW_PATH), help="Path to d2core raw JSON.")
    parser.add_argument("--variant", type=int, required=True, help="Variant index to prepare.")
    parser.add_argument("--reference-dir", default=str(DEFAULT_REFERENCE_DIR), help="Reference data directory.")
    parser.add_argument(
        "--analysis-out",
        default=str(DEFAULT_ANALYSIS_OUTPUT),
        help="Output path for the primary analysis JSON.",
    )
    parser.add_argument(
        "--candidate-out",
        default=str(DEFAULT_CANDIDATE_OUTPUT),
        help="Output path for the optional candidate pool JSON.",
    )
    parser.add_argument(
        "--with-candidates",
        action="store_true",
        help="Also write outputs/build_candidate_pool.json.",
    )
    parser.add_argument("--candidate-limit", type=int, default=15, help="Maximum candidates per category.")
    parser.add_argument(
        "--include-used",
        action="store_true",
        help="Include already-used items in the candidate pool.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = resolve_path(args.raw)
    reference_dir = resolve_path(args.reference_dir)
    analysis_output = resolve_path(args.analysis_out)
    candidate_output = resolve_path(args.candidate_out)

    try:
        current_build = load_current_build(raw_path, reference_dir, args.variant)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}")
        raise SystemExit(1)

    analysis_input = build_analysis_input(current_build)
    write_json(analysis_output, analysis_input)
    print(f"wrote analysis input: {analysis_output}")

    if args.with_candidates:
        candidate_input = build_candidate_input(
            current_build=current_build,
            reference_dir=reference_dir,
            limit=args.candidate_limit,
            include_used=args.include_used,
        )
        write_json(candidate_output, candidate_input)
        counts = {key: len(value) for key, value in candidate_input["candidate_pool"].items()}
        print(f"wrote candidate pool: {candidate_output}")
        print("candidate counts:", ", ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
