from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_RAW_PATH = ROOT_DIR / "data" / "raw" / "d2core_raw_001.json"
DEFAULT_REFERENCE_DIR = ROOT_DIR / "data" / "reference"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data" / "converted"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return " ".join(self.parts)


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_raw_build(path: Path) -> dict[str, Any]:
    raw = load_json(path)
    response_data = raw.get("data", {}).get("response_data")
    if not isinstance(response_data, str):
        raise ValueError("Expected data.response_data to be a JSON string.")

    parsed = json.loads(response_data)
    data = parsed.get("data")
    if not isinstance(data, dict):
        raise ValueError("Expected response_data.data to be an object.")

    return data


def load_references(reference_dir: Path) -> dict[str, Any]:
    skilltree = load_json(reference_dir / "warlock_skilltree.json")
    paragon = load_json(reference_dir / "paragon.json")

    return {
        "skills_by_key": {
            item["key"]: item for item in skilltree.get("skills", []) if item.get("key")
        },
        "skills_by_id": {
            str(item["id"]): item for item in skilltree.get("skills", []) if item.get("id") is not None
        },
        "aspects_by_key": {
            item["key"]: item for item in load_json(reference_dir / "aspect.json") if item.get("key")
        },
        "uniques_by_key": {
            item["key"]: item for item in load_json(reference_dir / "uniqueItem.json") if item.get("key")
        },
        "affixes_by_key": {
            item["key"]: item for item in load_json(reference_dir / "affix.json") if item.get("key")
        },
        "runes_by_key": {
            item["key"]: item for item in load_json(reference_dir / "rune.json") if item.get("key")
        },
        "expertise_by_key": {
            item["key"]: item for item in load_json(reference_dir / "expertise.json") if item.get("key")
        },
        "paragon": paragon,
    }


def clean_html(value: str | None) -> str:
    if not value:
        return ""

    parser = TextExtractor()
    parser.feed(value)
    return re.sub(r"\s+", " ", html.unescape(parser.get_text())).strip()


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

    result: list[str] = []
    for value in values:
        text = clean_markup(value)
        if text:
            result.append(text)
    return result


def selected_skill_mods(equipped: dict[str, Any], skill_ref: dict[str, Any]) -> list[dict[str, Any]]:
    selected_names = {str(name).lower() for name in equipped.get("mods") or []}
    result: list[dict[str, Any]] = []

    for mod in skill_ref.get("mods") or []:
        eng_name = str(mod.get("engName") or "").lower()
        local_name = str(mod.get("name") or "").lower()
        if eng_name not in selected_names and local_name not in selected_names:
            continue

        result.append(
            {
                "name": mod.get("name") or mod.get("engName") or "",
                "eng_name": mod.get("engName") or "",
                "key": f"{skill_ref.get('id')}_{mod.get('id')}",
                "description": clean_list(mod.get("desc")),
            }
        )

    return result


def compact_affix(ref: dict[str, Any], fallback_key: str) -> dict[str, Any]:
    return {
        "key": fallback_key,
        "description": clean_markup(ref.get("desc")) or fallback_key,
        "template": clean_markup(ref.get("descTpl")),
        "is_tempered": bool(ref.get("tempered")),
    }


def compact_socket(socket: dict[str, Any], refs: dict[str, Any]) -> dict[str, Any]:
    key = socket.get("key") or ""
    rune_ref = refs["runes_by_key"].get(key)
    if rune_ref:
        return {
            "type": socket.get("type") or rune_ref.get("type") or "",
            "key": key,
            "name": rune_ref.get("name") or key,
            "description": clean_list(rune_ref.get("affixesDesc")),
            "value": rune_ref.get("value"),
            "quality": rune_ref.get("quality") or "",
        }

    return {
        "type": socket.get("type") or "",
        "key": key,
        "name": key,
        "description": [],
    }


def infer_skill_role(skill: dict[str, Any], rank: int) -> str:
    tags = set(skill.get("tags") or [])
    name = str(skill.get("name") or "")
    key = str(skill.get("key") or "")

    if "终极技能" in tags:
        return "ultimate"
    if "防御" in tags or "护盾" in tags:
        return "defense"
    if "位移" in tags or "移动" in tags or "step" in key:
        return "mobility"
    if "基础" in tags:
        return "generator_or_basic"
    if "核心" in tags or rank >= 12:
        return "main_damage_or_core"
    if "命令" in name:
        return "summon_command"

    return "support"


