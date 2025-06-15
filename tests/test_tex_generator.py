from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.letter import LetterSpec
from backend.tex_generator import generate_letter


def dummy_candidate():
    return Candidate(
        name="Ada Lovelace",
        personal_data={"email": "ada@lovelace.org", "address": "London", "phone": "+49 123 456789"},
        hard_skills=["Python", "Machine Learning"],
        soft_skills=["Creativity", "Teamwork"],
        portfolio_links=["https://ada.dev"],
        education=["BSc Mathematics"],
        languages_spoken=["English", "French"],
        miscellaneous="Inventor of algorithms"
    )


def dummy_job():
    return Job(
        raw_text="We are looking for a Machine Learning Engineer at FutureTech. "
                 "The ideal candidate is passionate about AI and innovation.",
        source="test_input.txt",
        company_name="FutureTech",
        title="Machine Learning Engineer",
        post_date="2024-06-15",
        keywords=["AI", "Python", "Deep Learning"]
    )


def dummy_spec():
    return LetterSpec(
        style="professional",
        length="medium",
        paragraphs="3",
        idea="enthusiasm for AI",
        size="11pt",
        font="palatino"
    )


def test_generate_letter_returns_valid_spec():
    candidate = dummy_candidate()
    job = dummy_job()
    spec = dummy_spec()

    result = generate_letter(candidate, job, spec)

    print("\n","Letter content:","\n")
    print(result.introduction, "\n", result.body, "\n", result.closing, "\n")

    assert isinstance(result.introduction, str) and result.introduction.strip()
    assert isinstance(result.body, str) and result.body.strip()
    assert isinstance(result.closing, str) and result.closing.strip()
