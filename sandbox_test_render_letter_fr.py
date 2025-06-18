from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.letter import LetterSpec
from backend.tex_generator import render_cover_letter_tex

def main():
    candidate = Candidate(
        name="Antoine Hocquet",
        personal_data={
            "address": "42 Rue des Mathématiques, Paris",
            "phone": "+33 1 23 45 67 89",
            "email": "antoine@example.com"
        },
        hard_skills=["Python", "Machine Learning"],
        soft_skills=["Problem solving", "Team collaboration"],
        portfolio_links=["https://github.com/antoinehocquet"],
        education=["PhD in Applied Mathematics - École Polytechnique"],
        languages_spoken=["French", "English", "German"]
    )


    job = Job(
        company_name="Institut de Physique Théorique",
        title="Chercheur Postdoctoral",
        raw_text="Bonjour, je suis un texte en français pour tester la détection de langue automatique."
    )

    spec = LetterSpec(
        introduction="Madame, Monsieur,",
        body="Je suis vivement intéressé par ce poste qui correspond à mon expertise en mathématiques appliquées.",
        closing="Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées."
    )

    render_cover_letter_tex(
        candidate=candidate,
        job=job,
        spec=spec,
        output_path="output/dummy_letter_fr.tex",
        fit_ad_language=True
    )

if __name__ == "__main__":
    main()
