from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_PATH = ROOT_DIR / "data" / "converted" / "d2core_1STz_variant_0.json"


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Build JSON root must be an object.")
    return data


def list_quality_findings(build: dict[str, Any]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    suggestions: list[str] = []

    status = build.get("ai_analysis_status") or {}
    missing_fields = status.get("missing_fields") or []
    if missing_fields:
        warnings.append(f"ai_analysis_status.missing_fields is not empty: {', '.join(missing_fields)}")

    conversion_quality = build.get("_conversion_quality") or {}
    unresolved = conversion_quality.get("unresolved_references") or []
    if unresolved:
        warnings.append(f"unresolved reference keys: {', '.join(str(item) for item in unresolved[:20])}")

    if not build.get("passive_skills"):
        warnings.append("passive_skills is empty.")
        suggestions.append("Separate passive skill nodes from raw skill data or fill important passives manually.")

    role_review = [
        skill.get("name")
        for skill in build.get("core_skills", [])
        if skill.get("role") in {"main_damage_or_core", "support", "generator_or_basic"}
    ]
    if role_review:
        suggestions.append(
            "Review inferred skill roles for: " + ", ".join(str(name) for name in role_review[:10])
        )

    for group in build.get("affix_priorities", []):
        notes = group.get("notes") or ""
        if "not a verified priority ranking" in notes:
            suggestions.append("Review affix_priorities because current order is auto-collected from gear mods.")
            break

    if not build.get("glyphs"):
        warnings.append("glyphs is empty.")

    if not build.get("legendary_nodes"):
        warnings.append("legendary_nodes is empty.")

    if not build.get("author_notes"):
        warnings.append("author_notes is empty.")

    return warnings, suggestions


def print_summary(build_path: Path, build: dict[str, Any], warnings: list[str], suggestions: list[str]) -> None:
    print(f"quality checked: {build_path}")
    print(f"build_name: {build.get('build_name')}")
    print(f"class: {build.get('class')}")
    print(f"core_skills: {len(build.get('core_skills') or [])}")
    print(f"gear: {len(build.get('gear') or [])}")
    print(f"aspects: {len(build.get('aspects') or [])}")
    print(f"uniques: {len(build.get('uniques') or [])}")
    print(f"affix_priority_groups: {len(build.get('affix_priorities') or [])}")
    print(f"paragon_boards: {len(build.get('paragon_boards') or [])}")
    print(f"glyphs: {len(build.get('glyphs') or [])}")
    print(f"legendary_nodes: {len(build.get('legendary_nodes') or [])}")

    for warning in warnings:
        print(f"warning: {warning}")

    for suggestion in suggestions:
        print(f"suggestion: {suggestion}")

    if warnings:
        print("quality_status: needs_review")
    else:
        print("quality_status: good")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check converted Build JSON data quality.")
    parser.add_argument(
        "build",
        nargs="?",
        default=str(DEFAULT_BUILD_PATH),
        help="Path to converted Build JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_path = resolve_path(args.build)
    try:
        build = load_json(build_path)
    except FileNotFoundError:
        print(f"error: file not found: {build_path}")
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {build_path}: {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        print(f"error: {exc}")
        raise SystemExit(1)

    warnings, suggestions = list_quality_findings(build)
    print_summary(build_path, build, warnings, suggestions)


if __name__ == "__main__":
    main()
