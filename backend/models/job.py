import re
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.exceptions import OutputParserException
from backend.llm_config import llm


class Job(BaseModel):
    raw_text: str = Field(
        default="",
        description="The full text of the job advertisement."
    )
    source: Optional[str] = Field(
        default="",
        description="The platform on which the ad was found, e.g. Linkedin, Indeed, StepStone etc."
    )
    company_name: Optional[str] = Field(
        default="",
        description="The name of the company."
    )
    title: Optional[str] = Field(
        default="",
        description="The title of the job, e.g. Machine Learning Engineer, Data Scientist, AI Engineer, etc."
    )
    post_date: Optional[str] = Field(
        default="",
        description="The date the job was posted, e.g. 2023-01-01. Write 'Unknown' if unknown."
    )
    keywords: List[str] = Field(
        default=[],
        description="The keywords associated with the job, e.g. ['Python', 'Machine Learning', 'Data Science']"
    )

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
        Tries a fixing parser, and falls back to manual sanitization if needed.
        """
        parser = PydanticOutputParser(pydantic_object=cls)
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

        chain = (
            prompt.partial(format_instructions=fixing_parser.get_format_instructions())
            | llm
            | fixing_parser
        )

        try:
            parsed: Job = chain.invoke({"ad": raw_text})

        except OutputParserException as e:
            faulty_output = e.llm_output if hasattr(e, "llm_output") else ""

            # Clean up: remove escaped underscores
            cleaned_output = faulty_output.replace('\\_', '_')

            # Extract JSON part only (from first '{' to last '}')
            match = re.search(r"\{.*\}", cleaned_output, re.DOTALL)
            if not match:
                raise ValueError(f"Could not extract JSON from:\n{cleaned_output}")

            json_str = match.group(0)

            try:
                json_data = json.loads(json_str)
                parsed = cls(**json_data)
            except Exception as e2:
                raise ValueError(
                    f"Failed to parse sanitized LLM output.\n"
                    f"Original Error: {e}\n"
                    f"Sanitized Error: {e2}\n"
                    f"Sanitized JSON Extract:\n{json_str}"
                )
            
        parsed.raw_text = raw_text
        parsed.source = source

        return parsed

    def __repr__(self):
        return f"Job(company='{self.company_name}', title='{self.title}', post_date={self.post_date})"
