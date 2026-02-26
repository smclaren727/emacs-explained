# Implementation Checklist: Hybrid Emacs Assistant

This checklist merges both tracks:
- Hybrid architecture (Emacs Lisp client + Python backend)
- Self-contained local default model with optional providers

## Phase 1: Backend provider abstraction

- [ ] Create `backend/` package layout.
  - [ ] Add `backend/config.py`
  - [ ] Add `backend/providers/base.py`
  - [ ] Add `backend/providers/local_small.py`
  - [ ] Add `backend/providers/ollama_provider.py`
  - [ ] Add `backend/providers/openai_provider.py`
  - [ ] Add `backend/providers/factory.py`
- [ ] Move answer generation logic out of `emacs_assistant.py` into `backend/service.py`.
- [ ] Define stable interfaces.
  - [ ] `class ChatProvider: generate(prompt: str, system: str | None = None) -> str`
  - [ ] `class EmbeddingProvider: embed(texts: list[str]) -> list[list[float]]`
- [ ] Add provider selection via env/config.
  - [ ] `MODEL_PROVIDER=local_small|ollama|openai`
  - [ ] `CHAT_MODEL=...`
  - [ ] `EMBEDDING_MODEL=...`
- [ ] Keep current behavior working behind the new interface.

## Phase 2: Local default model (self-contained)

- [ ] Add model catalog file: `resources/model_catalog.json`.
  - [ ] Include one default small instruct model entry.
  - [ ] Include checksum, URL, local filename, context length, and recommended settings.
- [ ] Add installer script: `sync_models.py`.
  - [ ] Download model to `data/models/`
  - [ ] Verify checksum
  - [ ] Skip download if already present unless `--force`
- [ ] Add local runtime wrapper in `backend/providers/local_small.py`.
  - [ ] Option A: use `llama.cpp` server mode HTTP endpoint
  - [ ] Option B: invoke local binary directly (if endpoint unavailable)
- [ ] Add startup health checks.
  - [ ] Validate model file exists
  - [ ] Validate runtime is reachable

## Phase 3: Unified bootstrap/setup flow

- [ ] Add `bootstrap.py` to run first-time setup.
  - [ ] `sync_sources.py`
  - [ ] `sync_models.py`
  - [ ] `prepare_data.py`
  - [ ] backend health check
- [ ] Add one command in README:
  - [ ] `python3 bootstrap.py`
- [ ] Improve error messages for missing keys/runtime/files.

## Phase 4: API layer for Emacs client

- [ ] Add lightweight API server: `backend/api.py` (FastAPI).
- [ ] Add endpoints.
  - [ ] `POST /ask` `{question, skill_level}`
  - [ ] `POST /explain-region` `{code, language, context}`
  - [ ] `GET /health`
  - [ ] `GET /config`
- [ ] Return structured responses.
  - [ ] `answer`
  - [ ] `sources`
  - [ ] `provider`
  - [ ] `model`
- [ ] Refactor `streamlit_app.py` to consume the same backend service methods.

## Phase 5: Emacs Lisp client package

- [ ] Create package directory: `elisp/`.
  - [ ] `elisp/emacs-explained.el`
  - [ ] `elisp/emacs-explained-http.el`
  - [ ] `elisp/emacs-explained-ui.el`
- [ ] Implement commands.
  - [ ] `emacs-explained-ask`
  - [ ] `emacs-explained-explain-region`
  - [ ] `emacs-explained-explain-defun`
  - [ ] `emacs-explained-explain-symbol-at-point`
- [ ] Add customizable variables.
  - [ ] `emacs-explained-api-url`
  - [ ] `emacs-explained-skill-level`
  - [ ] `emacs-explained-auto-cite-sources`
- [ ] Add response buffer mode.
  - [ ] dedicated buffer `*Emacs Explained*`
  - [ ] source links and copy action

## Phase 6: Quality, safety, and observability

- [ ] Add prompt templates directory: `prompts/`.
  - [ ] `prompts/ask.txt`
  - [ ] `prompts/explain_region.txt`
- [ ] Add prompt guardrails.
  - [ ] plain-language first
  - [ ] define jargon
  - [ ] include actionable steps
- [ ] Add structured logging.
  - [ ] request id
  - [ ] provider/model used
  - [ ] retrieval chunk count
- [ ] Add optional telemetry-off local metrics file in `data/logs/`.

## Phase 7: Testing and release hygiene

- [ ] Add tests directory: `tests/`.
  - [ ] provider factory tests
  - [ ] source/model sync tests
  - [ ] retrieval integration smoke test
  - [ ] API endpoint tests
- [ ] Add Emacs Lisp ERT smoke tests for core commands.
- [ ] Add `Makefile` targets.
  - [ ] `make bootstrap`
  - [ ] `make run-api`
  - [ ] `make run-ui`
  - [ ] `make test`
- [ ] Add release checklist in `RELEASE.md`.

## Immediate execution order (recommended)

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6
7. Phase 7

## Definition of done for MVP

- [ ] User can run one setup command on a fresh machine.
- [ ] User can ask a question and explain selected elisp from inside Emacs.
- [ ] Default local model works without API keys.
- [ ] User can switch to Ollama or OpenAI via config only.
- [ ] Answers include source citations.
