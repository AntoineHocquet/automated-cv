from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.letter import LetterSpec
from backend.tex_generator import render_cover_letter_tex 

def main():
    candidate = Candidate(
        name="Antoine Hocquet",
        personal_data={
            "address": "Humboldtstraße 12, 10115 Berlin",
            "phone": "+49 30 123456",
            "email": "antoine@example.com"
        },
        hard_skills=["Python", "Datenanalyse"],
        soft_skills=["Problemlösung", "Teamarbeit"],
        portfolio_links=["https://github.com/antoinehocquet"],
        education=["PhD in Mathematik – École Polytechnique"],
        languages_spoken=["Deutsch", "Französisch", "Englisch"]
    )

    job = Job(
        company_name="Fraunhofer-Institut",
        title="Data Scientist",
        raw_text="Sehr geehrte Damen und Herren, wir suchen einen erfahrenen Data Scientist mit Kenntnissen in Python und Machine Learning."
    )

    spec = LetterSpec(
        introduction="Dear Hiring Manager,",
        body="I am writing to apply for this role.",
        closing="Sincerely, Antoine Hocquet"
    )

    render_cover_letter_tex(
        candidate=candidate,
        job=job,
        spec=spec,
        output_path="output/dummy_letter_de.tex",
        fit_ad_language=True
    )

if __name__ == "__main__":
    main()
