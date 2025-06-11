import os
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.tex_generator import render_cover_letter_tex
from backend.compile_tex import compile_tex_to_pdf

ADS_DIR = "ads/"
OUTPUT_DIR = "output/cover_letters/"
PROFILE_PATH = "data/profiles/params.json"

candidate = Candidate.from_json(PROFILE_PATH)

for filename in os.listdir(ADS_DIR):
    if filename.endswith(".txt"):
        ad_path = os.path.join(ADS_DIR, filename)
        with open(ad_path) as f:
            job_text = f.read()

        job = Job(job_text, source=filename)
        job.populate_from_llm()

        base = os.path.splitext(filename)[0]
        tex_path = os.path.join(OUTPUT_DIR, f"{base}.tex")

        render_cover_letter_tex(candidate, job, output_path=tex_path)
        compile_tex_to_pdf(tex_path)
