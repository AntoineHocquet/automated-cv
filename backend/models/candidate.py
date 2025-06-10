# backend/models/candidate.py

import json
from typing import List, Dict, Optional


class Candidate:
    def __init__(
        self,
        name: str,
        personal_data: Dict[str, str],
        hard_skills: List[str],
        soft_skills: List[str],
        portfolio_links: List[str],
        education: List[str],
        languages_spoken: List[str],
        miscellaneous: Optional[str] = "",
    ):
        self.name = name
        self.personal_data = personal_data
        self.hard_skills = hard_skills
        self.soft_skills = soft_skills
        self.portfolio_links = portfolio_links
        self.education = education
        self.languages_spoken = languages_spoken
        self.miscellaneous = miscellaneous

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
        return {
            "name": self.name,
            "personal_data": self.personal_data,
            "hard_skills": self.hard_skills,
            "soft_skills": self.soft_skills,
            "portfolio_links": self.portfolio_links,
            "education": self.education,
            "languages_spoken": self.languages_spoken,
            "miscellaneous": self.miscellaneous,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data["name"],
            personal_data=data["personal_data"],
            hard_skills=data["hard_skills"],
            soft_skills=data["soft_skills"],
            portfolio_links=data["portfolio_links"],
            education=data["education"],
            languages_spoken=data["languages_spoken"],
            miscellaneous=data.get("miscellaneous", "")
        )

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def __repr__(self):
        return f"Candidate({self.name}, {self.personal_data.get('email')})"
