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
- `sync_models.py`: downloads local model files from a model catalog.
- `bootstrap.py`: one-command setup for sources, models, and indexing.
- `backend/api.py`: FastAPI layer for Emacs/editor clients.
- `emacs_assistant.py`: runs retrieval + LLM answer generation.
- `streamlit_app.py`: simple UI for asking questions.
- `resources/source_catalog.json`: source URLs + license metadata.
- `resources/model_catalog.json`: local model URLs + metadata.
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

3. Run one-command bootstrap:

```bash
python3 bootstrap.py
```

Optional:

- `python3 bootstrap.py --include-noncommercial` to include non-commercial sources.
- `python3 bootstrap.py --skip-models` to skip local model download.
- `python3 bootstrap.py --skip-index` to skip vector index rebuild.

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

Source sync flags (`sync_sources.py`):

- `--include-noncommercial`: include catalog entries with non-commercial licenses.
- `--all`: include all catalog entries (including disabled-by-default).
- `--force`: re-download files even if they already exist.

Model sync flags (`sync_models.py`):

- `--all`: include all model catalog entries.
- `--force`: re-download model files even if they already exist.
- `--skip-checksum`: skip checksum verification when `sha256` is configured.

## Run the app

```bash
streamlit run streamlit_app.py
```

## Run the API (for Emacs integration)

```bash
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Example API calls:

```bash
curl -s http://127.0.0.1:8000/health
```

```bash
curl -s -X POST http://127.0.0.1:8000/ask \\
  -H \"Content-Type: application/json\" \\
  -d '{\"question\":\"How do I switch buffers?\",\"skill_level\":\"beginner\"}'
```

```bash
curl -s -X POST http://127.0.0.1:8000/explain-region \\
  -H \"Content-Type: application/json\" \\
  -d '{\"code\":\"(setq inhibit-startup-message t)\",\"language\":\"elisp\",\"skill_level\":\"beginner\"}'
```

## Model provider configuration

The backend supports provider selection via environment variables.

- `MODEL_PROVIDER`: `ollama` (default), `openai`, or `local_small`.
- `CHAT_MODEL`: chat model name (default `deepseek-r1` for ollama/openai).
- `EMBEDDING_MODEL`: embedding model name (default `all-MiniLM-L6-v2`).
- `VECTOR_DB_DIR`: vector database path (default `emacs_db`).
- `RETRIEVAL_K`: number of retrieved chunks (default `4`).
- `LOCAL_SMALL_BASE_URL`: OpenAI-compatible local runtime URL (default `http://127.0.0.1:8080/v1`).
- `LOCAL_MODEL_FILE`: expected local model file path (default `data/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`).

Examples:

```bash
MODEL_PROVIDER=ollama CHAT_MODEL=deepseek-r1 streamlit run streamlit_app.py
```

```bash
MODEL_PROVIDER=openai CHAT_MODEL=gpt-4o-mini OPENAI_API_KEY=... streamlit run streamlit_app.py
```

```bash
MODEL_PROVIDER=local_small CHAT_MODEL=tinyllama-1.1b-chat-v1.0.Q4_K_M \
LOCAL_SMALL_BASE_URL=http://127.0.0.1:8080/v1 \
streamlit run streamlit_app.py
```

## Notes

- Default embeddings use `all-MiniLM-L6-v2`.
- `local_small` expects a running OpenAI-compatible local inference server (for example `llama.cpp` server mode).
- Make sure your local environment has required packages installed.
- Review `SOURCES.md` before redistributing source docs.
