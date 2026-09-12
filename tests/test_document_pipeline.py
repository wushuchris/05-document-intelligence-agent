import json
from pathlib import Path

import pytest

from src.document_parser import chunk_pages, parse_document, parse_document_iter
from src.output_writer import findings_to_dataframe, report_to_json
from src.search_index import search_chunks


SAMPLE_PATH = Path("sample_docs/sample_business_memo.txt")


def test_parse_text_document_returns_structured_report():
    report = parse_document(str(SAMPLE_PATH))

    assert report.metadata.file_name == "sample_business_memo.txt"
    assert report.metadata.page_count == 1
    assert report.metadata.character_count > 0
    assert report.chunks
    assert report.summary.key_facts
    assert report.summary.important_dates
    assert report.summary.risks_or_issues
    assert report.summary.action_items


def test_structured_findings_keep_source_lineage():
    report = parse_document(str(SAMPLE_PATH))

    assert report.summary.findings
    assert {finding.category for finding in report.summary.findings} >= {
        "key_fact",
        "entity",
        "date",
        "risk",
        "action_item",
    }
    assert all(finding.page_number == 1 for finding in report.summary.findings)
    assert all(finding.chunk_id is not None for finding in report.summary.findings)


def test_parse_document_iter_emits_real_stage_order():
    events = list(parse_document_iter(str(SAMPLE_PATH)))

    assert [event.event for event in events] == [
        "document_received",
        "text_extracted",
        "chunks_created",
        "structure_extracted",
        "report_completed",
    ]
    assert events[-1].report is not None
    assert events[-1].finding_count == len(events[-1].report.summary.findings)


def test_parse_document_uses_same_final_report_as_observable_pipeline():
    direct_report = parse_document(str(SAMPLE_PATH))
    streamed_report = list(parse_document_iter(str(SAMPLE_PATH)))[-1].report

    assert streamed_report is not None
    assert direct_report.model_dump() == streamed_report.model_dump()


def test_unsupported_file_type_is_rejected(tmp_path):
    file_path = tmp_path / "unsupported.csv"
    file_path.write_text("a,b\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        list(parse_document_iter(str(file_path)))


def test_chunk_pages_preserves_page_numbers():
    chunks = chunk_pages([
        "alpha " * 300,
        "beta " * 300,
    ], chunk_size=300, overlap=50)

    assert chunks
    assert {chunk.page_number for chunk in chunks} == {1, 2}
    assert [chunk.chunk_id for chunk in chunks] == list(range(1, len(chunks) + 1))


def test_search_chunks_ranks_keyword_overlap():
    chunks = chunk_pages([
        "Vendor onboarding risk review and compliance process.",
        "Quarterly operating report and staffing update.",
    ])

    results = search_chunks("vendor compliance risk", chunks)

    assert results
    assert results[0].page_number == 1


def test_report_json_includes_source_linked_findings():
    report = parse_document(str(SAMPLE_PATH))
    payload = json.loads(report_to_json(report))

    assert payload["summary"]["findings"]
    first = payload["summary"]["findings"][0]
    assert "page_number" in first
    assert "chunk_id" in first


def test_findings_dataframe_exposes_lineage_columns():
    report = parse_document(str(SAMPLE_PATH))
    dataframe = findings_to_dataframe(report)

    assert not dataframe.empty
    assert list(dataframe.columns) == ["finding_id", "category", "finding", "page", "chunk"]
    assert dataframe["page"].notna().all()


def test_empty_text_document_returns_safe_empty_intelligence(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    report = parse_document(str(file_path))

    assert report.summary.executive_summary == "No usable text was extracted from the document."
    assert report.summary.findings == []
    assert report.chunks == []
