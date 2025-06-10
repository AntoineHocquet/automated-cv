# backend/models/job.py

import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from backend.llm_config import llm


class Job:
    def __init__(self, raw_text: str, source: str = ""):
        self.raw_text = raw_text.strip()
        self.source = source

        # Attributes to be filled by LLM
        self.company_name = None
        self.title = None
        self.post_date = None
        self.keywords = []

    def to_document(self) -> Document:
        """Return a LangChain-compatible document."""
        return Document(
            page_content=self.raw_text,
            metadata={
                "source": self.source,
                "company_name": self.company_name,
                "title": self.title,
                "post_date": self.post_date
            }
        )

    # Use tenacity to retry on parse or runtime errors
    @retry(
        stop=stop_after_attempt(3),         # max 3 tries
        wait=wait_exponential(multiplier=1, min=2, max=10), # exponential backoff: 2s, 4s, 8s
        retry=retry_if_exception_type((json.JSONDecodeError, Exception)), # retry on parse or runtime errors
        reraise=True
    )
    def populate_from_llm(self):
        """
        Uses an LLM to fill structured attributes of the job.
        Decorated with tenacity to retry on parse or runtime errors.
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import Runnable
        from backend.llm_config import llm

        prompt = PromptTemplate.from_template("""
        You are given the full text of a job advertisement:

        {ad}

        Extract the following fields and return them in JSON format:
        - Company name
        - Job title
        - Posting date (YYYY-MM-DD if mentioned)
        - 5–10 keywords

        Return valid JSON like:
        {{
        "company_name": "...",
        "title": "...",
        "post_date": "...",
        "keywords": ["...", "..."]
        }}
        """)

        chain: Runnable = prompt | llm
        response = chain.invoke({"ad": self.raw_text})

        try:
            cleaned = response.content.strip()

            # Remove Markdown code block markers if present
            if cleaned.startswith("```json"):
                cleaned = cleaned.removeprefix("```json").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned.removesuffix("```").strip()

            parsed = json.loads(cleaned)
            self.company_name = parsed.get("company_name")
            self.title = parsed.get("title")
            self.post_date = parsed.get("post_date")
            self.keywords = parsed.get("keywords", [])
        except json.JSONDecodeError:
            print("⚠️ Failed to decode JSON from LLM response.")
            print("🔍 Raw output was:\n", response.content)
            raise


    def __repr__(self):
        return f"Job(company='{self.company_name}', title='{self.title}', post_date={self.post_date})"
