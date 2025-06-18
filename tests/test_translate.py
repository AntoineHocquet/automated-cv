import pytest
from backend.models.job import Job


def test_translate_if_needed_no_translation():
    text = "This is an English job ad."
    job = Job(raw_text=text)
    job.translate_if_needed()
    assert job.language == "english"
    assert job.raw_text == text


@pytest.mark.parametrize("text,expected_lang_code", [
    ("Hola, soy un anuncio de trabajo.", "es"),   # Spanish
    ("Ciao, questa è un'offerta di lavoro.", "it"),  # Italian
    ("Olá, esta é uma oferta de emprego.", "pt"),  # Portuguese
])
def test_translate_unsupported_language(text, expected_lang_code):
    job = Job(raw_text=text)
    with pytest.raises(ValueError) as exc_info:
        job.translate_if_needed()
    assert f"Language '{expected_lang_code}'" in str(exc_info.value)


def test_translate_if_needed_translates(monkeypatch):
    text = "Dies ist eine Stellenanzeige."

    class FakeLLM:
        def invoke(self, prompt):
            class Result:
                content = "This is a translated job ad."
            return Result()

    monkeypatch.setattr("backend.models.job.llm_gemini", FakeLLM())

    job = Job(raw_text=text)
    job.translate_if_needed()
    assert job.language == "german"
    assert "translated job ad" in job.raw_text
