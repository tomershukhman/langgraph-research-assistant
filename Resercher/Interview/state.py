from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
import operator
from ..Analysts.schemas import Analyst


class InterviewInput(BaseModel):
    """Input schema for the Interview subgraph - what the caller provides via Send()."""

    analyst: Optional[Analyst] = None  # Analyst asking questions
    messages: Annotated[List[AnyMessage], add_messages] = []


class InterviewOutput(BaseModel):
    """Output schema for the Interview subgraph - what it returns."""

    sections: List[str] = []  # Written section from this interview


class InterviewState(BaseModel):
    """Internal overall state for the Interview subgraph."""

    max_num_turns: int = 2  # Number turns of conversation
    context: Annotated[List[str], operator.add] = []  # Source docs
    analyst: Optional[Analyst] = None  # Analyst asking questions
    interview: Optional[str] = None  # Interview transcript
    sections: List[str] = []  # Final key we duplicate in outer state for Send() API
    messages: Annotated[List[AnyMessage], add_messages] = []
