# backend/llm_config.py

import os
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables (e.g. MISTRAL_API_KEY, GEMINI_API_KEY)
load_dotenv()

# Initialize Mistral LLM globally
llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small",  # or "mistral-medium", "mistral-tiny"
    temperature=0.3
)

# Initialize Gemini LLM globally
llm_gemini = ChatGoogleGenerativeAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-flash-latest",
    temperature=0.3,
    convert_system_message_to_human=True, # recommended for Gemini
)