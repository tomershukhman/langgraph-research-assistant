from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Structured search query for web/Wikipedia retrieval."""

    search_query: str = Field(
        description="Search query string for retrieving relevant documents"
    )
