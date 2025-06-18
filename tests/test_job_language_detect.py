import pytest
from backend.models.job import Job
from backend.llm_config import llm_gemini

# -----------------------------
# Supported Language Detection
# -----------------------------
@pytest.mark.parametrize(
    "text, expected_language",
    [
        ("Bonjour, je suis un texte en français.", "french"),
        ("Hallo, ich bin ein deutscher Text.", "german"),
        ("Hello, I am an English sentence.", "english"),
    ]
)
def test_translate_if_needed_language_detection_only(monkeypatch, text, expected_language):
    # Patch translation to skip actual call
    class FakeLLM:
        def invoke(self, prompt):
            class Response:
                content = "Dummy English translation."
            return Response()
    monkeypatch.setattr("backend.models.job.llm_gemini", FakeLLM())

    job = Job(raw_text=text)
    job.translate_if_needed()
    assert job.language == expected_language
    if expected_language != "english":
        assert job.raw_text == "Dummy English translation."
    else:
        assert job.raw_text == text

# -----------------------------
# Unsupported Language
# -----------------------------
@pytest.mark.parametrize("text", [
    "Hola, soy una frase en español.",   # Spanish
    "Ciao, sono un annuncio di lavoro.",  # Italian
    "Olá, esta é uma frase em português."  # Portuguese
])
def test_translate_if_needed_unsupported(monkeypatch, text):
    job = Job(raw_text=text)
    with pytest.raises(ValueError) as exc_info:
        job.translate_if_needed()
    assert "Language '" in str(exc_info.value)

# -----------------------------
# Exception Handling: Empty text
# -----------------------------
def test_translate_if_needed_empty():
    job = Job(raw_text="")
    with pytest.raises(ValueError) as exc_info:
        job.translate_if_needed()
    assert "empty or whitespace-only" in str(exc_info.value)
