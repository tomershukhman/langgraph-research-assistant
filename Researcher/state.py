import operator
from typing import List, Annotated, Optional
from pydantic import BaseModel, Field
from .Analysts.schemas import Analyst


class ResearchInput(BaseModel):
    """Input schema for the main Researcher graph - what the user provides."""

    topic: str = Field(description="Research topic to investigate")


class ResearchOutput(BaseModel):
    """Output schema for the main Researcher graph - what it returns."""

    final_report: str = Field(
        default="",
        description="Final research report with introduction, content, and conclusion",
    )


class ResearchGraphState(BaseModel):
    """Internal overall state for the main Researcher graph."""

    topic: str = Field(description="Research topic to investigate")
    analysts: Optional[List[Analyst]] = Field(
        default=None,
        description="List of AI analyst personas generated for the research",
    )
    sections: Annotated[list, operator.add] = Field(
        default_factory=list,
        description="Interview sections from all analysts (accumulated via Send API)",
    )
    introduction: str = Field(
        default="", description="Introduction section of the final report"
    )
    content: str = Field(
        default="", description="Main content section of the final report"
    )
    conclusion: str = Field(
        default="", description="Conclusion section of the final report"
    )
    final_report: str = Field(
        default="", description="Complete final report combining all sections"
    )