def selected_skill_ids(variant: dict[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for raw_key, rank in (variant.get("skill") or {}).items():
        base_id = raw_key.split("_", 1)[0]
        if not raw_key.isdigit():
            continue
        if isinstance(rank, int) and rank > 0:
            result[base_id] = rank
    return result


def convert_core_skills(variant: dict[str, Any], refs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    unresolved: list[str] = []
    skills: list[dict[str, Any]] = []
    ranks = selected_skill_ids(variant)
    seen: set[str] = set()

    for equipped in variant.get("equipSkills") or []:
        key = equipped.get("key")
        ref = refs["skills_by_key"].get(key)
        if not ref:
            unresolved.append(str(key))
            continue

        skill_id = str(ref.get("id"))
        rank = int(equipped.get("rank") or ranks.get(skill_id) or 0)
        seen.add(skill_id)
        skills.append(
            {
                "name": ref.get("name") or key,
                "key": key,
                "rank": rank,
                "role": infer_skill_role(ref, rank),
                "description": clean_list(ref.get("desc")),
                "damage_type": ref.get("damageType") or "",
                "tags": ref.get("tags") or [],
                "selected_mods": selected_skill_mods(equipped, ref),
                "notes": f"rank={rank}; active_bar=true",
            }
        )

    for skill_id, rank in ranks.items():
        if skill_id in seen:
            continue

        ref = refs["skills_by_id"].get(skill_id)
        if not ref:
            unresolved.append(skill_id)
            continue

        skills.append(
            {
                "name": ref.get("name") or skill_id,
                "key": ref.get("key") or skill_id,
                "rank": rank,
                "role": infer_skill_role(ref, rank),
                "description": clean_list(ref.get("desc")),
                "damage_type": ref.get("damageType") or "",
                "tags": ref.get("tags") or [],
                "selected_mods": [],
                "notes": f"id={skill_id}; rank={rank}; active_bar=false",
            }
        )

    return skills, unresolved


def convert_gear(variant: dict[str, Any], refs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    gear: list[dict[str, Any]] = []
    aspects: list[dict[str, Any]] = []
    uniques: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for slot_id, item in sorted((variant.get("gear") or {}).items(), key=lambda pair: int(pair[0])):
        key = item.get("key")
        item_type = item.get("type") or ""
        slot = item.get("itemType") or f"slot_{slot_id}"
        mods = item.get("mods") or []
        affixes: list[str] = []
        affix_details: list[dict[str, Any]] = []
        sockets = [
            compact_socket(socket, refs)
            for socket in item.get("sockets") or []
            if isinstance(socket, dict)
        ]

        for mod in mods:
            if not isinstance(mod, dict):
                continue
            mod_name = mod.get("name")
            affix_ref = refs["affixes_by_key"].get(mod_name)
            affixes.append(clean_markup((affix_ref or {}).get("desc")) or mod_name or "")
            affix_details.append(compact_affix(affix_ref or {}, mod_name or ""))

        if item_type == "uniqueItem":
            ref = refs["uniques_by_key"].get(key)
            if not ref:
                unresolved.append(str(key))
            name = (ref or {}).get("name") or item.get("name") or key
            uniques.append(
                {
                    "name": name,
                    "key": key,
                    "slot": slot,
                    "required": True,
                    "description": clean_list((ref or {}).get("affixesDesc")),
                    "flavor": clean_markup((ref or {}).get("flavor")),
                    "damage_details": clean_list((ref or {}).get("damageDetails")),
                    "is_mythic": bool((ref or {}).get("isMythic")),
                    "notes": f"item_power={item.get('itemPower')}; source=variant gear",
                }
            )
            gear_type = "unique"
        else:
            ref = refs["aspects_by_key"].get(key)
            if not ref:
                unresolved.append(str(key))
            name = (ref or {}).get("name") or item.get("name") or key
            aspects.append(
                {
                    "name": name,
                    "key": key,
                    "slot": slot,
                    "priority": "high",
                    "description": clean_markup((ref or {}).get("affixesDesc")),
                    "aspect_type": item.get("aspectType") or (ref or {}).get("aspectType", ""),
                    "filters": (ref or {}).get("filters") or [],
                    "notes": f"source=variant gear",
                }
            )
            gear_type = "legendary"

        gear.append(
            {
                "slot": slot,
                "item_type": gear_type,
                "name": name,
                "required": True,
                "recommended_affixes": [value for value in affixes if value],
                "affix_details": affix_details,
                "sockets": sockets,
            }
        )

    return gear, aspects, uniques, unresolved


def convert_affix_priorities(variant: dict[str, Any], refs: dict[str, Any]) -> list[dict[str, Any]]:
    categories: dict[str, list[str]] = {
        "offense": [],
        "defense": [],
        "utility": [],
    }
    details: dict[str, list[dict[str, Any]]] = {
        "offense": [],
        "defense": [],
        "utility": [],
    }

    for item in (variant.get("gear") or {}).values():
        for mod in item.get("mods") or []:
            if not isinstance(mod, dict):
                continue
            key = mod.get("name")
            ref = refs["affixes_by_key"].get(key, {})
            label = ref.get("desc") or key
            tags = " ".join(str(value) for value in [key, ref.get("desc"), ref.get("descTpl")] if value)
            target = "utility"
            if any(token in tags for token in ["Damage", "Crit", "SkillRank", "AttackSpeed", "Vulnerable"]):
                target = "offense"
            elif any(token in tags for token in ["Life", "Armor", "Resistance", "DamageReduction"]):
                target = "defense"
            if label and label not in categories[target]:
                categories[target].append(label)
                details[target].append(compact_affix(ref, key or ""))

    return [
        {
            "category": category,
            "priority_order": values,
            "affix_details": details[category],
            "notes": "Auto-collected from equipped gear affixes. Order reflects first appearance, not a verified priority ranking.",
        }
        for category, values in categories.items()
        if values
    ]


def node_suffix(raw_node: str) -> str:
    parts = raw_node.split("_")
    if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
        return "_".join(parts[2:])
    return raw_node


def convert_paragon(raw: dict[str, Any], variant: dict[str, Any], refs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    class_name = raw.get("char") or "Generic"
    paragon_data = refs["paragon"].get(class_name, {})
    board_refs = paragon_data.get("board") or {}
    node_refs = {**(refs["paragon"].get("Generic", {}).get("node") or {}), **(paragon_data.get("node") or {})}
    glyph_refs = {**(refs["paragon"].get("Generic", {}).get("glyph") or {}), **(paragon_data.get("glyph") or {})}

    boards: list[dict[str, Any]] = []
    glyphs: list[dict[str, Any]] = []
    legendary_nodes: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for board_key, board in (variant.get("paragon") or {}).items():
        board_ref = board_refs.get(board_key)
        if not board_ref:
            unresolved.append(board_key)
        board_name = (board_ref or {}).get("name") or board_key

        important_nodes: list[str] = []
        important_node_details: list[dict[str, Any]] = []
        for raw_node in board.get("data") or []:
            suffix = node_suffix(raw_node)
            node_ref = node_refs.get(suffix)
            if not node_ref:
                unresolved.append(suffix)
                continue
            node_name = node_ref.get("name") or suffix
            if "Rare" in suffix or "Legendary" in suffix:
                important_nodes.append(node_name)
                important_node_details.append(
                    {
                        "name": node_name,
                        "key": suffix,
                        "description": clean_markup(node_ref.get("desc")),
                        "tags": node_ref.get("tags") or [],
                    }
                )
            if "Legendary" in suffix:
                legendary_nodes.append(
                    {
                        "name": node_name,
                        "key": suffix,
                        "board": board_name,
                        "priority": "high",
                        "description": clean_markup(node_ref.get("desc")),
                        "tags": node_ref.get("tags") or [],
                        "notes": f"selected on board {board_key}",
                    }
                )

        boards.append(
            {
                "name": board_name,
                "key": board_key,
                "purpose": f"Auto-converted from board key {board_key}.",
                "important_nodes": important_nodes,
                "important_node_details": important_node_details,
                "selected_node_count": len(board.get("data") or []),
            }
        )

        for socket, glyph_key in (board.get("glyph") or {}).items():
            glyph_ref = glyph_refs.get(glyph_key)
            if not glyph_ref:
                unresolved.append(glyph_key)
            glyphs.append(
                {
                    "name": (glyph_ref or {}).get("name") or glyph_key,
                    "key": glyph_key,
                    "board": board_name,
                    "priority": "high",
                    "description": clean_markup((glyph_ref or {}).get("desc")),
                    "bonus": clean_markup((glyph_ref or {}).get("bonus")),
                    "legendary_bonus": clean_markup((glyph_ref or {}).get("legendaryBonus")),
                    "threshold_requirements": (glyph_ref or {}).get("threshold_requirements") or [],
                    "notes": f"socket={socket}; rank={(board.get('glyphRank') or {}).get(socket)}",
                }
            )

    return boards, glyphs, legendary_nodes, unresolved


def convert_variant(raw: dict[str, Any], variant: dict[str, Any], variant_index: int, refs: dict[str, Any]) -> dict[str, Any]:
    core_skills, unresolved_skills = convert_core_skills(variant, refs)
    gear, aspects, uniques, unresolved_gear = convert_gear(variant, refs)
    paragon_boards, glyphs, legendary_nodes, unresolved_paragon = convert_paragon(raw, variant, refs)
    variant_notes = clean_html(variant.get("desc"))
    top_notes = clean_html(raw.get("description"))

    missing_fields: list[str] = []
    for field_name, value in {
        "core_skills": core_skills,
        "gear": gear,
        "aspects": aspects,
        "affix_priorities": convert_affix_priorities(variant, refs),
        "paragon_boards": paragon_boards,
    }.items():
        if not value:
            missing_fields.append(field_name)

    unresolved = sorted(set(unresolved_skills + unresolved_gear + unresolved_paragon))

    return {
        "source_url": f"https://www.d2core.com/d4/planner/{raw.get('_id')}",
        "game_version": "",
        "season": f"Season {raw.get('season')}" if raw.get("season") else "",
        "class": raw.get("char") or "",
        "build_name": f"{raw.get('title') or 'Untitled'} - {variant.get('name') or f'Variant {variant_index}'}",
        "build_type": raw.get("scene") or [],
        "core_skills": core_skills,
        "passive_skills": [],
        "gear": gear,
        "aspects": aspects,
        "uniques": uniques,
        "affix_priorities": convert_affix_priorities(variant, refs),
        "paragon_boards": paragon_boards,
        "glyphs": glyphs,
        "legendary_nodes": legendary_nodes,
        "author_notes": [
            note
            for note in [
                top_notes,
                variant_notes,
                f"Converted from d2core raw build id={raw.get('_id')} variant_index={variant_index}.",
            ]
            if note
        ],
        "ai_analysis_status": {
            "status": "ready_for_analysis" if not unresolved else "needs_review",
            "missing_fields": missing_fields,
            "last_analyzed_at": None,
            "notes": "Auto-converted from d2core raw JSON. Review inferred roles and affix priorities before using as final analysis data.",
        },
        "_conversion_quality": {
            "variant_index": variant_index,
            "variant_name": variant.get("name") or "",
            "unresolved_references": unresolved,
            "warnings": [
                "passive_skills are not separated from active skill data yet.",
                "affix_priorities are collected from gear mods and are not true ranked priorities.",
                "skill roles are inferred from tags/ranks and should be manually reviewed.",
            ],
        },
    }


def write_build(build: dict[str, Any], output_dir: Path, raw_id: str, variant_index: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9_-]+", "_", raw_id or "d2core")
    path = output_dir / f"d2core_{safe_id}_variant_{variant_index}.json"
    path.write_text(json.dumps(build, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert local d2core raw JSON into MVP Build JSON.")
    parser.add_argument("--raw", default=str(DEFAULT_RAW_PATH), help="Path to d2core raw JSON.")
    parser.add_argument("--variant", type=int, help="Variant index to convert. Converts all variants when omitted.")
    parser.add_argument("--reference-dir", default=str(DEFAULT_REFERENCE_DIR), help="Reference data directory.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for converted JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = resolve_path(args.raw)
    reference_dir = resolve_path(args.reference_dir)
    output_dir = resolve_path(args.out_dir)

    raw = load_raw_build(raw_path)
    refs = load_references(reference_dir)
    variants = raw.get("variants") or []
    if not variants:
        raise SystemExit("error: no variants found in raw build")

    indices = [args.variant] if args.variant is not None else list(range(len(variants)))
    for index in indices:
        if index < 0 or index >= len(variants):
            raise SystemExit(f"error: variant index out of range: {index}")
        build = convert_variant(raw, variants[index], index, refs)
        output_path = write_build(build, output_dir, raw.get("_id") or "d2core", index)
        unresolved_count = len(build["_conversion_quality"]["unresolved_references"])
        print(f"wrote: {output_path} unresolved_references={unresolved_count}")


if __name__ == "__main__":
    main()
