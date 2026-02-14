from typing import List, Optional
from pydantic import BaseModel, Field
from .schemas import Analyst
from ..configuration import DEFAULT_MAX_ANALYSTS, MIN_ANALYSTS, MAX_ANALYSTS


class AnalystsInput(BaseModel):
    """Input schema for the Analysts subgraph - what the caller must provide."""

    topic: str = Field(description="Research topic to generate analysts for")
    human_analyst_feedback: Optional[str] = Field(
        default="",
        description="Optional feedback from user to refine analyst generation (used in feedback loop)",
    )


class AnalystsOutput(BaseModel):
    """Output schema for the Analysts subgraph - what it returns."""

    analysts: List[Analyst] = Field(
        default_factory=list, description="Generated list of AI analyst personas"
    )


class GenerateAnalystsState(BaseModel):
    """Internal overall state for the Analysts subgraph."""

    topic: str = Field(description="Research topic to generate analysts for")
    max_analysts: int = Field(
        default=DEFAULT_MAX_ANALYSTS,
        description="Maximum number of analyst personas to generate",
        ge=MIN_ANALYSTS,
        le=MAX_ANALYSTS,
    )
    human_analyst_feedback: Optional[str] = Field(
        default="",
        description="Human feedback for refining analysts (accumulated through interrupt loop)",
    )
    analysts: List[Analyst] = Field(
        default_factory=list, description="Generated list of AI analyst personas"
    )
