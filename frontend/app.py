import sys
import os
sys.path.append(os.path.abspath("."))
import re
import json
import glob
from datetime import date

import streamlit as st

from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.letter import LetterSpec
from backend.tex_generator import render_cover_letter_tex
from backend.compile_tex import compile_tex_to_pdf

# --- UTILS ---
def to_snakecase(text):
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s\-]+", "_", text.strip())
    return text.lower()

def today():
    return date.today().strftime("%Y_%m_%d")

# --- PATHS ---
DATA_PATH = "data/profiles"
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs("data/jobs", exist_ok=True)
os.makedirs("data/letters", exist_ok=True)
PROFILE_FILE = os.path.join(DATA_PATH, "params.json")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Candidate Profile Setup", page_icon="\U0001F9E0")
st.title("\U0001F9E0 Candidate Profile Setup")

# --- Load existing profile ---
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        default_data = json.load(f)
else:
    default_data = {
        "name": "",
        "personal_data": {"email": "", "phone": "", "address": ""},
        "hard_skills": [],
        "soft_skills": [],
        "portfolio_links": [],
        "education": [],
        "languages_spoken": [],
        "miscellaneous": ""
    }

# --- Form ---
with st.form("candidate_form"):
    name = st.text_input("Full Name", value=default_data["name"])
    email = st.text_input("Email", value=default_data["personal_data"].get("email", ""))
    phone = st.text_input("Phone Number", value=default_data["personal_data"].get("phone", ""))
    address = st.text_area("Address", value=default_data["personal_data"].get("address", ""))

    st.markdown("#### Hard Skills (comma-separated)")
    hard_skills = st.text_input("Hard Skills", value=", ".join(default_data["hard_skills"]), key="hard_skills_input")

    st.markdown("#### Soft Skills (comma-separated)")
    soft_skills = st.text_input("Soft Skills", value=", ".join(default_data["soft_skills"]), key="soft_skills_input")

    st.markdown("#### Portfolio Links (comma-separated)")
    portfolio_links = st.text_input("Portfolio Links", value=", ".join(default_data["portfolio_links"]), key="portfolio_input")

    st.markdown("#### Education (one per line)")
    education = st.text_area("Education", value="\n".join(default_data["education"]))

    st.markdown("#### Languages Spoken (comma-separated)")
    languages_spoken = st.text_input("Languages Spoken", value=", ".join(default_data["languages_spoken"]), key="langs_input")

    misc = st.text_area("Miscellaneous Notes", value=default_data["miscellaneous"])

    # --- Customization Fields ---
    st.divider()
    st.header("\U0001F9E0 Customize Your Cover Letter")

    col1, col2 = st.columns(2)

    with col1:
        size = st.selectbox("Font size", ["9pt", "10pt", "11pt", "12pt"], index=3)
        font = st.selectbox("Font family", ["default", "times", "fourier", "euler"], index=0)

    with col2:
        style = st.selectbox("Writing style", ["enthusiastic", "confident", "factual", "cold"], index=1)
        length = st.selectbox("Length", ["succint", "normal", "thorough"], index=1)
        paragraphs = st.slider("Number of paragraphs", min_value=1, max_value=6, value=3)
        idea = st.text_input("Idea to convey (optional)", value="")

    submitted = st.form_submit_button("\U0001F4BE Save Profile")

# --- Upload a New Job Ad ---
st.divider()
st.header("\U0001F4E4 Upload New Job Ad (.txt)")
uploaded_file = st.file_uploader("Upload a job description (.txt)", type=["txt"])

