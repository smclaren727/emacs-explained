# Emacs Learning Assistant

A local RAG-based assistant for learning Emacs in plain language.

## What this project does

- Answers Emacs questions using your local documentation sources.
- Explains concepts in beginner-friendly terms.
- Shows which source files were used for each answer.
- Lets you add more learning resources over time.

## Current architecture

- `prepare_data.py`: builds the vector index from a resource manifest.
- `sync_sources.py`: downloads cataloged sources and writes the resource manifest.
- `emacs_assistant.py`: runs retrieval + LLM answer generation.
- `streamlit_app.py`: simple UI for asking questions.
- `resources/source_catalog.json`: source URLs + license metadata.
- `resources/resource_manifest.json`: list of source files to index.
- `SOURCES.md`: licensing notes for bundled/cataloged documents.
- `emacs_db/`: persisted vector database.

## First-time setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Download allowed/default sources and generate the manifest:

```bash
python3 sync_sources.py
```

4. Build/rebuild the vector index:

```bash
python3 prepare_data.py
```

## Add new resources

1. Add new entries to `resources/source_catalog.json`.
2. Re-run `python3 sync_sources.py`.
3. Re-run `python3 prepare_data.py`.

Example catalog entry:

```json
{
  "id": "my-guide",
  "filename": "my-guide.pdf",
  "url": "https://example.com/my-guide.pdf",
  "type": "pdf",
  "description": "My Emacs guide",
  "license": "CC BY 4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "enabled_by_default": false
}
```

Optional flags:

- `--manifest <path>`: use a different manifest file.
- `--db-dir <path>`: use a different vector DB location.
- `--no-reset`: append into existing DB instead of replacing.

Source sync flags:

- `--include-noncommercial`: include catalog entries with non-commercial licenses.
- `--all`: include all catalog entries (including disabled-by-default).
- `--force`: re-download files even if they already exist.

## Run the app

```bash
streamlit run streamlit_app.py
```

## Notes

- This app uses Ollama model `deepseek-r1` and embedding model `all-MiniLM-L6-v2`.
- Make sure your local environment has required packages installed.
- Review `SOURCES.md` before redistributing source docs.
