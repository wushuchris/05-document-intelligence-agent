# 05 Document Intelligence Agent

A document intelligence agent that converts PDFs and text files into structured summaries, searchable chunks, and exportable data.

## Agent Pattern

Documents in. Structured intelligence out.

## What This Agent Does

This project demonstrates a lightweight document intelligence workflow:

1. Parse a PDF or text document
2. Extract document metadata
3. Generate a structured summary
4. Identify simple entities, dates, risks, and action items
5. Split the document into searchable page-aware chunks
6. Export the results as JSON and CSV files

## Why This Agent Matters

Many real-world workflows depend on reading long documents and turning them into useful decisions, summaries, and records.

This agent shows how to move from unstructured documents to structured, auditable outputs. The first version intentionally uses transparent local logic rather than an external LLM API. This keeps the demo simple, reproducible, and safe for public deployment.

## Features

- PDF text extraction with PyMuPDF
- Plain text document support
- Structured Pydantic schemas
- Page-aware chunking
- Keyword search across document chunks
- Simple entity and date detection
- Risk and action item extraction
- Downloadable JSON and CSV outputs
- Streamlit web interface
- Synthetic sample memo included

## Tech Stack

- Python
- Streamlit
- PyMuPDF
- pandas
- Pydantic
- pdfplumber

## Project Structure

- app.py
- requirements.txt
- sample_docs/sample_business_memo.txt
- src/document_parser.py
- src/document_schema.py
- src/output_writer.py
- src/search_index.py

## Run Locally

Install dependencies:

pip install -r requirements.txt

Run the app:

streamlit run app.py

## Usage

You can either upload a PDF or TXT file, or use the included synthetic sample memo.

The app will produce:

- Structured metadata
- Executive summary
- Key facts
- Important dates
- Key entities
- Risks or issues
- Action items
- Searchable chunks
- Downloadable JSON and CSV files

## Privacy and Safety

This repository is designed for public demonstration with synthetic or non-sensitive documents.

Do not upload client documents, legal documents, medical documents, financial account documents, confidential business documents, private curriculum, or private source material.

## Limitations

This version uses lightweight local extraction rules. It does not yet include OCR for scanned PDFs, semantic embeddings, LLM-generated summaries, advanced table extraction, multi-document comparison, authentication, or persistent storage.

## Agent Engineering Lesson

This build demonstrates a practical document intelligence pattern:

Parse -> Structure -> Validate -> Search -> Export

The important engineering idea is that the agent does not simply summarize a document. It creates structured, validated, auditable outputs that can be inspected, searched, and exported.

## Status

Working prototype.
