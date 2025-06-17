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
from backend.translate import translate_if_needed

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

job_files = sorted([f for f in glob.glob("ads/*.txt") if os.path.isfile(f)])
job_file = st.selectbox("Select a job ad", job_files)
# generate_german = st.checkbox("🇩🇪 Also generate letter in German?", value=False)
generate = st.button("\U0001F680 Generate Latex Cover Letter")

if generate:
    if job_file:
        candidate = Candidate.from_json(PROFILE_FILE)
        job_text = open(job_file, encoding="utf-8").read()
        translated_text = translate_if_needed(job_text)

        if translated_text != job_text:
            with open(job_file, "w", encoding="utf-8") as f:
                f.write(translated_text)
            st.info("✅ Job ad was detected as German and translated to English.")

        job = Job.populate_from_llm(raw_text=translated_text)

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

        filenamebody = f"{to_snakecase(job.company_name)}-{to_snakecase(job.title)}-{today()}"
        job_filename = filenamebody + ".json"
        with open(os.path.join("data/jobs", job_filename), "w", encoding="utf-8") as jf:
            json.dump(job.model_dump(), jf, indent=2)

        spec_filename = filenamebody + "_spec.json"
        with open(os.path.join("data/letters", spec_filename), "w", encoding="utf-8") as sf:
            json.dump(spec.model_dump(), sf, indent=2)

        tex_path = f"output/cover_letters/{filenamebody}.tex"
        render_cover_letter_tex(candidate, job, spec, output_path=tex_path)
        compile_tex_to_pdf(tex_path)

        pdf_path = tex_path.replace(".tex", ".pdf")
        st.success("✅ LaTeX letter generated!")

        if os.path.exists(tex_path):
            with open(tex_path, "rb") as f:
                st.session_state["tex_bytes"] = f.read()

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.session_state["pdf_bytes"] = f.read()

        # # Optional: generate German translation of letter
        # if generate_german and "tex_bytes" in st.session_state:
        #     tex_de = translate_if_needed(st.session_state["tex_bytes"].decode("utf-8"), source_lang="en", target_lang="de")
        #     tex_de_path = tex_path.replace(".tex", "_de.tex")
        #     with open(tex_de_path, "w", encoding="utf-8") as f:
        #         f.write(tex_de)
        #     compile_tex_to_pdf(tex_de_path)
        #     pdf_de_path = tex_de_path.replace(".tex", ".pdf")
        #     if os.path.exists(pdf_de_path):
        #         pdf_bytes_de = open(pdf_de_path, "rb").read()
        #         st.download_button("📥 Download German PDF", pdf_bytes_de, file_name=os.path.basename(pdf_de_path))

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
