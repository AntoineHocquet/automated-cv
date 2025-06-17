# Makefile for automated-cv

run:
	PYTHONPATH=$(shell pwd) streamlit run frontend/app.py

test:
	PYTHONPATH=$(shell pwd) pytest -s -v

minimal:
	PYTHONPATH=$(shell pwd) python3 minimal.py

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + -o -name "*.pyc" -delete

reset:
	rm -rf venv
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
