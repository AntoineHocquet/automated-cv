# setup.py

from setuptools import setup, find_packages

setup(
    name="automated_cv_app",
    version="0.1",
    packages=find_packages(),  # Automatically finds backend/, frontend/ if needed
    install_requires=[
        "langchain",
        "mistralai",
        "streamlit",
        "tenacity",
        "jinja2",
        "python-dotenv"
    ],
    extras_require={
        "gemini": [
            "langchain-google-genai==2.1.5"
        ]
    },
    entry_points={
        "console_scripts": [
            "automated-cv=frontend.app:main",
        ]
    },
)