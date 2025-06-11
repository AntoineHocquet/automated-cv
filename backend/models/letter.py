# backend/models/letter.py

from pydantic import BaseModel, Field
from typing import Optional


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
        default="",
        description="The polite sign-off line of the letter, e.g., 'Sincerely, John Doe'"
        )

    # --- User formatting preferences ---
    size: Optional[str] = Field(
        default="11pt",
        description="Font size of the letter (e.g., 9pt, 10pt, 11pt, 12pt)."
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
