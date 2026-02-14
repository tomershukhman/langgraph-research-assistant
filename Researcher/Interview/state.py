from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
import operator
from ..Analysts.schemas import Analyst
from ..configuration import DEFAULT_MAX_TURNS, MIN_TURNS, MAX_TURNS


class InterviewInput(BaseModel):
    """Input schema for the Interview subgraph - what the caller provides via Send()."""

    analyst: Optional[Analyst] = Field(
        default=None, description="AI analyst persona conducting the interview"
    )
    messages: Annotated[List[AnyMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation messages between analyst and expert",
    )


class InterviewOutput(BaseModel):
    """Output schema for the Interview subgraph - what it returns."""

    sections: List[str] = Field(
        default_factory=list, description="Written section(s) from this interview"
    )


class InterviewState(BaseModel):
    """Internal overall state for the Interview subgraph."""

    max_num_turns: int = Field(
        default=DEFAULT_MAX_TURNS,
        description="Maximum number of question-answer turns in the interview",
        ge=MIN_TURNS,
        le=MAX_TURNS,
    )
    context: Annotated[List[str], operator.add] = Field(
        default_factory=list,
        description="Retrieved source documents from web and Wikipedia searches",
    )
    analyst: Optional[Analyst] = Field(
        default=None, description="AI analyst persona conducting the interview"
    )
    interview: Optional[str] = Field(
        default=None, description="Complete interview transcript as a string"
    )
    sections: List[str] = Field(
        default_factory=list,
        description="Final written sections (returned to parent graph)",
    )
    messages: Annotated[List[AnyMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation messages between analyst and expert",
    )
