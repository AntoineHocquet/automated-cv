# backend/models/job.py

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import OutputFixingParser, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from backend.llm_config import llm


class Job(BaseModel):
    # Input
    raw_text: str
    source: Optional[str] = ""

    # Output
    company_name: Optional[str] = None
    title: Optional[str] = None
    post_date: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    def to_document(self) -> Document:
        return Document(
            page_content=self.raw_text,
            metadata={
                "source": self.source,
                "company_name": self.company_name,
                "title": self.title,
                "post_date": self.post_date
            }
        )

    @classmethod
    def populate_from_llm(cls, raw_text: str, source: str = "") -> "Job":
        """
        Class method that calls the LLM and returns a validated Job object.
        """
        parser = StructuredOutputParser.from_pexpect(cls)
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)

        prompt = PromptTemplate.from_template("""
        You are given the full text of a job advertisement:

        {ad}

        Extract the following fields and return them in JSON format:
        - Company name
        - Job title
        - Posting date (YYYY-MM-DD if mentioned)
        - 5–10 keywords

        Return valid JSON.
        {format_instructions}
        """)

        chain = prompt.partial(format_instructions=fixing_parser.get_format_instructions()) | llm | fixing_parser
        parsed: Job = chain.invoke({"ad": raw_text})
        parsed.raw_text = raw_text
        parsed.source = source
        return parsed

    def __repr__(self):
        return f"Job(company='{self.company_name}', title='{self.title}', post_date={self.post_date})"
