import argparse
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_CATALOG = BASE_DIR / "resources" / "source_catalog.json"
DEFAULT_MANIFEST = BASE_DIR / "resources" / "resource_manifest.json"
DEFAULT_SOURCE_DIR = BASE_DIR / "data" / "sources"


def _looks_noncommercial(license_name: str) -> bool:
    return "noncommercial" in license_name.lower() or "by-nc" in license_name.lower()


def load_catalog(path: Path) -> list:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Catalog must be a JSON array")
    return data


def should_include(entry: dict, include_noncommercial: bool, include_all: bool) -> bool:
    if include_all:
        return True
    if not entry.get("enabled_by_default", False):
        return False
    if _looks_noncommercial(entry.get("license", "")) and not include_noncommercial:
        return False
    return True


def download(url: str, destination: Path, force: bool = False) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        return

    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def build_manifest_entries(selected: list, source_dir: Path) -> list:
    entries = []
    for entry in selected:
        filename = entry["filename"]
        rel_path = source_dir.relative_to(BASE_DIR) / filename
        entries.append(
            {
                "id": entry["id"],
                "path": str(rel_path),
                "type": entry.get("type", "pdf"),
                "description": entry.get("description", ""),
            }
        )
    return entries


def validate_entry(entry: dict) -> None:
    required = ["id", "filename", "url", "license"]
    missing = [key for key in required if not entry.get(key)]
    if missing:
        raise ValueError(f"Catalog entry missing required fields {missing}: {entry}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download configured source docs and generate resource manifest."
    )
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR))
    parser.add_argument(
        "--include-noncommercial",
        action="store_true",
        help="Include sources marked non-commercial.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all sources in the catalog regardless of enabled_by_default.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even if they already exist.",
    )
    args = parser.parse_args()

    catalog = load_catalog(Path(args.catalog))
    source_dir = Path(args.source_dir)

    selected = []
    for entry in catalog:
        validate_entry(entry)
        if should_include(entry, args.include_noncommercial, args.all):
            selected.append(entry)

    if not selected:
        raise ValueError("No sources selected. Adjust flags or catalog settings.")

    for entry in selected:
        filename = entry["filename"]
        url = entry["url"]

        download(url, source_dir / filename, force=args.force)
        print(f"Ready: {filename}")

    manifest_entries = build_manifest_entries(selected, source_dir)
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest_entries, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote manifest with {len(manifest_entries)} sources to {manifest_path}")


if __name__ == "__main__":
    main()
