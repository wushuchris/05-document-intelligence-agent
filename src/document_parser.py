import re
from collections.abc import Iterator
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF

from src.document_schema import (
    DocumentChunk,
    DocumentFinding,
    DocumentIntelligenceReport,
    DocumentMetadata,
    DocumentProcessingEvent,
    DocumentSummary,
)


def extract_text_from_pdf(file_path: str) -> Tuple[List[str], str]:
    """Extract text from a PDF and return page texts plus extraction notes."""
    page_texts = []

    with fitz.open(file_path) as doc:
        for page in doc:
            text = page.get_text("text")
            page_texts.append(text.strip())

    empty_pages = sum(1 for page in page_texts if not page)
    if empty_pages == len(page_texts):
        notes = "No selectable text found. This may be a scanned PDF that requires OCR."
    elif empty_pages > 0:
        notes = f"Extracted text from PDF. {empty_pages} page(s) had little or no selectable text."
    else:
        notes = "Extracted selectable text from PDF."

    return page_texts, notes


def extract_text_from_txt(file_path: str) -> Tuple[List[str], str]:
    """Read a text file as a single-page document."""
    text = Path(file_path).read_text(encoding="utf-8")
    return [text.strip()], "Read plain text document."


def chunk_pages(page_texts: List[str], chunk_size: int = 1200, overlap: int = 150) -> List[DocumentChunk]:
    """Split page text into page-aware overlapping chunks."""
    chunks = []
    chunk_id = 1

    for page_index, text in enumerate(page_texts, start=1):
        clean_text = re.sub(r"\s+", " ", text).strip()
        if not clean_text:
            continue

        start = 0
        while start < len(clean_text):
            end = start + chunk_size
            chunk_text = clean_text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        page_number=page_index,
                        text=chunk_text,
                    )
                )
                chunk_id += 1

            if end >= len(clean_text):
                break

            start = max(0, end - overlap)

    return chunks


