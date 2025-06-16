import os
import re
from jinja2 import Environment, FileSystemLoader
from backend.llm_config import llm
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from backend.models.letter import LetterSpec
from backend.models.job import Job
from backend.models.candidate import Candidate
from langchain_core.outputs import Generation


def sanitize_output_text(json_text: str) -> str:
    """
    Sanitize malformed JSON text from LLM output, especially field names with escaped characters.
    Example: 'raw\\_text' → 'raw_text'
    """
    return re.sub(r'\\_', '_', json_text)


def generate_letter(candidate: Candidate, job: Job, spec: LetterSpec) -> LetterSpec:
    """
    Generate structured letter content using LLM with robust parsing and sanitization.
    """
    # Step 1: Setup prompt template
    prompt = PromptTemplate.from_template("""
You are writing a personalized cover letter for a job application.

Candidate profile:
{candidate_profile}

Job ad:
{job_description}

Tone: {style}
Length: {length}
Paragraphs: {paragraphs}
Idea to emphasize: {idea}

Use these preferences to generate a JSON object with:
- introduction (a greeting)
- body (main letter content)
- closing (sign-off)

{format_instructions}
""")

    # Step 2: Set up parser and chain
    parser = PydanticOutputParser(pydantic_object=LetterSpec)
    chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm

    # Step 3: Invoke LLM
    raw_output = chain.invoke({
        "candidate_profile": candidate.to_prompt_chunk(),
        "job_description": job.raw_text,
        "style": spec.style,
        "length": spec.length,
        "paragraphs": spec.paragraphs,
        "idea": spec.idea
    })

    # Step 4: Extract and sanitize text output
    raw_text = raw_output.content if hasattr(raw_output, "content") else str(raw_output)
    clean_text = sanitize_output_text(raw_text)

    # Step 5: Parse the clean output into a LetterSpec object
    return parser.parse(clean_text)


def render_cover_letter_tex(
    candidate: Candidate,
    job: Job,
    spec: LetterSpec,
    output_path: str = "output/cover_letters/letter.tex"
):
    """
    Generate .tex cover letter using structured LLM output and a Jinja2 LaTeX template.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    filled_spec = generate_letter(candidate, job, spec)

    if not filled_spec.closing.strip():
        print("⚠️ Closing is missing, using candidate name instead.")
        filled_spec.closing = f"Sincerely yours,\n{candidate.name}"

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("cover_template.tex.j2")

    tex_output = template.render(
        name=candidate.name,
        address=candidate.personal_data.get("address", ""),
        phone=candidate.personal_data.get("phone", ""),
        email=candidate.personal_data.get("email", ""),
        company_name=job.company_name or "Company",
        title=job.title or "Open",
        introduction=filled_spec.introduction.strip(),
        body=filled_spec.body.strip(),
        closing=filled_spec.closing.strip(),
        size=spec.size,
        font=spec.font
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex_output)

    print(f"✅ LaTeX cover letter written to {output_path}")
