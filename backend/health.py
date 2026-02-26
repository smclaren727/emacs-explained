from pathlib import Path

from backend.config import AppConfig


def check_local_small_prereqs(config: AppConfig) -> None:
    model_path = Path(config.local_model_file)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Local model file not found: {model_path}. Run `python3 sync_models.py` first."
        )
