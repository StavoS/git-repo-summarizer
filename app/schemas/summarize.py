from pydantic import BaseModel, HttpUrl, Field
from typing import List


class SummarizeRequest(BaseModel):
    github_url: HttpUrl
    advanced: bool = Field(
        default=False,
        description="Enable advanced mode to fetch actual file contents for better analysis (uses more tokens)"
    )


class SummarizeResponse(BaseModel):
    summary: str
    technologies: List[str]
    structure: str
