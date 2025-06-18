import os
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.letter import LetterSpec
from backend.tex_generator import generate_letter, render_cover_letter_tex


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
        language="english",
        source="Indeed",
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

    # print type
    print(f"\nLetter type: {type(result)}")

    # print dump
    print(f"\nLetter dump: {result.model_dump()}")

    # print all fields in a for loop
    print("\nLetter content:")
    for field, value in result.model_dump().items():
        print(f"- {field}: {value}")

    assert isinstance(result, LetterSpec)
    assert isinstance(result.introduction, str) and result.introduction.strip()
    assert isinstance(result.body, str) and result.body.strip()
    assert isinstance(result.closing, str) and result.closing.strip()


def dummy_filled_spec():
    return LetterSpec(
        introduction="Hello, I'm Ada Lovelace.",
        body="I'm passionate about Machine Learning and AI." \
        "I'm writing to apply for the Machine Learning Engineer position at FutureTech, as advertised." \
        " I am excited to contribute my skills and experience in mathematics, programming,"
        " and innovation to your team. As a BSc Mathematics graduate with a portfolio of machine learning" \
        " projects (<https://ada.dev>), I am confident that I can bring a unique blend of hard"
        " and soft skills to your company." \
        "My passion for AI and machine learning has led me to develop a strong foundation in Python and" \
        " machine learning algorithms. I am particularly proud of my accomplishments as an inventor of algorithms," \
        " which I believe demonstrates my creativity and problem-solving abilities. In addition, I am a strong team player," \
        " having worked on collaborative projects throughout my academic and professional career.I am fluent in English and French," \
        " which I believe would be an asset in working with international teams and clients. I am eager to bring my enthusiasm" \
        " for AI and innovation to FutureTech, and I am confident that I can make a valuable contribution to your team.",
        closing="Best regards, Ada Lovelace",
        style="professional",
        length="medium",
        paragraphs="3",
        idea="enthusiasm for AI",
        size="12pt",
        font="palatino"
    )


def test_render_cover_letter_tex():
    candidate = dummy_candidate()
    job = dummy_job()
    filled_spec = dummy_filled_spec()

    # delete the file if already exists, and prints message if previous file was succesfully removed
    if os.path.exists("output/ada_letter.tex"):
        os.remove("output/ada_letter.tex")
    print("\nPrevious file removed. Tests now begins.")

    # Call the function
    render_cover_letter_tex(candidate, job, filled_spec, output_path = "output/ada_letter.tex")
    if os.path.exists("output/ada_letter.tex"):
        print("File created successfully.")
    else:
        print("File creation failed.")

    # Check if the file exists
    assert os.path.exists("output/ada_letter.tex")