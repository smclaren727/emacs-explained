import argparse
import json
import shutil
from pathlib import Path

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

BASE_DIR = Path(__file__).parent
DEFAULT_MANIFEST = BASE_DIR / "resources" / "resource_manifest.json"
DEFAULT_DB_DIR = BASE_DIR / "emacs_db"


def load_manifest(manifest_path: Path) -> list:
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Manifest not found at {manifest_path}. Create it to list your resources."
        )

    with manifest_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Manifest must be a JSON array of resource objects.")

    return data


def load_resource(resource: dict) -> list:
    resource_id = resource.get("id", "unknown-resource")
    raw_path = resource.get("path")
    resource_type = resource.get("type", "").lower()

    if not raw_path:
        raise ValueError(f"Resource '{resource_id}' is missing required field: path")

    full_path = (BASE_DIR / raw_path).resolve()
    if not full_path.exists():
        raise FileNotFoundError(f"Resource path not found: {raw_path}")

    if resource_type == "pdf" or full_path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(full_path))
    else:
        loader = TextLoader(str(full_path), encoding="utf-8")

    docs = loader.load()
    for doc in docs:
        doc.metadata["resource_id"] = resource_id
        doc.metadata["resource_path"] = str(raw_path)
        doc.metadata["resource_description"] = resource.get("description", "")

    return docs


def build_index(manifest_path: Path, db_dir: Path, reset: bool = True) -> None:
    resources = load_manifest(manifest_path)

    all_docs = []
    for resource in resources:
        all_docs.extend(load_resource(resource))

    if not all_docs:
        raise ValueError("No documents were loaded from the manifest.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
    chunks = splitter.split_documents(all_docs)

    if reset and db_dir.exists():
        shutil.rmtree(db_dir)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(db_dir),
    )

    print(f"Indexed {len(chunks)} chunks from {len(resources)} resources into {db_dir}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or rebuild the local Emacs knowledge index."
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="Path to resource manifest JSON file.",
    )
    parser.add_argument(
        "--db-dir",
        default=str(DEFAULT_DB_DIR),
        help="Path to Chroma persist directory.",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not delete the existing index before adding documents.",
    )
    args = parser.parse_args()

    build_index(
        manifest_path=Path(args.manifest),
        db_dir=Path(args.db_dir),
        reset=not args.no_reset,
    )


if __name__ == "__main__":
    main()
