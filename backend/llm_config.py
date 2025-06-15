# backend/llm_config.py

import os
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI

# Load environment variables (e.g. MISTRAL_API_KEY), which are set in the .env file
load_dotenv()

# Initialize LLM globally
llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small",  # or "mistral-medium", "mistral-tiny"
    temperature=0.3
)
