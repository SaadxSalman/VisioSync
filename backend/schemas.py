from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=6, ge=1, le=20)
    document_ids: list[str] = Field(default_factory=list)


class PageHit(BaseModel):
    page: int
    score: float
    title: str
    excerpt: str
    document_id: str
    document_name: str = "Engineering corpus"
    image_url: str | None = None


class QueryResponse(BaseModel):
    answer: str
    hits: list[PageHit]
    model: str
    retrieval_mode: str
    query: str
    latency_ms: int


class DocumentResponse(BaseModel):
    id: str
    name: str
    pages: int
    status: str
    indexed_at: datetime
    kind: str
    size_bytes: int


class JobResponse(BaseModel):
    id: str
    document_id: str
    status: str
    progress: int
    message: str
