from setuptools import setup, find_packages

setup(
    name="automated_cv_app",
    version="0.1",
    packages=find_packages(),  # Automatically finds backend/, frontend/ if needed
    install_requires=[
        "streamlit",
        "langchain",
        "mistralai",
        "tenacity",
        "python-dotenv"
        # Add more as needed (or rely on requirements.txt)
    ],
    entry_points={
        "console_scripts": [
            "automated-cv=frontend.app:main",  # optional CLI entry point if needed
        ]
    },
)
