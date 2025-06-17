import pytest
from backend.models.job import Job 


@pytest.mark.parametrize(
    "text, expected_language",
    [
        ("Bonjour, je suis un texte en français.", "french"),
        ("Hallo, ich bin ein deutscher Text.", "german"),
        ("Hello, I am an English sentence.", "english"),
    ]
)
def test_detect_language_supported(text, expected_language):
    job = Job(raw_text=text)
    detected = job.detect_language()
    print(f"Text: {text}\nDetected: {detected}")
    assert detected == expected_language


def test_detect_language_unsupported():
    job = Job()
    job.raw_text = "Hola, soy una frase en español."  # Spanish text
    language_detected = job.detect_language()
    print("Language detected:", language_detected)
    assert language_detected.startswith("Error: Language '")


def test_detect_language_exception():
    job = Job()
    job.raw_text = None  # Invalid input
    language_detected = job.detect_language()
    print("Language detected:", language_detected)
    assert language_detected == "Error: Unable to detect language."
