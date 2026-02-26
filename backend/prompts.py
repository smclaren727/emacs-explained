from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def ask_prompt_template() -> str:
    return load_prompt("ask.txt")


def explain_region_prompt_template() -> str:
    return load_prompt("explain_region.txt")
