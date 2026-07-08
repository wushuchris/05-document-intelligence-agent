import re
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF

from src.document_schema import (
    DocumentChunk,
    DocumentIntelligenceReport,
    DocumentMetadata,
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
        s for s in sentences
        if sentence_matches_keywords(
            s,
            ["risk", "issue", "concern", "delay", "constraint", "challenge", "exposure", "dependency"],
        )
    ][:5]

    action_items = [
        s for s in sentences
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


def parse_document(file_path: str) -> DocumentIntelligenceReport:
    """Parse a PDF or TXT file into a structured intelligence report."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        page_texts, notes = extract_text_from_pdf(str(path))
        extraction_method = "PyMuPDF PDF text extraction"
    elif suffix == ".txt":
        page_texts, notes = extract_text_from_txt(str(path))
        extraction_method = "Plain text reader"
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")

    full_text = "\n\n".join(page_texts).strip()
    chunks = chunk_pages(page_texts)

    metadata = DocumentMetadata(
        file_name=path.name,
        page_count=len(page_texts),
        character_count=len(full_text),
        extraction_method=extraction_method,
        parsing_notes=notes,
    )

    summary = build_summary(full_text)

    return DocumentIntelligenceReport(
        metadata=metadata,
        summary=summary,
        chunks=chunks,
        tables=[],
    )
