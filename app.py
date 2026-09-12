import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.demo_presentation import (
    APP_CSS,
    ARCHITECTURE_MARKDOWN,
    CONTROL_BOUNDARY_HTML,
    HERO_HTML,
    LIMITS_MARKDOWN,
    PIPELINE_HTML,
    WHY_IT_MATTERS_HTML,
)
from src.document_parser import parse_document_iter
from src.output_writer import (
    chunks_to_dataframe,
    findings_to_dataframe,
    metadata_to_dataframe,
    report_to_json,
    summary_to_dataframe,
)
from src.search_index import search_chunks


SAMPLE_PATH = Path("sample_docs/sample_business_memo.txt")

st.set_page_config(
    page_title="Document Intelligence Agent",
    page_icon="📄",
    layout="wide",
)

st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

st.markdown("## Why document intelligence needs traceability")
left, right = st.columns(2)
with left:
    st.markdown(WHY_IT_MATTERS_HTML, unsafe_allow_html=True)
with right:
    st.markdown(CONTROL_BOUNDARY_HTML, unsafe_allow_html=True)

st.markdown("## How the document becomes structured intelligence")
st.markdown(PIPELINE_HTML, unsafe_allow_html=True)

st.markdown("## Process a document")
st.caption(
    "The included Northstar Operations Group memo is synthetic and is the recommended public-safe demonstration."
)

source_choice = st.radio(
    "Document source",
    ["Synthetic sample memo", "Upload PDF or TXT"],
    horizontal=True,
)

uploaded_file = None
if source_choice == "Upload PDF or TXT":
    uploaded_file = st.file_uploader(
        "Upload a PDF or TXT document",
        type=["pdf", "txt"],
        help="Use synthetic or non-sensitive documents only in this public demo.",
    )
    st.warning(
        "Public demo safety: do not upload client, legal, medical, account, confidential business, "
        "or other sensitive documents."
    )
else:
    with st.expander("Preview the synthetic Northstar memo"):
        st.text(SAMPLE_PATH.read_text(encoding="utf-8"))

process_button = st.button("Process document", type="primary", use_container_width=True)

if "document_report" not in st.session_state:
    st.session_state.document_report = None
if "processing_events" not in st.session_state:
    st.session_state.processing_events = []


def _process_path(file_path: str):
    events = []
    report = None

    with st.status("Turning the document into structured intelligence...", expanded=True) as status:
        for event in parse_document_iter(file_path):
            events.append(event.message)
            status.write(event.message)
            if event.report is not None:
                report = event.report

        if report is None:
            status.update(label="Document processing stopped before a report was produced.", state="error")
            raise RuntimeError("Document processing completed without producing a report.")

        status.update(label="Document intelligence report ready.", state="complete", expanded=False)

    return report, events


if process_button:
    try:
        if source_choice == "Synthetic sample memo":
            report, events = _process_path(str(SAMPLE_PATH))
        else:
            if uploaded_file is None:
                st.warning("Choose a PDF or TXT document before processing.")
                st.stop()

            safe_name = Path(uploaded_file.name).name
            suffix = Path(safe_name).suffix.lower()
            with tempfile.TemporaryDirectory(prefix="document_intelligence_") as temp_dir:
                temp_path = Path(temp_dir) / safe_name
                temp_path.write_bytes(uploaded_file.getbuffer())
                report, events = _process_path(str(temp_path))

        st.session_state.document_report = report
        st.session_state.processing_events = events

    except Exception as error:
        st.session_state.document_report = None
        st.session_state.processing_events = []
        st.error(f"Could not process document: {error}")


report = st.session_state.document_report

if report is None:
    st.info("Process the synthetic memo or a public-safe PDF/TXT file to see the source-linked intelligence report.")
