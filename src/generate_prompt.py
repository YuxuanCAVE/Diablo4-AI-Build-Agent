from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_JSON_PATH = ROOT_DIR / "data" / "examples" / "sample_build.json"
PROMPT_TEMPLATE_PATH = ROOT_DIR / "prompts" / "build_analysis_prompt.md"
PLACEHOLDER = "{{BUILD_JSON}}"


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path

    return ROOT_DIR / path


def load_build_json(path: Path) -> str:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return json.dumps(data, ensure_ascii=False, indent=2)


def load_prompt_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def generate_prompt(build_json_path: Path, template_path: Path) -> str:
    build_json = load_build_json(build_json_path)
    template = load_prompt_template(template_path)

    if PLACEHOLDER not in template:
        raise ValueError(f"Prompt template must contain {PLACEHOLDER}")

    return template.replace(PLACEHOLDER, build_json)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Diablo 4 build analysis prompt from a Build JSON file."
    )
    parser.add_argument(
        "--build",
        default=str(DEFAULT_BUILD_JSON_PATH),
        help="Path to the Build JSON file. Defaults to data/examples/sample_build.json.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the generated prompt. Prints to terminal when omitted.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_json_path = resolve_path(args.build)
    prompt = generate_prompt(build_json_path, PROMPT_TEMPLATE_PATH)

    if args.output:
        output_path = resolve_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(prompt, encoding="utf-8")
        print(f"wrote prompt: {output_path}")
        return

    print(prompt)


if __name__ == "__main__":
    main()
