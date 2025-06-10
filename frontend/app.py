import streamlit as st
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.tex_generator import render_cover_letter_tex
from backend.compile_tex import compile_tex_to_pdf
import os
import json
import glob



# --- PAGE CONFIG ---
DATA_PATH = "data/profiles"
os.makedirs(DATA_PATH, exist_ok=True)
PROFILE_FILE = os.path.join(DATA_PATH, "params.json")

st.set_page_config(page_title="Candidate Profile Setup", page_icon="🧠")

st.title("🧠 Candidate Profile Setup")

# Load existing data if available
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

    submitted = st.form_submit_button("💾 Save Profile")

# --- Generate Cover Letter ---
st.divider()
st.header("📄 Generate Cover Letter PDF")

# Load job ad list from ads/
job_files = sorted(glob.glob("ads/*.txt"))
job_file = st.selectbox("Select a job ad", job_files)

generate = st.button("🚀 Generate Cover Letter (PDF)")

# --- Generate PDF ---
if generate:
    if job_file:
        candidate = Candidate.from_json("data/profiles/params.json")
        job_text = open(job_file).read()
        job = Job(job_text, source=job_file)
        job.populate_from_llm()

        tex_path = "output/cover_letters/letter_streamlit.tex"
        render_cover_letter_tex(candidate, job, output_path=tex_path)
        compile_tex_to_pdf(tex_path)

        pdf_path = tex_path.replace(".tex", ".pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.success("✅ PDF successfully generated!")
                st.download_button("📥 Download PDF", f, file_name=os.path.basename(pdf_path), mime="application/pdf")
        else:
            st.error("❌ PDF generation failed.")
    else:
        st.warning("⚠️ Please select a job ad before generating the PDF.")


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
