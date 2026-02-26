PYTHON ?= python3

.PHONY: bootstrap run-api run-ui test

bootstrap:
	$(PYTHON) bootstrap.py

run-api:
	uvicorn backend.api:app --host 127.0.0.1 --port 8000

run-ui:
	streamlit run streamlit_app.py

test:
	$(PYTHON) -m unittest discover -s tests -v
