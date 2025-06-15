import tempfile
import json
from backend.models.candidate import Candidate


def sample_candidate_dict():
    return {
        "name": "Ada Lovelace",
        "personal_data": {
            "email": "ada@example.com",
            "phone": "+49 123 456789",
            "address": "London, UK"
        },
        "hard_skills": ["Python", "Machine Learning", "Docker"],
        "soft_skills": ["Communication", "Problem Solving"],
        "portfolio_links": ["https://github.com/ada", "https://ada.dev"],
        "education": ["M.Sc. in Computer Science", "B.Sc. in Mathematics"],
        "languages_spoken": ["English", "French"],
        "miscellaneous": "First programmer in history."
    }


def test_candidate_init_and_repr():
    data = sample_candidate_dict()
    candidate = Candidate(**data)

    assert candidate.name == "Ada Lovelace"
    assert "ada@" in repr(candidate)


def test_to_prompt_chunk():
    candidate = Candidate(**sample_candidate_dict())
    prompt = candidate.to_prompt_chunk()

    assert "Ada Lovelace" in prompt
    assert "Machine Learning" in prompt
    assert "Portfolio" in prompt


def test_to_latex_macro_dict():
    candidate = Candidate(**sample_candidate_dict())
    macros = candidate.to_latex_macro_dict()

    assert macros["CANDIDATE_NAME"] == "Ada Lovelace"
    assert "Python" in macros["CANDIDATE_HARDSKILLS"]
    assert "London" in macros["CANDIDATE_ADDRESS"]


def test_serialization_to_dict_and_json_roundtrip():
    original = Candidate(**sample_candidate_dict())

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        original.to_json(tmp.name)
        tmp.seek(0)
        loaded = Candidate.from_json(tmp.name)

    assert loaded == original


def test_missing_misc_is_handled_gracefully():
    minimal = sample_candidate_dict()
    del minimal["miscellaneous"]

    candidate = Candidate(**minimal)
    assert candidate.miscellaneous == ""
