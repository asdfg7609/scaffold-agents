"""
domain/schemas/output.py — Schema-First: agent output types (framework-agnostic)
"""
from pydantic import BaseModel, Field
from datetime import datetime


class SearchResult(BaseModel):
    title:        str
    url:          str
    summary:      str
    published_at: str = ""


class ResearchOutput(BaseModel):
    query:        str
    results:      list[SearchResult]
    collected_at: datetime = Field(default_factory=datetime.now)


class AnalysisOutput(BaseModel):
    key_insights: list[str] = Field(description="List of key insights")
    trends:       list[str] = Field(description="Identified trends")
    confidence:   float     = Field(ge=0.0, le=1.0, description="Analysis confidence score")
    summary:      str


class ReportOutput(BaseModel):
    title:             str
    executive_summary: str
    file_path:         str
    word_count:        int
    created_at:        datetime = Field(default_factory=datetime.now)
