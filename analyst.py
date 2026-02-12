from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
import operator

### Schema


class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(description="Name of the analyst.")
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )


class GenerateAnalystsState(BaseModel):
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = None  # Human feedback
    analysts: List[Analyst] = []  # Analyst asking questions


class InterviewState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = []
    max_num_turns: int = 2  # Number turns of conversation
    context: Annotated[List[str], operator.add] = []  # Source docs
    analyst: Optional[Analyst] = None  # Analyst asking questions
    interview: Optional[str] = None  # Interview transcript
    sections: List[str] = []  # Final key we duplicate in outer state for Send() API


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")
