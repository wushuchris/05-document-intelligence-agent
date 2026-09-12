from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    file_name: str
    page_count: int
    character_count: int
    extraction_method: str
    parsing_notes: str


class DocumentChunk(BaseModel):
    chunk_id: int = Field(ge=1)
    page_number: int = Field(ge=1)
    text: str


class DocumentFinding(BaseModel):
    """A structured finding that remains traceable to the source document."""

    finding_id: str
    category: Literal["key_fact", "entity", "date", "risk", "action_item"]
    text: str
    page_number: int = Field(ge=1)
    chunk_id: Optional[int] = Field(default=None, ge=1)


class DocumentSummary(BaseModel):
    executive_summary: str
    key_facts: List[str] = Field(default_factory=list)
    key_entities: List[str] = Field(default_factory=list)
    important_dates: List[str] = Field(default_factory=list)
    risks_or_issues: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    findings: List[DocumentFinding] = Field(default_factory=list)


class TableExtraction(BaseModel):
    table_id: int
    page_number: Optional[int] = None
    rows: List[dict] = Field(default_factory=list)


class DocumentIntelligenceReport(BaseModel):
    metadata: DocumentMetadata
    summary: DocumentSummary
    chunks: List[DocumentChunk]
    tables: List[TableExtraction] = Field(default_factory=list)


class DocumentProcessingEvent(BaseModel):
    """Observable event emitted by the real deterministic document pipeline."""

    event: str
    message: str
    page_count: Optional[int] = None
    chunk_count: Optional[int] = None
    finding_count: Optional[int] = None
    report: Optional[DocumentIntelligenceReport] = None
