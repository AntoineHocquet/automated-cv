from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.tex_generator import render_cover_letter_tex
from backend.compile_tex import compile_tex_to_pdf

candidate = Candidate.from_json("data/profiles/params.json")
job_text = open("ads/zalando_applied_scientist.txt").read()
job = Job(job_text, source="zalando_applied_scientist.txt")
job.populate_from_llm()

tex_path = "output/cover_letters/test_letter.tex"
render_cover_letter_tex(candidate, job, output_path=tex_path)

compile_tex_to_pdf(tex_path)
