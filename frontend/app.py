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
from backend.tex_generator import generate_letter, render_cover_letter_tex
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

# --- Load existing profile into session state at first app load ---
if "candidate" not in st.session_state and os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        st.session_state["candidate"] = Candidate.from_dict(json.load(f))

# --- Initialize spec and persistent font-related parameters ---
if "spec" not in st.session_state:
    st.session_state["spec"] = LetterSpec()
spec = st.session_state["spec"]

if "font_size" not in st.session_state:
    st.session_state["font_size"] = "12pt"
if "font_scale" not in st.session_state:
    st.session_state["font_scale"] = 0.75
if "font_family" not in st.session_state:
    st.session_state["font_family"] = "default"

# --- Form for Candidate Profile ---
with st.form("candidate_form"):
    default_data = st.session_state["candidate"].model_dump() if "candidate" in st.session_state else {
        "name": "",
        "personal_data": {"email": "", "phone": "", "address": ""},
        "hard_skills": [],
        "soft_skills": [],
        "portfolio_links": [],
        "education": [],
        "languages_spoken": [],
        "miscellaneous": ""
    }

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

    # --- Submit Button ---
    submitted = st.form_submit_button("\U0001F4BE Save Profile")

# --- If submitted: save Candidate Profile and display summary ---
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
    st.session_state["candidate"] = candidate
    st.success("✅ Candidate profile saved!")
    st.markdown("### LLM Prompt Summary")
    st.info(candidate.to_prompt_chunk())

elif "candidate" in st.session_state:
    candidate = st.session_state["candidate"]
    st.markdown("### LLM Prompt Summary")
    st.info(candidate.to_prompt_chunk())
else:
    candidate = Candidate.from_dict(default_data)
    st.warning("⚠️ Candidate and letter fields are set to default.")

# --- Preview Letter Customization Fields ---
st.divider()
st.header("\U0001F9E0 Customize Your Cover Letter")

spec.style = st.selectbox("Writing style", ["enthusiastic", "confident", "factual", "cold"], index=1)
spec.length = st.selectbox("Length", ["succint", "normal", "thorough"], index=1)
spec.paragraphs = st.slider("Number of paragraphs", min_value=1, max_value=6, value=3)
spec.idea = st.text_input("Idea to convey (optional)", value="")

# --- Upload a New Job Ad ---
st.divider()
st.header("\U0001F4E4 Upload New Job Ad (.txt)")
uploaded_file = st.file_uploader("Upload a job description (.txt)", type=["txt"])

