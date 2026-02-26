# Release Checklist

## Pre-release checks

- [ ] Create a fresh virtualenv and install dependencies with `pip install -r requirements.txt`.
- [ ] Run `python3 bootstrap.py` successfully on a clean checkout.
- [ ] Run `make test` and confirm all required tests pass.
- [ ] Start API (`make run-api`) and verify `/health` and `/config` endpoints.
- [ ] Start Streamlit (`make run-ui`) and validate Q&A flow.

## Emacs integration checks

- [ ] Load `elisp/emacs-explained.el` from a clean Emacs session.
- [ ] Validate `M-x emacs-explained-ask` returns an answer.
- [ ] Validate `M-x emacs-explained-explain-region` on sample elisp.
- [ ] Validate `M-x emacs-explained-explain-defun` and symbol workflow.

## Source and licensing checks

- [ ] Confirm source catalog entries and license metadata are current.
- [ ] Confirm non-commercial sources remain opt-in for distribution.
- [ ] Re-check `SOURCES.md` for licensing accuracy.

## Packaging and documentation

- [ ] Ensure `.gitignore` excludes local artifacts (`data/`, envs, caches).
- [ ] Ensure README setup and API examples match current behavior.
- [ ] Tag release and include notable provider/runtime changes.
