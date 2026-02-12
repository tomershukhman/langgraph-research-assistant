from typing import List, Annotated, Optional
import operator
from pydantic import BaseModel, Field


# Mock Analyst class for testing
class Analyst(BaseModel):
    affiliation: str
    name: str
    role: str
    description: str

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


# Copy of ResearchGraphState from Resercher/state.py
# (We will use this to test the fix before applying it)
class ResearchGraphState(BaseModel):
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = None  # Human feedback
    analysts: List[Analyst] = []  # Analyst asking questions
    sections: Annotated[list, operator.add] = []  # Send() API key
    introduction: Optional[str] = None  # Introduction for the final report
    content: Optional[str] = None  # Content for the final report
    conclusion: Optional[str] = None  # Conclusion for the final report
    final_report: Optional[str] = None  # Final report


try:
    # Try to instantiate with minimal arguments
    state = ResearchGraphState(topic="AI", max_analysts=3)
    print("Successfully instantiated ResearchGraphState with minimal arguments.")
    print(state)
except Exception as e:
    print(f"Failed to instantiate ResearchGraphState: {e}")
