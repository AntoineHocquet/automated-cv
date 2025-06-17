from langdetect import detect
from backend.llm_config import llm_gemini

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"

def translate_if_needed(text: str, source_lang="de", target_lang="en") -> str:
    detected = detect_language(text)
    if detected != source_lang:
        return text  # Return unchanged

    prompt = f"""Translate the following job advertisement from {source_lang} to {target_lang}.
Preserve structure and tone. Do not add explanations.

--- TEXT START ---
{text}
--- TEXT END ---
"""
    result = llm_gemini.invoke(prompt)
    return f"[This ad was originally in {source_lang}. Translated by Gemini.]\n\n{result.content}"
