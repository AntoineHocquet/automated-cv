import pytest
from backend.models.letter import LetterSpec
from backend.llm_config import llm_gemini

def mock_invoke_french(prompt):
    class MockResponse:
        content = """
        {
            "ouverture": "Bonjour",
            "corps": "Ceci est le corps de la lettre traduit en français.",
            "fermeture": "Cordialement"
        }
        """
    return MockResponse()


def test_translate_to_french(monkeypatch):
    monkeypatch.setattr(type(llm_gemini), "invoke", lambda self, prompt: mock_invoke_french(prompt))

    letter = LetterSpec(
        introduction="Dear Hiring Manager,",
        body="This is the body of the letter in English.",
        closing="Sincerely, Antoine Hocquet"
    )

    letter.translate_to_french()

    print(letter.introduction)
    print(letter.body)
    print(letter.closing)

    assert letter.introduction == "Bonjour"
    assert letter.body == "Ceci est le corps de la lettre traduit en français."
    assert letter.closing == "Cordialement"

def mock_invoke_german(prompt):
    class MockResponse:
        content = """
        {
            "einleitung": "Sehr geehrte Damen und Herren,",
            "hauptteil": "Ich habe Ihre Ausschreibung mit großem Interesse gelesen.",
            "schlussformel": "Mit freundlichen Grüssen"
        }
        """
    return MockResponse()

def test_translate_to_german(monkeypatch):
    monkeypatch.setattr(type(llm_gemini), "invoke", lambda self, prompt: mock_invoke_german(prompt))

    letter = LetterSpec(
        introduction="Dear Hiring Manager,",
        body="I am writing to express my interest in your job offer.",
        closing="Sincerely, Antoine Hocquet"
    )

    letter.translate_to_german()

    assert letter.introduction == "Sehr geehrte Damen und Herren,"
    assert letter.body == "Ich habe Ihre Ausschreibung mit großem Interesse gelesen."
    assert letter.closing == "Mit freundlichen Grüssen"