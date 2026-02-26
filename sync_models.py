import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_CATALOG = BASE_DIR / "resources" / "model_catalog.json"
DEFAULT_MODEL_DIR = BASE_DIR / "data" / "models"


def load_catalog(path: Path) -> list:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Model catalog must be a JSON array")
    return data


def validate_entry(entry: dict) -> None:
    required = ["id", "filename", "url", "provider"]
    missing = [key for key in required if not entry.get(key)]
    if missing:
        raise ValueError(f"Model entry missing required fields {missing}: {entry}")


def should_include(entry: dict, include_all: bool) -> bool:
    if include_all:
        return True
    return bool(entry.get("enabled_by_default", False))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, destination: Path, force: bool = False) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        return

    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download configured local models into data/models."
    )
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    parser.add_argument("--all", action="store_true", help="Include all catalog entries.")
    parser.add_argument("--force", action="store_true", help="Re-download existing files.")
    parser.add_argument(
        "--skip-checksum",
        action="store_true",
        help="Skip checksum verification even when sha256 is provided.",
    )
    args = parser.parse_args()

    catalog = load_catalog(Path(args.catalog))
    model_dir = Path(args.model_dir)

    selected = []
    for entry in catalog:
        validate_entry(entry)
        if should_include(entry, args.all):
            selected.append(entry)

    if not selected:
        raise ValueError("No models selected. Adjust flags or catalog settings.")

    for entry in selected:
        filename = entry["filename"]
        url = entry["url"]
        expected_sha = str(entry.get("sha256", "")).strip().lower()
        file_path = model_dir / filename

        download(url, file_path, force=args.force)

        if expected_sha and not args.skip_checksum:
            actual_sha = sha256_file(file_path)
            if actual_sha != expected_sha:
                raise ValueError(
                    f"Checksum mismatch for {filename}: expected {expected_sha}, got {actual_sha}"
                )

        if not expected_sha:
            print(f"Ready: {filename} (no sha256 configured)")
        else:
            print(f"Ready: {filename} (sha256 verified)")

    print(f"Model sync complete. Files available in {model_dir}")


if __name__ == "__main__":
    main()
