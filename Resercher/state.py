import operator
from typing import List, Annotated
from pydantic import BaseModel, Field
from .Analysts.schemas import Analyst
from typing import Optional


class ResearchGraphState(BaseModel):
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = ""  # Human feedback
    analysts: Optional[List[Analyst]] = None  # Analyst asking questions
    sections: Annotated[list, operator.add] = []  # Send() API key
    introduction: str = ""  # Introduction for the final report
    content: str = ""  # Content for the final report
    conclusion: str = ""  # Conclusion for the final report
    final_report: str = ""  # Final report
