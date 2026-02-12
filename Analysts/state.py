from typing import List, Optional
from pydantic import BaseModel
from Analysts.schemas import Analyst


class GenerateAnalystsState(BaseModel):
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: Optional[str] = None  # Human feedback
    analysts: List[Analyst] = []  # Analyst asking questions
