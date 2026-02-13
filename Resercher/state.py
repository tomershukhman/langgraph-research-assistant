import operator
from typing import List, Annotated, Optional
from pydantic import BaseModel, Field
from .Analysts.schemas import Analyst


class ResearchInput(BaseModel):
    """Input schema for the main Researcher graph - what the user provides."""

    topic: str  # Research topic


class ResearchOutput(BaseModel):
    """Output schema for the main Researcher graph - what it returns."""

    final_report: str = ""  # Final report


class ResearchGraphState(BaseModel):
    """Internal overall state for the main Researcher graph."""

    topic: str  # Research topic
    analysts: Optional[List[Analyst]] = None  # Analyst asking questions
    sections: Annotated[list, operator.add] = []  # Send() API key
    introduction: str = ""  # Introduction for the final report
    content: str = ""  # Content for the final report
    conclusion: str = ""  # Conclusion for the final report
    final_report: str = ""  # Final report
