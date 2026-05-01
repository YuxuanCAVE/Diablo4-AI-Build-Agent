from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_PATH = ROOT_DIR / "data" / "converted" / "d2core_1STz_variant_4.json"
DEFAULT_REFERENCE_DIR = ROOT_DIR / "data" / "reference"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data" / "candidates"

MECHANIC_KEYWORDS = [
    "深渊",
    "暗影",
    "暗影形态",
    "妖术",
    "易伤",
    "虚弱",
    "恶魔学",
    "恶魔",
    "核心",
    "终极技能",
    "暴击",
    "暴击几率",
    "暴击伤害",
    "攻击速度",
    "生命",
    "护甲",
    "抗性",
    "伤害减免",
    "移动速度",
    "冷却",
    "资源",
    "愤怒",
    "幸运一击",
    "不可阻挡",
    "控制",
    "精英",
]

REFERENCE_FILTER_PREFIXES = (
    "Skill_",
    "Search_",
    "Keyword_",
    "Archetype_",
    "FILTER_",
)


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_markup(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(clean_markup(item) for item in value if item is not None).strip()

    if isinstance(value, dict):
        if "line" in value:
            return clean_markup(value.get("line"))
        return json.dumps(value, ensure_ascii=False)

    text = str(value)
    text = re.sub(r"\{/?c[^}]*\}", "", text)
    text = re.sub(r"\{/?u\}", "", text)
    text = text.replace("\\n", " ")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def clean_list(values: Any) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        values = [values]
    return [text for text in (clean_markup(value) for value in values) if text]


def normalize_text(*parts: Any) -> str:
    return " ".join(clean_markup(part).lower() for part in parts if part is not None)


def unique_sorted(values: list[str] | set[str]) -> list[str]:
    return sorted({value for value in values if value})


def keep_reference_filter(value: str, class_name: str) -> bool:
    if not value:
        return False
    if value.startswith("Archetype_"):
        return class_name in value
    if value.startswith(("Search_", "Skill_", "Keyword_")):
        return True
    if value in {"FILTER_Build_All_Generic", "FILTER_Legendary_Offensive", "FILTER_Legendary_Defensive", "FILTER_Legendary_Utility", "FILTER_Legendary_Resource"}:
        return True
    return class_name in value


def is_class_compatible(item_classes: Any, class_name: str) -> bool:
    if not item_classes:
        return True
    if not isinstance(item_classes, list):
        item_classes = [item_classes]
    return class_name in item_classes or "Generic" in item_classes


def collect_build_profile(build: dict[str, Any]) -> dict[str, Any]:
    class_name = build.get("class") or ""
    skill_tags: set[str] = set()
    damage_types: set[str] = set()
    reference_filters: set[str] = set()
    keywords: set[str] = set()

    used_aspect_keys = {item.get("key") for item in build.get("aspects", []) if item.get("key")}
    used_unique_keys = {item.get("key") for item in build.get("uniques", []) if item.get("key")}
    used_affix_keys = {
        item.get("key")
        for gear in build.get("gear", [])
        for item in gear.get("affix_details", [])
        if item.get("key")
    }
    used_glyph_keys = {item.get("key") for item in build.get("glyphs", []) if item.get("key")}
    used_legendary_node_keys = {
        item.get("key") for item in build.get("legendary_nodes", []) if item.get("key")
    }

    text_parts: list[str] = []

    for skill in build.get("core_skills", []):
        skill_tags.update(skill.get("tags") or [])
        if skill.get("damage_type"):
            damage_types.add(skill["damage_type"])
        text_parts.extend(skill.get("description") or [])
        for mod in skill.get("selected_mods") or []:
            text_parts.extend(mod.get("description") or [])

    for aspect in build.get("aspects", []):
        reference_filters.update(
            value for value in aspect.get("filters") or [] if keep_reference_filter(value, class_name)
        )
        text_parts.append(aspect.get("description") or "")

    for unique in build.get("uniques", []):
        text_parts.extend(unique.get("description") or [])

    for gear in build.get("gear", []):
        for affix in gear.get("affix_details") or []:
            text_parts.append(affix.get("description") or "")

    for glyph in build.get("glyphs", []):
        text_parts.extend([glyph.get("description") or "", glyph.get("bonus") or "", glyph.get("legendary_bonus") or ""])

    for node in build.get("legendary_nodes", []):
        reference_filters.update(
            value for value in node.get("tags") or [] if keep_reference_filter(value, class_name)
        )
        text_parts.append(node.get("description") or "")

    all_text = normalize_text(*text_parts, *skill_tags, *reference_filters, *damage_types)
    for keyword in MECHANIC_KEYWORDS:
        if keyword.lower() in all_text:
            keywords.add(keyword)

    keywords.update(tag for tag in skill_tags if len(tag) <= 12)
    keywords.update(
        filter_value
        for filter_value in reference_filters
        if filter_value.startswith(REFERENCE_FILTER_PREFIXES)
    )
    keywords.update(damage_types)

    return {
        "class": class_name,
        "build_name": build.get("build_name") or "",
        "build_type": build.get("build_type") or [],
        "damage_types": unique_sorted(damage_types),
        "skill_tags": unique_sorted(skill_tags),
        "reference_filters": unique_sorted(reference_filters),
        "keywords": unique_sorted(keywords),
        "used_aspect_keys": unique_sorted(used_aspect_keys),
        "used_unique_keys": unique_sorted(used_unique_keys),
        "used_affix_keys": unique_sorted(used_affix_keys),
        "used_glyph_keys": unique_sorted(used_glyph_keys),
        "used_legendary_node_keys": unique_sorted(used_legendary_node_keys),
    }


def match_reasons(
    *,
    text: str,
    keywords: list[str],
    item_filters: list[str] | None = None,
    profile_filters: list[str] | None = None,
    class_compatible: bool = False,
) -> list[str]:
    reasons: list[str] = []

    if class_compatible:
        reasons.append("class_compatible")

    for keyword in keywords:
        if keyword and keyword.lower() in text:
            reasons.append(f"keyword:{keyword}")

    if item_filters and profile_filters:
        matched_filters = sorted(set(item_filters) & set(profile_filters))
        reasons.extend(f"filter:{value}" for value in matched_filters[:8])

    return reasons


def compact_aspect(item: dict[str, Any], reasons: list[str], already_used: bool) -> dict[str, Any]:
    return {
        "name": item.get("name") or item.get("key") or "",
        "key": item.get("key") or "",
        "already_used": already_used,
        "score": len(reasons),
        "reasons": reasons,
        "aspect_type": item.get("aspectType") or "",
        "char": item.get("char") or [],
        "description": clean_markup(item.get("affixesDesc")),
        "filters": item.get("filters") or [],
    }


def compact_unique(item: dict[str, Any], reasons: list[str], already_used: bool) -> dict[str, Any]:
    return {
        "name": item.get("name") or item.get("key") or "",
        "key": item.get("key") or "",
        "already_used": already_used,
        "score": len(reasons),
        "reasons": reasons,
        "equip_type": item.get("equipType") or "",
        "char": item.get("char") or [],
        "is_mythic": bool(item.get("isMythic")),
        "description": clean_list(item.get("affixesDesc")),
        "damage_details": clean_list(item.get("damageDetails")),
    }


def compact_affix(item: dict[str, Any], reasons: list[str], already_used: bool) -> dict[str, Any]:
    return {
        "key": item.get("key") or "",
        "already_used": already_used,
        "score": len(reasons),
        "reasons": reasons,
        "description": clean_markup(item.get("desc")),
        "template": clean_markup(item.get("descTpl")),
        "item_type": item.get("itemType") or [],
        "char_type": item.get("charType") or [],
        "is_tempered": bool(item.get("tempered")),
    }


def compact_paragon_item(
    name: str,
    key: str,
    item: dict[str, Any],
    reasons: list[str],
    already_used: bool,
) -> dict[str, Any]:
    return {
        "name": name or key,
        "key": key,
        "already_used": already_used,
        "score": len(reasons),
        "reasons": reasons,
        "description": clean_markup(item.get("desc")),
        "bonus": clean_markup(item.get("bonus")),
        "legendary_bonus": clean_markup(item.get("legendaryBonus")),
        "tags": item.get("tags") or [],
        "threshold_requirements": item.get("threshold_requirements") or [],
    }


def sort_and_limit(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    items.sort(key=lambda item: (item.get("already_used", False), -item.get("score", 0), item.get("name") or item.get("key") or ""))
    return items[:limit]


def generate_candidate_pool(
    build: dict[str, Any],
    reference_dir: Path,
    limit: int,
    include_used: bool,
) -> dict[str, Any]:
    profile = collect_build_profile(build)
    class_name = profile["class"]
    keywords = profile["keywords"]
    profile_filters = profile["reference_filters"]

    aspects: list[dict[str, Any]] = []
    for item in load_json(reference_dir / "aspect.json"):
        key = item.get("key")
        already_used = key in profile["used_aspect_keys"]
        if already_used and not include_used:
            continue
        class_ok = is_class_compatible(item.get("char"), class_name)
        if not class_ok:
            continue
        text = normalize_text(item.get("name"), item.get("key"), item.get("affixesDesc"), item.get("filters"))
        reasons = match_reasons(
            text=text,
            keywords=keywords,
            item_filters=item.get("filters") or [],
            profile_filters=profile_filters,
            class_compatible=class_ok,
        )
        if len(reasons) > 1:
            aspects.append(compact_aspect(item, reasons, already_used))

    uniques: list[dict[str, Any]] = []
    for item in load_json(reference_dir / "uniqueItem.json"):
        key = item.get("key")
        already_used = key in profile["used_unique_keys"]
        if already_used and not include_used:
            continue
        class_ok = is_class_compatible(item.get("char"), class_name)
        if not class_ok:
            continue
        text = normalize_text(item.get("name"), item.get("key"), item.get("affixesDesc"), item.get("damageDetails"))
        reasons = match_reasons(text=text, keywords=keywords, class_compatible=class_ok)
        if len(reasons) > 1:
            uniques.append(compact_unique(item, reasons, already_used))

    affixes: list[dict[str, Any]] = []
    for item in load_json(reference_dir / "affix.json"):
        key = item.get("key")
        already_used = key in profile["used_affix_keys"]
        if already_used and not include_used:
            continue
        class_ok = is_class_compatible(item.get("charType"), class_name)
        if not class_ok:
            continue
        text = normalize_text(item.get("key"), item.get("desc"), item.get("descTpl"))
        reasons = match_reasons(text=text, keywords=keywords, class_compatible=class_ok)
        if len(reasons) > 1:
            affixes.append(compact_affix(item, reasons, already_used))

    paragon = load_json(reference_dir / "paragon.json")
    class_paragon = paragon.get(class_name, {})
    generic_paragon = paragon.get("Generic", {})

    glyphs: list[dict[str, Any]] = []
    glyph_refs = {**(generic_paragon.get("glyph") or {}), **(class_paragon.get("glyph") or {})}
    for key, item in glyph_refs.items():
        already_used = key in profile["used_glyph_keys"]
        if already_used and not include_used:
            continue
        text = normalize_text(key, item.get("name"), item.get("desc"), item.get("bonus"), item.get("legendaryBonus"))
        reasons = match_reasons(text=text, keywords=keywords, class_compatible=True)
        if len(reasons) > 1:
            glyphs.append(compact_paragon_item(item.get("name") or "", key, item, reasons, already_used))

    legendary_nodes: list[dict[str, Any]] = []
    node_refs = {**(generic_paragon.get("node") or {}), **(class_paragon.get("node") or {})}
    for key, item in node_refs.items():
        if "Legendary" not in key:
            continue
        already_used = key in profile["used_legendary_node_keys"]
        if already_used and not include_used:
            continue
        text = normalize_text(key, item.get("name"), item.get("desc"), item.get("tags"))
        reasons = match_reasons(
            text=text,
            keywords=keywords,
            item_filters=item.get("tags") or [],
            profile_filters=profile_filters,
            class_compatible=True,
        )
        if len(reasons) > 1:
            legendary_nodes.append(compact_paragon_item(item.get("name") or "", key, item, reasons, already_used))

    return {
        "source_build": {
            "source_url": build.get("source_url") or "",
            "build_name": build.get("build_name") or "",
        },
        "build_profile": profile,
        "candidate_pool": {
            "aspects": sort_and_limit(aspects, limit),
            "uniques": sort_and_limit(uniques, limit),
            "affixes": sort_and_limit(affixes, limit),
            "glyphs": sort_and_limit(glyphs, limit),
            "legendary_nodes": sort_and_limit(legendary_nodes, limit),
        },
        "_notes": [
            "Candidates are relevance matches, not optimization conclusions.",
            "score is a simple count of class/filter/keyword reasons.",
            "Use this file as LLM context for possible tests, downgrade options, or replacement exploration.",
        ],
    }


def default_output_path(build_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{build_path.stem}_candidates.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a relevance-based candidate pool for a converted Build JSON.")
    parser.add_argument("--build", default=str(DEFAULT_BUILD_PATH), help="Path to converted Build JSON.")
    parser.add_argument("--reference-dir", default=str(DEFAULT_REFERENCE_DIR), help="Reference data directory.")
    parser.add_argument("--out", help="Output candidate JSON path.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum candidates per category.")
    parser.add_argument("--include-used", action="store_true", help="Include items already used by the current build.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_path = resolve_path(args.build)
    reference_dir = resolve_path(args.reference_dir)
    output_path = resolve_path(args.out) if args.out else default_output_path(build_path, DEFAULT_OUTPUT_DIR)

    build = load_json(build_path)
    candidate_pool = generate_candidate_pool(
        build=build,
        reference_dir=reference_dir,
        limit=args.limit,
        include_used=args.include_used,
    )
    write_json(output_path, candidate_pool)

    counts = {
        key: len(value)
        for key, value in candidate_pool["candidate_pool"].items()
    }
    print(f"wrote candidates: {output_path}")
    print("counts:", ", ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