if uploaded_file is not None:
    ads_path = "ads"
    os.makedirs(ads_path, exist_ok=True)
    save_path = os.path.join(ads_path, uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File '{uploaded_file.name}' uploaded to ads/ folder.")

# --- Generate Cover Letter ---
st.divider()
st.header("\U0001F4C4 Generate Cover Letter")

raw_job_files = sorted([f for f in glob.glob("ads/*.txt") if os.path.isfile(f)])
raw_job_file = st.selectbox("Select a job ad", raw_job_files)

fit_to_ad_language = st.checkbox(
    "🌍 Generate the letter in the language of the ad (if supported)?",
    value=False
    )
generate = st.button("\U0001F680 Generate Latex Cover Letter")

if generate:
    if raw_job_file:
        candidate = Candidate.from_json(PROFILE_FILE)
        raw_job_text = open(raw_job_file, encoding="utf-8").read()
        job = Job(raw_text=raw_job_text)
        job.translate_if_needed()

        if job.language in ["french", "german"]:
            st.info(f"✅ Job ad was detected as {job.language} and translated to English for internal processing.")
        
        # Populate the job object with Mistral-based method and displays the results
        filled_job= Job.populate_from_llm(raw_text=job.raw_text)
        filled_job.language = job.language
        
        st.markdown("\U0001F4DD **Language**: " + filled_job.language)
        st.markdown("\U0001F4DD **Keywords**: " + ", ".join(filled_job.keywords))
        st.markdown("\U0001F4DD **Title**: " + filled_job.title)
        st.markdown("\U0001F4DD **Company**: " + filled_job.company_name)
        st.markdown("\U0001F4DD **Post Date**: " + filled_job.post_date)

        # Defines a generic filename based on extracted job title, company name and current date
        filenamebody = f"{to_snakecase(filled_job.company_name)}-{to_snakecase(filled_job.title)}-{today()}"

        # Uses the generic filename to save the populated job instance as a .json file
        job_filename = filenamebody + ".json"
        with open(os.path.join("data/jobs", job_filename), "w", encoding="utf-8") as jf:
            json.dump(filled_job.model_dump(), jf, indent=2)

        # Instantiates a LetterSpec with user specified parameters
        spec = LetterSpec(
            introduction="",
            body="",
            closing="",
            size=size,
            font=font,
            style=style,
            length=length,
            paragraphs=paragraphs,
            idea=idea
        )

        # Uses similar generic filename as before to save the letter spec as .JSON
        spec_filename = filenamebody + "_spec.json"
        with open(os.path.join("data/letters", spec_filename), "w", encoding="utf-8") as sf:
            json.dump(spec.model_dump(), sf, indent=2)

        # Defines the output path for the LaTeX cover letter based on the generic filename
        tex_path = f"output/cover_letters/{filenamebody}.tex"

        # Creates the LaTeX cover letter
        render_cover_letter_tex(
            candidate,
            filled_job,
            spec,
            output_path=tex_path,
            fit_ad_language=fit_to_ad_language
        )

        # Compiles the LaTeX cover letter to PDF and displays a success message
        compile_tex_to_pdf(tex_path)
        st.success("✅ LaTeX letter generated!")
        
        # TEX
        if os.path.exists(tex_path):
            with open(tex_path, "rb") as f:
                st.session_state["tex_bytes"] = f.read()

        # PDF
        pdf_path = tex_path.replace(".tex", ".pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.session_state["pdf_bytes"] = f.read()

    else:
        st.warning("⚠️ Please select a job ad before generating the PDF.")

# --- Always show download buttons if bytes exist ---
if "tex_bytes" in st.session_state:
    st.download_button("📄 Download LaTeX (.tex)", st.session_state["tex_bytes"],
                       file_name=os.path.basename("output/cover_letters/letter_streamlit.tex"), mime="text/plain")

if "pdf_bytes" in st.session_state:
    st.download_button("📥 Download PDF", st.session_state["pdf_bytes"],
                       file_name=os.path.basename("output/cover_letters/letter_streamlit.pdf"), mime="application/pdf")

if submitted:
    candidate = Candidate(
        name=name,
        personal_data={"email": email, "phone": phone, "address": address},
        hard_skills=[s.strip() for s in hard_skills.split(",") if s.strip()],
        soft_skills=[s.strip() for s in soft_skills.split(",") if s.strip()],
        portfolio_links=[s.strip() for s in portfolio_links.split(",") if s.strip()],
        education=[e.strip() for e in education.splitlines() if e.strip()],
        languages_spoken=[l.strip() for l in languages_spoken.split(",") if l.strip()],
        miscellaneous=misc.strip()
    )

    candidate.to_json(PROFILE_FILE)
    st.success("✅ Candidate profile saved!")
    st.markdown("### LLM Prompt Summary")
    st.info(candidate.to_prompt_chunk())
