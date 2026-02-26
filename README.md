# Emacs Learning Assistant

A local RAG-based assistant for learning Emacs in plain language.

## What this project does

- Answers Emacs questions using your local documentation sources.
- Explains concepts in beginner-friendly terms.
- Shows which source files were used for each answer.
- Lets you add more learning resources over time.

## Current architecture

- `prepare_data.py`: builds the vector index from a resource manifest.
- `emacs_assistant.py`: runs retrieval + LLM answer generation.
- `streamlit_app.py`: simple UI for asking questions.
- `resources/resource_manifest.json`: list of source files to index.
- `emacs_db/`: persisted vector database.

## Add new resources

1. Put new files in the project (PDF, TXT, MD, org notes, etc.).
2. Add each file to `resources/resource_manifest.json`.
3. Rebuild the index.

Example manifest entry:

```json
{
  "id": "my-notes",
  "path": "resources/my-emacs-notes.md",
  "type": "text",
  "description": "Personal notes about keybindings and workflows"
}
```

## Build/rebuild index

```bash
python3 prepare_data.py
```

Optional flags:

- `--manifest <path>`: use a different manifest file.
- `--db-dir <path>`: use a different vector DB location.
- `--no-reset`: append into existing DB instead of replacing.

## Run the app

```bash
streamlit run streamlit_app.py
```

## Notes

- This app uses Ollama model `deepseek-r1` and embedding model `all-MiniLM-L6-v2`.
- Make sure your local environment has required packages installed.
