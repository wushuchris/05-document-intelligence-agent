---
title: Document Intelligence Agent
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 05 Document Intelligence Agent — Source-Linked Document Intelligence

A deterministic document-intelligence system that turns PDFs and text files into structured, searchable work products while preserving a trace back to the source document.

## Business Question

**What did this document say — and can every extracted item be traced back to the source?**

Document-heavy workflows become much more useful when extracted facts, dates, entities, risks, and action items are not just summarized, but kept connected to the page and searchable chunk they came from.

This project demonstrates that boundary with a synthetic Northstar Operations memo and optional PDF/TXT uploads.

## Agent Pattern

**Parse → Structure → Preserve provenance → Search → Export**

The system does not use an LLM to invent summaries or citations. It uses transparent local extraction rules, typed schemas, page-aware chunks, deterministic source-lineage mapping, and explicit exports so a reviewer can inspect how the structured output was produced.

## What This Agent Does

1. Accept a PDF or plain-text document
2. Extract selectable text and document metadata
3. Split content into page-aware searchable chunks
4. Produce a structured summary using deterministic local rules
5. Identify key facts, entities, dates, risks, and action items
6. Attach source page and chunk lineage to extracted findings when the source can be located
7. Expose real processing-stage events through `parse_document_iter()`
8. Search the original document chunks by keyword overlap
9. Export structured JSON and CSV outputs for inspection and downstream use

## Why This Agent Matters

Many operational, compliance, research, and review workflows start with unstructured documents. A useful document-intelligence system should do more than create a convenient summary: it should preserve enough structure and source context for a human or downstream system to inspect where the extracted information came from.

The central engineering lesson is therefore not simply “summarize a PDF.” It is:

> **Turn unstructured documents into typed, source-linked evidence without losing the connection back to the source.**

This makes Agent 5 a natural precursor to Agent 6. Agent 5 structures and preserves evidence provenance; Agent 6 evaluates whether claims are supported by evidence.

## Source-Lineage Boundary

Each structured finding can carry:

- a stable finding ID,
- a finding category,
- the extracted text,
- source page number,
- and the best matching source chunk when available.

The application only records provenance it can locate deterministically. It does not invent a page or chunk when the source cannot be found.

**Important:** source provenance is not truth verification. A finding being traceable to a document means “this came from the supplied document,” not “this statement is independently true.”

## Observable Processing Pipeline

`parse_document_iter()` exposes the real deterministic processing stages:

1. `document_received`
2. `text_extracted`
3. `chunks_created`
4. `structure_extracted`
5. `report_completed`

The normal `parse_document()` API consumes the same observable pipeline and returns the final structured report. There is no separate demo-only workflow.

## Live Demo

The Hugging Face Space presents the system as a business-first document review workflow rather than a raw extraction form.

The approved demo includes:

- a centered 1080px Streamlit layout,
- a synthetic Northstar Operations memo as the recommended scenario,
- PDF/TXT upload as a secondary path,
- visible processing stages from the real parser pipeline,
- readable structured findings,
- source page/chunk lineage,
- searchable original chunks,
- structured metadata and summary views,
- JSON/CSV exports,
- and engineering details beneath the business-facing workflow.

Live demo: https://huggingface.co/spaces/FlyingNunchucks/05-document-intelligence-agent

## Engineering Architecture

### Parsing
- PDF text extraction with PyMuPDF
- Plain-text file reader
- Explicit note when a PDF has little or no selectable text

### Structure
- Pydantic schemas for metadata, chunks, findings, summaries, processing events, and the complete report
- Deterministic local extraction rules for facts, entities, dates, risks, and actions

### Provenance
- Page-aware findings
- Best matching source-chunk linkage when deterministically locatable
- No fabricated lineage

### Search
- Lightweight token overlap against the original page-aware chunks
- Ranked top-k matching chunks

### Export
- Full structured JSON report
- CSV outputs for chunks, metadata, summary, and source-linked findings

## Evaluation and Regression Lessons

The retrofit added the first automated validation suite to this project.

A four-case deterministic document benchmark now checks:

- the synthetic Northstar business memo,
- a risk/action-focused memo,
- a neutral factual note,
- and an empty-document fallback.

The evaluation gate caught a real legacy extraction bug: the old substring-based action detector treated the past-tense word **“completed”** as an action because it contained `complete`. Deployment was blocked, the heuristic was tightened to directive language, and the failure became a permanent regression test.

This is an important engineering lesson: **a benchmark should be capable of stopping deployment when the extraction rules drift or over-trigger.**

## Production Validation

Final approved retrofit status:

- **17 automated tests passed**
- **4/4 deterministic document-evaluation cases passed**
- Streamlit application smoke test passed
- GitHub Actions gates deployment on both pytest and the document evaluation
- GitHub → Hugging Face deployment succeeded
- Final live presentation review approved by the project owner

## Tech Stack

- Python
- Streamlit
- PyMuPDF
- pandas
- Pydantic
- pdfplumber
- pytest
- Docker
- GitHub Actions
- Hugging Face Spaces

## Project Structure

```text
app.py
requirements.txt
Dockerfile
sample_docs/
  sample_business_memo.txt
src/
  document_parser.py
  document_schema.py
  output_writer.py
  search_index.py
  demo_presentation.py
tests/
  test_document_pipeline.py
  test_presentation.py
  test_app_smoke.py
evals/
  cases.json
  run_evaluation.py
.github/workflows/
  sync-to-huggingface.yml
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
python -m pytest -q
```

Run the deterministic evaluation suite:

```bash
python -m evals.run_evaluation
```

## Privacy and Safety

This repository is a public portfolio project. Use synthetic or non-sensitive documents only.

Do not upload client documents, legal records, medical records, financial account documents, confidential business material, private curriculum, or other sensitive source material.

## Limitations

This project intentionally keeps the document-intelligence primitive transparent and bounded.

It does not currently include:

- OCR for scanned/image-only PDFs,
- semantic embeddings,
- LLM-generated summaries,
- advanced table extraction,
- multi-document comparison,
- authentication,
- or persistent document storage.

The local extraction rules are deterministic and auditable, but they remain heuristics and can miss context or over-extract on unfamiliar document styles. Human review remains appropriate before consequential use.

## Reusable Engineering Primitive

Agent 5 contributes a reusable source-linked document-processing primitive:

> **Parse unstructured material into typed work products while preserving enough provenance for a reviewer or downstream system to trace structured findings back to the original source.**

That primitive becomes the evidence foundation for later verification, tool-use, and agentic workflow systems.

## Status

**Complete — production-validated and human-reviewed.**
