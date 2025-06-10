# backend/llm_config.py

import os
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

# Initialize LLM globally
llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small",  # or "mistral-medium", "mistral-tiny"
    temperature=0.3
)
