# Makefile for automated-cv project

# Set PYTHONPATH to current directory and run tests
test:
	PYTHONPATH=$(shell pwd) pytest

# Optional: install dependencies inside venv
install:
	pip install -r requirements.txt

# Run your app (if you have a CLI entry point later)
run:
	PYTHONPATH=$(shell pwd) streamlit run frontend/app.py

# Clean up .pyc and __pycache__
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + -o -name "*.pyc" -delete
