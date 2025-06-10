# backend/tex_generator.py

import os
from jinja2 import Environment, FileSystemLoader
from backend.llm_config import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from backend.models.job import Job
from backend.models.candidate import Candidate


def generate_letter_body(candidate: Candidate, job: Job) -> str:
    """Use an LLM to generate a tailored cover letter body."""
    prompt = PromptTemplate.from_template("""
You are writing a short and compelling cover letter for a job application.

Candidate profile:
{candidate_profile}

Job ad:
{job_description}

Write a short paragraph that fits as the body of a LaTeX cover letter. Make it natural, confident, and tailored to the job.
""")

    chain: Runnable = prompt | llm
    response = chain.invoke({
        "candidate_profile": candidate.to_prompt_chunk(),
        "job_description": job.raw_text
    })

    return response.content.strip()


def render_cover_letter_tex(candidate: Candidate, job: Job, output_path="output/cover_letters/letter.tex"):
    """Generate .tex cover letter using LLM body + template."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    letter_body = generate_letter_body(candidate, job)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("cover_template.tex.j2")

    tex_output = template.render(
        name=candidate.name,
        body=letter_body
        # Add more fields here as needed from candidate
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex_output)

    print(f"✅ LaTeX cover letter written to {output_path}")
