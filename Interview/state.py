from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
import operator
from Analysts.schemas import Analyst


class InterviewState(BaseModel):
    max_num_turns: int = 2  # Number turns of conversation
    context: Annotated[List[str], operator.add] = []  # Source docs
    analyst: Optional[Analyst] = None  # Analyst asking questions
    interview: Optional[str] = None  # Interview transcript
    sections: List[str] = []  # Final key we duplicate in outer state for Send() API
    messages: Annotated[List[AnyMessage], add_messages] = []
