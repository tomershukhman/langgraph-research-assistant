from typing import List, Optional
from pydantic import BaseModel
from .schemas import Analyst


class AnalystsInput(BaseModel):
    """Input schema for the Analysts subgraph - what the caller must provide."""

    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = ""  # Human feedback


class AnalystsOutput(BaseModel):
    """Output schema for the Analysts subgraph - what it returns."""

    analysts: List[Analyst] = []  # Generated analysts


class GenerateAnalystsState(BaseModel):
    """Internal overall state for the Analysts subgraph."""

    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = ""  # Human feedback
    analysts: List[Analyst] = []  # Analyst asking questions
