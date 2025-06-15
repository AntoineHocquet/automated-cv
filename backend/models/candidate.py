from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json


class Candidate(BaseModel):
    """A candidate for a job."""
    
    name: str
    personal_data: Dict[str, str]
    hard_skills: List[str]
    soft_skills: List[str]
    portfolio_links: List[str]
    education: List[str]
    languages_spoken: List[str]
    miscellaneous: Optional[str] = Field(default="", description="Extra info like hobbies or distinctions")

    def to_prompt_chunk(self) -> str:
        """Returns a natural-language summary suitable for LLM prompts."""
        return (
            f"{self.name} is a candidate with a background in {', '.join(self.education)}. "
            f"They possess hard skills in {', '.join(self.hard_skills)} and soft skills such as {', '.join(self.soft_skills)}. "
            f"They speak {', '.join(self.languages_spoken)}. "
            f"Portfolio: {', '.join(self.portfolio_links)}. "
            f"Additional notes: {self.miscellaneous}"
        )

    def to_latex_macro_dict(self) -> Dict[str, str]:
        """Returns a dict of key-value pairs for templating LaTeX macros."""
        return {
            "CANDIDATE_NAME": self.name,
            "CANDIDATE_EMAIL": self.personal_data.get("email", ""),
            "CANDIDATE_PHONE": self.personal_data.get("phone", ""),
            "CANDIDATE_ADDRESS": self.personal_data.get("address", ""),
            "CANDIDATE_EDUCATION": " \\\\ ".join(self.education),
            "CANDIDATE_HARDSKILLS": ", ".join(self.hard_skills),
            "CANDIDATE_SOFTSKILLS": ", ".join(self.soft_skills),
            "CANDIDATE_LANGUAGES": ", ".join(self.languages_spoken),
            "CANDIDATE_MISC": self.miscellaneous,
        }

    def to_dict(self) -> Dict:
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> "Candidate":
        return cls(**data)

    @classmethod
    def from_json(cls, path: str) -> "Candidate":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def __repr__(self):
        return f"Candidate({self.name}, {self.personal_data.get('email', 'N/A')})"
