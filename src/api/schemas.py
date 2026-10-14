from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    session_id: str | None = Field(default=None, max_length=128)

class FeedbackRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)
    query: str | None = Field(default=None, max_length=2000)