if uploaded_file:
    ads_path = "ads"
    os.makedirs(ads_path, exist_ok=True)
    save_path = os.path.join(ads_path, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File '{uploaded_file.name}' uploaded to ads/ folder.")
    st.session_state.preview_ready = False  # Reset preview when a new file is uploaded

# --- Generate Cover Letter ---
st.divider()
st.header("\U0001F4C4 Generate Cover Letter")

raw_job_files = sorted([f for f in glob.glob("ads/*.txt") if os.path.isfile(f)])
raw_job_file = st.selectbox("Select a job ad", raw_job_files)

if st.button("\U0001F680 Generate Preview", type="primary"):
    st.session_state.preview_ready = True

# --- Main logic ---
if st.session_state.get("preview_ready", False):
    if raw_job_file:
        raw_job_text = open(raw_job_file, encoding="utf-8").read()
        job = Job(raw_text=raw_job_text)
        job.translate_if_needed()

        if job.language in ["french", "german"]:
            st.info(f"✅ Job ad was detected as {job.language} and translated to English for internal processing.")

        # Store filled_job in st.session_state to avoid recomputing
        if "filled_job" not in st.session_state:
            st.session_state.filled_job = Job.populate_from_llm(raw_text=job.raw_text)
        filled_job = st.session_state.filled_job

        st.header("\U0001F4DD Job Ad LLM Preprocessing:")
        filled_job.language = job.language
        st.markdown(" **Ad Language**: " + filled_job.language)
        st.markdown(" **Ad Keywords**: " + ", ".join(filled_job.keywords))
        st.markdown(" **Job Title**: " + filled_job.title)
        st.markdown(" **Company**: " + filled_job.company_name)
        st.markdown(" **Post Date**: " + filled_job.post_date)

        filenamebody = f"{to_snakecase(filled_job.company_name)}-{to_snakecase(filled_job.title)}-{today()}"
        job_filename = filenamebody + ".json"
        spec_filename = filenamebody + "_spec.json"
        tex_path = f"output/cover_letters/{filenamebody}.tex"
        pdf_path = tex_path.replace(".tex", ".pdf")

        with open(os.path.join("data/jobs", job_filename), "w", encoding="utf-8") as jf:
            json.dump(filled_job.model_dump(), jf, indent=2)

        #  Generate filled_spec and persist it in st.session_state after it’s created once.
        if "filled_spec" not in st.session_state:
            st.session_state.filled_spec = generate_letter(candidate, filled_job, spec)
        filled_spec = st.session_state.filled_spec


        with open(os.path.join("data/letters", spec_filename), "w", encoding="utf-8") as sf:
            json.dump(spec.model_dump(), sf, indent=2)
        st.success(f"✅ Cover letter preview successfully generated and saved to data/letters/{spec_filename}")
        st.markdown("### \U0001F4DD Edit and Approve Preview")

        # --- Preview Letter Customization Fields ---
        intro = st.text_area("Introduction", value=filled_spec.introduction, height=100, key="edit_intro")
        body = st.text_area("Body", value=filled_spec.body, height=200, key="edit_body")
        closing = st.text_area("Closing", value=filled_spec.closing, height=100, key="edit_closing")

        # --- Post-preview font and size customization ---
        st.markdown("### \U0001F4DD Customize LaTeX Output")
        size = st.selectbox("Font size", ["9pt", "10pt", "11pt", "12pt"], index=3, key="font_size")
        scale = st.slider("Scale", min_value=0.4, max_value=0.9, value=0.75, step=0.01, key="font_scale")
        font = st.selectbox("Font family", ["default", "times", "fourier", "euler"], index=0, key="font_family")

        # --- Post-preview language customization ---
        st.markdown("### \U0001F4DD Customize Language")
        fit_to_ad_language = st.checkbox(
            "🌍 Generate the letter in the language of the ad? (French or German are supported.)",
            value=False
        )

        # --- Export to LaTeX Cover Letter ---
        if st.button("\U0001F4DD Save and export to PDF", type="primary"):
            # update letter fields
            filled_spec.introduction = intro
            filled_spec.body = body
            filled_spec.closing = closing

            # Update letter spec with .TEX related fields
            filled_spec.size = st.session_state["font_size"]
            filled_spec.scale = st.session_state["font_scale"]
            filled_spec.font = st.session_state["font_family"]

            # Overwrite existing spec
            with open(os.path.join("data/letters", spec_filename), "w", encoding="utf-8") as sf:
                json.dump(filled_spec.model_dump(), sf, indent=2)
            st.info(f"Letter spec (editable preview) saved to data/letters/{spec_filename}")

            render_cover_letter_tex(candidate, filled_job, filled_spec, output_path=tex_path, fit_ad_language=fit_to_ad_language)
            st.success(f"✅ LaTeX cover letter saved to {tex_path}")

            compile_tex_to_pdf(tex_path)
            st.success("✅ LaTeX letter generated!")

            if os.path.exists(tex_path):
                with open(tex_path, "rb") as f:
                    st.session_state["tex_bytes"] = f.read()

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.session_state["pdf_bytes"] = f.read()

        # --- Always show download buttons if bytes exist ---
        if "tex_bytes" in st.session_state:
            st.download_button("📄 Download LaTeX (.tex)", st.session_state["tex_bytes"],
                               file_name=os.path.basename(tex_path), mime="text/plain")

        if "pdf_bytes" in st.session_state:
            st.download_button("📥 Download PDF", st.session_state["pdf_bytes"],
                               file_name=os.path.basename(pdf_path), mime="application/pdf")
    else:
        st.warning("⚠️ Please select a job ad before generating a preview.")