else:
    st.markdown("## Document intelligence at a glance")
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Pages", report.metadata.page_count)
    metric_2.metric("Searchable chunks", len(report.chunks))
    metric_3.metric("Source-linked findings", len(report.summary.findings))
    metric_4.metric("Characters", f"{report.metadata.character_count:,}")

    st.caption(f"Extraction method: {report.metadata.extraction_method}")
    if "No selectable text" in report.metadata.parsing_notes or "little or no selectable text" in report.metadata.parsing_notes:
        st.warning(report.metadata.parsing_notes)
    else:
        st.success(report.metadata.parsing_notes)

    st.markdown("## Structured intelligence")
    st.markdown(
        f'<div class="summary-callout"><strong>Executive summary</strong><br>{report.summary.executive_summary}</div>',
        unsafe_allow_html=True,
    )

    risks_col, actions_col = st.columns(2)
    with risks_col:
        st.markdown("### Risks / issues")
        risk_findings = [finding for finding in report.summary.findings if finding.category == "risk"]
        if risk_findings:
            for finding in risk_findings:
                chunk_label = f" · Chunk {finding.chunk_id}" if finding.chunk_id is not None else ""
                st.markdown(f"- {finding.text}  \n  *Page {finding.page_number}{chunk_label}*")
        else:
            st.caption("No risks or issues detected by the current rules.")

    with actions_col:
        st.markdown("### Action items")
        action_findings = [finding for finding in report.summary.findings if finding.category == "action_item"]
        if action_findings:
            for finding in action_findings:
                chunk_label = f" · Chunk {finding.chunk_id}" if finding.chunk_id is not None else ""
                st.markdown(f"- {finding.text}  \n  *Page {finding.page_number}{chunk_label}*")
        else:
            st.caption("No action items detected by the current rules.")

    dates_col, entities_col = st.columns(2)
    with dates_col:
        st.markdown("### Important dates")
        date_findings = [finding for finding in report.summary.findings if finding.category == "date"]
        if date_findings:
            for finding in date_findings:
                st.markdown(f"- **{finding.text}** — Page {finding.page_number}")
        else:
            st.caption("No dates detected.")

    with entities_col:
        st.markdown("### Key entities")
        entity_findings = [finding for finding in report.summary.findings if finding.category == "entity"]
        if entity_findings:
            for finding in entity_findings:
                st.markdown(f"- **{finding.text}** — Page {finding.page_number}")
        else:
            st.caption("No entities detected.")

    st.markdown("## Source lineage")
    st.markdown(
        '<div class="lineage-note"><strong>Why this matters:</strong> structured extraction should not sever an item '
        'from the document that produced it. Every finding below keeps its source page and, where available, its '
        'searchable chunk ID.</div>',
        unsafe_allow_html=True,
    )

    findings_df = findings_to_dataframe(report)
    if findings_df.empty:
        st.info("No source-linked findings were produced for this document.")
    else:
        category_choices = ["All"] + sorted(findings_df["category"].unique().tolist())
        selected_category = st.selectbox("Filter findings", category_choices)
        display_findings = findings_df
        if selected_category != "All":
            display_findings = findings_df[findings_df["category"] == selected_category]
        st.dataframe(display_findings, use_container_width=True, hide_index=True)

    st.markdown("## Search the original source")
    st.caption("Search runs against the page-aware source chunks, not only the rewritten summary.")
    query = st.text_input("Search for a term, topic, date, risk, entity, or action item")

    if query:
        results = search_chunks(query, report.chunks)
        if results:
            st.write(f"Found {len(results)} matching chunk(s).")
            for chunk in results:
                with st.expander(
                    f"Page {chunk.page_number} · Chunk {chunk.chunk_id}",
                    expanded=True,
                ):
                    st.write(chunk.text)
        else:
            st.info("No matching source chunks found.")

    st.markdown("## Engineering evidence")
    tab_chunks, tab_audit, tab_exports, tab_limits = st.tabs(
        ["Source Chunks", "Architecture & Trace", "Exports", "Limits"]
    )

    with tab_chunks:
        chunks_df = chunks_to_dataframe(report)
        if chunks_df.empty:
            st.info("No chunks were created.")
        else:
            st.dataframe(chunks_df, use_container_width=True, hide_index=True)

    with tab_audit:
        st.markdown(ARCHITECTURE_MARKDOWN)
        if st.session_state.processing_events:
            st.markdown("### Processing trace")
            for index, message in enumerate(st.session_state.processing_events, start=1):
                st.markdown(f"**{index}.** {message}")
        st.markdown("### Structured metadata")
        st.dataframe(metadata_to_dataframe(report), use_container_width=True, hide_index=True)
        with st.expander("Raw structured JSON"):
            st.json(report.model_dump())

    with tab_exports:
        json_report = report_to_json(report)
        chunks_df = chunks_to_dataframe(report)
        metadata_df = metadata_to_dataframe(report)
        summary_df = summary_to_dataframe(report)
        findings_export_df = findings_to_dataframe(report)

        st.download_button(
            label="Download full JSON report",
            data=json_report,
            file_name="document_intelligence_report.json",
            mime="application/json",
            use_container_width=True,
        )
        st.download_button(
            label="Download source-linked findings CSV",
            data=findings_export_df.to_csv(index=False),
            file_name="document_findings.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            label="Download chunks CSV",
            data=chunks_df.to_csv(index=False),
            file_name="document_chunks.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            label="Download metadata CSV",
            data=metadata_df.to_csv(index=False),
            file_name="document_metadata.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            label="Download summary CSV",
            data=summary_df.to_csv(index=False),
            file_name="document_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab_limits:
        st.markdown(LIMITS_MARKDOWN)
