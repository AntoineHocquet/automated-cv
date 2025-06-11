# 📄 Automated CV/Cover Letter Generator

Automated cv/cover letter pipeline for online job adds using LangChain and dockerized Latex.
Generate custom, LLM-powered LaTeX cover letters based on structured candidate profiles and job ads — then compile them into beautiful PDF files using Docker.

---

## ✨ Automated Cover Letter Generator

Create personalized, LLM-powered LaTeX cover letters in your browser.  
Customize tone, font, formatting — and download a polished PDF in seconds.

🌍 **[Try the App Here](https://your-username.streamlit.app)**

---

## 🚧 Status: Version 1 Released

✅ Features:
- Streamlit UI for editing your profile
- Upload/select job ads (`.txt`)
- Customize letter style, font, length
- Download PDF generated via LaTeX + Docker

🔜 Coming Soon:
- CV generation and templating
- Google Drive export
- Translations via Gemini API

---

## 🛡️ Privacy Notice

This app does **not track or store** user profiles.  
Your personal data (`params.json`) is stored locally in your browser/session and is **not pushed to GitHub**.

Only job ads in `ads/*.txt` are version-controlled.

---

## 🧪 Run Locally

```bash
git clone https://github.com/AntoineHocquet/automated-cv.git
cd automated-cv
make reset
make run
```

### 🔐 Mistral API Key (required for local use)

To generate real letters using LLMs, you need a free Mistral API key:  
👉 [https://console.mistral.ai](https://console.mistral.ai)

Then set it in a `.env` file located at the root, with the syntax
`MISTRAL_API_KEY=...`