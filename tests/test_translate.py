import pytest
from backend.translate import detect_language, translate_if_needed

# Test detect_language
@pytest.mark.parametrize("text,expected_lang", [
    ("Dies ist eine Stellenanzeige.", "de"),
    ("This is a job ad.", "en"),
    ("Ceci est une offre d'emploi.", "fr"),
])
def test_detect_language(text, expected_lang):
    print(f"Text: {text}")
    detected = detect_language(text)
    print(f"Detected language: {detected}")
    assert detected == expected_lang

# Test translation behavior (mocked to avoid real API calls)
def test_translate_if_needed_no_translation(monkeypatch):
    sample_text = "This is an English job ad."

    def fake_detect(text):
        return "en"

    monkeypatch.setattr("backend.translate.detect_language", fake_detect)
    result = translate_if_needed(sample_text)
    assert result == sample_text

def test_translate_if_needed_translates(monkeypatch):
    german_text = "Dies ist eine Stellenanzeige."

    def fake_detect(text):
        return "de"

    class FakeLLM:
        def invoke(self, prompt):
            class Result:
                content = "This is a translated job ad."
            return Result()

    monkeypatch.setattr("backend.translate.detect_language", fake_detect)
    monkeypatch.setattr("backend.translate.llm_gemini", FakeLLM())

    result = translate_if_needed(german_text)
    assert result.startswith("[This ad was originally in de.")
    assert "translated job ad" in result

def test_translate_german_to_english():
    german_text = """
    Wir suchen eine/n motivierte/n Data Scientist (m/w/d), der/die mit Leidenschaft an datengetriebenen Lösungen arbeitet.
    """
    translated = translate_if_needed(german_text)

    print("\nOriginal (German):\n", german_text.strip())
    print("\nTranslation (English):\n", translated.strip())

    assert "Translated" in translated or "We are looking" in translated
    assert translated != german_text
    print("\n✅ Translation test passed.")

