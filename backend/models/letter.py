# backend/models/letter.py

from pydantic import BaseModel, Field
from typing import Optional
from backend.llm_config import llm_gemini
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from backend.models.schemas import ChampsTraduits, UebersetzteAbschnitte  # translation schemas


class LetterSpec(BaseModel):
    # --- Content fields (filled by LLM) ---
    introduction: str = Field(
        default="Dear Hiring Manager,",
        description="A formal greeting line for the letter, e.g., 'Dear Hiring Manager,'"
        )
    body: str = Field(
        default="",
        description="The main text content of the cover letter."
        )
    closing: str = Field(
        default="Sincerely, Antoine Hocquet",
        description="The polite sign-off line of the letter, e.g., 'Sincerely, John Doe'"
        )

    # --- User formatting preferences ---
    size: Optional[str] = Field(
        default="12pt",
        description="Font size of the letter (e.g., 9pt, 10pt, 11pt, 12pt)."
        )
    scale: Optional[float] = Field(
        default=0.75,
        description="Scale factor for the letter (e.g., 0.8, 0.9, 1.0)."
        )
    font: Optional[str] = Field(
        default="default",
        description="LaTeX font family: default, times, fourier, or euler."
        )

    # --- User generation preferences (affects LLM prompt) ---
    style: Optional[str] = Field(
        default="confident",
        description="The tone of the letter (e.g., enthusiastic, confident, factual, cold)."
    )
    length: Optional[str] = Field(
        default="normal",
        description="How detailed the letter should be: succint, normal, or thorough."
    )
    paragraphs: Optional[int] = Field(
        default=3,
        description="Number of body paragraphs the letter should contain (separated by a plain line skip)."
    )
    idea: Optional[str] = Field(
        default="",
        description="Optional idea or message to emphasize in the letter (e.g., international experience, team leadership)."
    )

    # --- Methods ---
    def translate_to_french(self) -> None:
        parser = PydanticOutputParser(pydantic_object=ChampsTraduits)
        prompt = PromptTemplate.from_template(
            """
            You are given the following fields of a cover letter written in English:

            INTRODUCTION:
            {introduction}

            BODY:
            {body}

            CLOSING:
            {closing}

            Translate them idiomatically into French. Preserve the structure, tone, and formality.
            Do not add extra commentary. Return valid JSON in the format:
            {format_instructions}
            """
        )

        full_prompt = prompt.format_prompt(
            introduction=self.introduction,
            body=self.body,
            closing=self.closing,
            format_instructions=parser.get_format_instructions()
        )

        result = llm_gemini.invoke(full_prompt.to_string())
        parsed = parser.parse(result.content)

        self.introduction = parsed.ouverture
        self.body = parsed.corps
        self.closing = parsed.fermeture

        print("\nTranslated cover letter:")
        print("INTRODUCTION:", self.introduction)
        print("BODY:", self.body)
        print("CLOSING:", self.closing)

        return


    def translate_to_german(self) -> None:
            parser = PydanticOutputParser(pydantic_object=UebersetzteAbschnitte)
            prompt = PromptTemplate.from_template(
                """
                You are given the following fields of a cover letter written in English:

                INTRODUCTION:
                {introduction}

                BODY:
                {body}

                CLOSING:
                {closing}

                Translate them idiomatically into German. Preserve the structure, tone, and formality.
                Do not add extra commentary. Return valid JSON in the format:
                {format_instructions}
                """
            )

            full_prompt = prompt.format_prompt(
                introduction=self.introduction,
                body=self.body,
                closing=self.closing,
                format_instructions=parser.get_format_instructions()
            )

            result = llm_gemini.invoke(full_prompt.to_string())
            parsed = parser.parse(result.content)

            self.introduction = parsed.einleitung
            self.body = parsed.hauptteil
            self.closing = parsed.schlussformel

            print("\nTranslated cover letter:")
            print("INTRODUCTION:", self.introduction)
            print("BODY:", self.body)
            print("CLOSING:", self.closing)

            return
