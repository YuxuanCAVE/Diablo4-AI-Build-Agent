from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_JSON_PATH = ROOT_DIR / "data" / "examples" / "sample_build.json"

EXPECTED_TYPES: dict[str, type | tuple[type, ...]] = {
    "source_url": str,
    "class": str,
    "build_name": str,
    "build_type": list,
    "core_skills": list,
    "gear": list,
    "aspects": list,
    "uniques": list,
    "affix_priorities": list,
    "paragon_boards": list,
    "glyphs": list,
    "legendary_nodes": list,
    "author_notes": list,
}


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


def is_empty_or_todo(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, str):
        return value.strip() == "" or value.strip().upper().startswith("TODO")

    if isinstance(value, list):
        return len(value) == 0

    return False


def validate_build(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field, expected_type in EXPECTED_TYPES.items():
        if field not in data:
            warnings.append(f"Missing important field: {field}")
            errors.append(f"Cannot generate a reliable prompt without field: {field}")
            continue

        value = data[field]
        if not isinstance(value, expected_type):
            expected_name = (
                " or ".join(t.__name__ for t in expected_type)
                if isinstance(expected_type, tuple)
                else expected_type.__name__
            )
            errors.append(
                f"Field '{field}' has wrong type: expected {expected_name}, got {type(value).__name__}"
            )
            continue

        if is_empty_or_todo(value):
            warnings.append(f"Field '{field}' is empty or TODO.")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a Diablo 4 Build JSON file before prompt generation."
    )
    parser.add_argument(
        "build",
        nargs="?",
        default=str(DEFAULT_BUILD_JSON_PATH),
        help="Path to the Build JSON file. Defaults to data/examples/sample_build.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_path = resolve_path(args.build)

    try:
        data = load_json(build_path)
        errors, warnings = validate_build(data)
    except FileNotFoundError:
        print(f"error: file not found: {build_path}")
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {build_path}: {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        print(f"error: {exc}")
        raise SystemExit(1)

    print(f"validated: {build_path}")

    for warning in warnings:
        print(f"warning: {warning}")

    for error in errors:
        print(f"error: {error}")

    if errors:
        print("not ready")
        raise SystemExit(1)

    print("ready")


if __name__ == "__main__":
    main()