def split_sentences(text: str) -> List[str]:
    """Simple sentence splitter for lightweight local summarization."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def find_dates(text: str) -> List[str]:
    """Find basic date-like strings."""
    patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\bQ[1-4]\s+\d{4}\b",
    ]

    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))

    return sorted(set(matches))


def find_entities(text: str) -> List[str]:
    """Find simple capitalized entity-like phrases."""
    candidates = re.findall(r"\b[A-Z][A-Za-z&.-]*(?:\s+[A-Z][A-Za-z&.-]*){0,4}\b", text)
    stopwords = {
        "The",
        "This",
        "That",
        "Summary",
        "Overview",
        "Background",
        "Recommendation",
        "Action",
        "Issue",
        "Risk",
    }

    entities = []
    for item in candidates:
        cleaned = item.strip()
        if cleaned not in stopwords and len(cleaned) > 2:
            entities.append(cleaned)

    unique_entities = []
    for entity in entities:
        if entity not in unique_entities:
            unique_entities.append(entity)

    return unique_entities[:15]


def sentence_matches_keywords(sentence: str, keywords: List[str]) -> bool:
    lower = sentence.lower()
    return any(keyword in lower for keyword in keywords)


def build_summary(full_text: str) -> DocumentSummary:
    """Create a lightweight structured summary using transparent rules."""
    sentences = split_sentences(full_text)

    executive_summary = " ".join(sentences[:3]) if sentences else "No usable text was extracted from the document."

    key_facts = sentences[:5]

    risks = [
        s
        for s in sentences
        if sentence_matches_keywords(
            s,
            ["risk", "issue", "concern", "delay", "constraint", "challenge", "exposure", "dependency"],
        )
    ][:5]

    action_items = [
        s
        for s in sentences
        if sentence_matches_keywords(
            s,
            ["should", "must", "recommend", "next step", "action", "approve", "review", "complete"],
        )
    ][:5]

    return DocumentSummary(
        executive_summary=executive_summary,
        key_facts=key_facts,
        key_entities=find_entities(full_text),
        important_dates=find_dates(full_text),
        risks_or_issues=risks,
        action_items=action_items,
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _source_location(text: str, page_texts: List[str], chunks: List[DocumentChunk]) -> tuple[int | None, int | None]:
    """Find the source page and best matching chunk for an extracted item without inventing provenance."""
    normalized = _normalize(text)
    if not normalized:
        return None, None

    page_number: int | None = None
    for index, page_text in enumerate(page_texts, start=1):
        if normalized in _normalize(page_text):
            page_number = index
            break

    if page_number is None:
        return None, None

    same_page_chunks = [chunk for chunk in chunks if chunk.page_number == page_number]
    for chunk in same_page_chunks:
        if normalized in _normalize(chunk.text):
            return page_number, chunk.chunk_id

    item_terms = set(re.findall(r"[a-zA-Z0-9]+", normalized))
    best_chunk_id: int | None = None
    best_overlap = 0
    for chunk in same_page_chunks:
        chunk_terms = set(re.findall(r"[a-zA-Z0-9]+", _normalize(chunk.text)))
        overlap = len(item_terms & chunk_terms)
        if overlap > best_overlap:
            best_overlap = overlap
            best_chunk_id = chunk.chunk_id

    return page_number, best_chunk_id if best_overlap > 0 else None


def build_findings(
    summary: DocumentSummary,
    page_texts: List[str],
    chunks: List[DocumentChunk],
) -> List[DocumentFinding]:
    """Attach deterministic source page/chunk lineage to structured summary items."""
    groups = [
        ("key_fact", "FACT", summary.key_facts),
        ("entity", "ENTITY", summary.key_entities),
        ("date", "DATE", summary.important_dates),
        ("risk", "RISK", summary.risks_or_issues),
        ("action_item", "ACTION", summary.action_items),
    ]

    findings: List[DocumentFinding] = []
    for category, prefix, items in groups:
        category_index = 1
        for item in items:
            page_number, chunk_id = _source_location(item, page_texts, chunks)
            if page_number is None:
                continue

            findings.append(
                DocumentFinding(
                    finding_id=f"{prefix}-{category_index:02d}",
                    category=category,
                    text=item,
                    page_number=page_number,
                    chunk_id=chunk_id,
                )
            )
            category_index += 1

    return findings


def parse_document_iter(file_path: str) -> Iterator[DocumentProcessingEvent]:
    """Yield real stages from the deterministic document-intelligence pipeline."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    yield DocumentProcessingEvent(
        event="document_received",
        message=f"Document accepted for processing: {path.name}.",
    )

    if suffix == ".pdf":
        page_texts, notes = extract_text_from_pdf(str(path))
        extraction_method = "PyMuPDF PDF text extraction"
    elif suffix == ".txt":
        page_texts, notes = extract_text_from_txt(str(path))
        extraction_method = "Plain text reader"
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")

    full_text = "\n\n".join(page_texts).strip()

    yield DocumentProcessingEvent(
        event="text_extracted",
        message=f"Text extraction complete across {len(page_texts)} page(s). {notes}",
        page_count=len(page_texts),
    )

    chunks = chunk_pages(page_texts)
    yield DocumentProcessingEvent(
        event="chunks_created",
        message=f"Created {len(chunks)} page-aware searchable chunk(s).",
        page_count=len(page_texts),
        chunk_count=len(chunks),
    )

    summary = build_summary(full_text)
    summary.findings = build_findings(summary, page_texts, chunks)

    yield DocumentProcessingEvent(
        event="structure_extracted",
        message=f"Extracted {len(summary.findings)} structured finding(s) with source lineage.",
        page_count=len(page_texts),
        chunk_count=len(chunks),
        finding_count=len(summary.findings),
    )

    metadata = DocumentMetadata(
        file_name=path.name,
        page_count=len(page_texts),
        character_count=len(full_text),
        extraction_method=extraction_method,
        parsing_notes=notes,
    )

    report = DocumentIntelligenceReport(
        metadata=metadata,
        summary=summary,
        chunks=chunks,
        tables=[],
    )

    yield DocumentProcessingEvent(
        event="report_completed",
        message="Structured document intelligence report is ready for review, search, and export.",
        page_count=len(page_texts),
        chunk_count=len(chunks),
        finding_count=len(summary.findings),
        report=report,
    )


def parse_document(file_path: str) -> DocumentIntelligenceReport:
    """Parse a PDF or TXT file and return the final report from the observable pipeline."""
    final_report: DocumentIntelligenceReport | None = None
    for event in parse_document_iter(file_path):
        if event.report is not None:
            final_report = event.report

    if final_report is None:
        raise RuntimeError("Document processing completed without producing a report.")

    return final_report
