import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.document_parser import parse_document
from src.output_writer import (
    chunks_to_dataframe,
    metadata_to_dataframe,
    report_to_json,
    summary_to_dataframe,
)
from src.search_index import search_chunks


st.set_page_config(
    page_title="Document Intelligence Agent",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Document Intelligence Agent")
st.caption(
    "Convert PDFs and text files into structured summaries, searchable chunks, and exportable data."
)

st.sidebar.header("About this agent")
st.sidebar.write(
    "This app demonstrates a document intelligence workflow: parse, structure, validate, search, and export."
)
st.sidebar.warning(
    "Demo note: avoid uploading private, confidential, client, legal, medical, or sensitive documents."
)

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT document",
    type=["pdf", "txt"],
)

use_sample = st.checkbox("Use included synthetic sample memo instead")

file_path = None

if use_sample:
    file_path = "sample_docs/sample_business_memo.txt"
elif uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        file_path = temp_file.name

if file_path:
    try:
        report = parse_document(file_path)

        st.success("Document parsed successfully.")

        tab_summary, tab_search, tab_chunks, tab_exports = st.tabs(
            ["Structured Summary", "Search", "Chunks", "Exports"]
        )

        with tab_summary:
            st.subheader("Document Metadata")
            st.dataframe(metadata_to_dataframe(report), use_container_width=True)

            st.subheader("Executive Summary")
            st.write(report.summary.executive_summary)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Key Facts")
                if report.summary.key_facts:
                    for fact in report.summary.key_facts:
                        st.markdown(f"- {fact}")
                else:
                    st.write("No key facts detected.")

                st.subheader("Important Dates")
                if report.summary.important_dates:
                    for item in report.summary.important_dates:
                        st.markdown(f"- {item}")
                else:
                    st.write("No dates detected.")

                st.subheader("Risks or Issues")
                if report.summary.risks_or_issues:
                    for risk in report.summary.risks_or_issues:
                        st.markdown(f"- {risk}")
                else:
                    st.write("No risks or issues detected.")

            with col2:
                st.subheader("Key Entities")
                if report.summary.key_entities:
                    for entity in report.summary.key_entities:
                        st.markdown(f"- {entity}")
                else:
                    st.write("No entities detected.")

                st.subheader("Action Items")
                if report.summary.action_items:
                    for action in report.summary.action_items:
                        st.markdown(f"- {action}")
                else:
                    st.write("No action items detected.")

        with tab_search:
            st.subheader("Search Document Chunks")
            query = st.text_input("Search for a term, topic, date, risk, entity, or action item")

            if query:
                results = search_chunks(query, report.chunks)

                if results:
                    st.write(f"Found {len(results)} matching chunk(s).")
                    for chunk in results:
                        with st.expander(
                            f"Chunk {chunk.chunk_id} — Page {chunk.page_number}",
                            expanded=True,
                        ):
                            st.write(chunk.text)
                else:
                    st.info("No matching chunks found.")

        with tab_chunks:
            st.subheader("Page-Aware Document Chunks")
            chunks_df = chunks_to_dataframe(report)

            if not chunks_df.empty:
                st.dataframe(chunks_df, use_container_width=True)
            else:
                st.info("No chunks were created.")

        with tab_exports:
            st.subheader("Download Structured Outputs")

            json_report = report_to_json(report)
            chunks_df = chunks_to_dataframe(report)
            metadata_df = metadata_to_dataframe(report)
            summary_df = summary_to_dataframe(report)

            st.download_button(
                label="Download full JSON report",
                data=json_report,
                file_name="document_intelligence_report.json",
                mime="application/json",
            )

            st.download_button(
                label="Download chunks CSV",
                data=chunks_df.to_csv(index=False),
                file_name="document_chunks.csv",
                mime="text/csv",
            )

            st.download_button(
                label="Download metadata CSV",
                data=metadata_df.to_csv(index=False),
                file_name="document_metadata.csv",
                mime="text/csv",
            )

            st.download_button(
                label="Download summary CSV",
                data=summary_df.to_csv(index=False),
                file_name="document_summary.csv",
                mime="text/csv",
            )

            st.subheader("Raw JSON Preview")
            st.json(report.model_dump())

    except Exception as error:
        st.error(f"Could not process document: {error}")

else:
    st.info("Upload a document or use the included synthetic sample memo to begin.")

    st.markdown(
        """
        ### What this agent does

        - Extracts text from PDF and TXT documents
        - Creates structured metadata
        - Generates a lightweight structured summary
        - Identifies simple entities, dates, risks, and action items
        - Splits the document into searchable page-aware chunks
        - Exports JSON and CSV files

        ### Privacy note

        This demo is designed for synthetic or non-sensitive documents.
        """
    )
