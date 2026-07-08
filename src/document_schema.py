from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    file_name: str
    page_count: int
    character_count: int
    extraction_method: str
    parsing_notes: str


class DocumentChunk(BaseModel):
    chunk_id: int
    page_number: int
    text: str


class DocumentSummary(BaseModel):
    executive_summary: str
    key_facts: List[str] = Field(default_factory=list)
    key_entities: List[str] = Field(default_factory=list)
    important_dates: List[str] = Field(default_factory=list)
    risks_or_issues: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


class TableExtraction(BaseModel):
    table_id: int
    page_number: Optional[int] = None
    rows: List[dict] = Field(default_factory=list)


class DocumentIntelligenceReport(BaseModel):
    metadata: DocumentMetadata
    summary: DocumentSummary
    chunks: List[DocumentChunk]
    tables: List[TableExtraction] = Field(default_factory=list)
