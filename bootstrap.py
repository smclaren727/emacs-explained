import argparse
import subprocess
import sys


def run_step(cmd: list[str]) -> None:
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap local Emacs assistant setup.")
    parser.add_argument(
        "--include-noncommercial",
        action="store_true",
        help="Include non-commercial source documents during source sync.",
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip local model download step.",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip vector index rebuild step.",
    )
    args = parser.parse_args()

    sync_sources_cmd = [sys.executable, "sync_sources.py"]
    if args.include_noncommercial:
        sync_sources_cmd.append("--include-noncommercial")

    run_step(sync_sources_cmd)

    if not args.skip_models:
        run_step([sys.executable, "sync_models.py"])

    if not args.skip_index:
        run_step([sys.executable, "prepare_data.py"])

    print("Bootstrap complete.")


if __name__ == "__main__":
    main()
