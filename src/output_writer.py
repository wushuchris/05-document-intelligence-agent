import json
from typing import Dict

import pandas as pd

from src.document_schema import DocumentIntelligenceReport


def report_to_dict(report: DocumentIntelligenceReport) -> Dict:
    """Convert a Pydantic report into a regular dictionary."""
    return report.model_dump()


def report_to_json(report: DocumentIntelligenceReport) -> str:
    """Convert the full report into formatted JSON."""
    return json.dumps(report_to_dict(report), indent=2)


def chunks_to_dataframe(report: DocumentIntelligenceReport) -> pd.DataFrame:
    """Convert document chunks into a dataframe."""
    return pd.DataFrame([chunk.model_dump() for chunk in report.chunks])


def findings_to_dataframe(report: DocumentIntelligenceReport) -> pd.DataFrame:
    """Convert source-linked structured findings into a dataframe."""
    rows = []
    for finding in report.summary.findings:
        rows.append(
            {
                "finding_id": finding.finding_id,
                "category": finding.category.replace("_", " ").title(),
                "finding": finding.text,
                "page": finding.page_number,
                "chunk": finding.chunk_id,
            }
        )
    return pd.DataFrame(rows)


def metadata_to_dataframe(report: DocumentIntelligenceReport) -> pd.DataFrame:
    """Convert metadata into a dataframe."""
    return pd.DataFrame([report.metadata.model_dump()])


def summary_to_dataframe(report: DocumentIntelligenceReport) -> pd.DataFrame:
    """Convert summary fields into a simple dataframe."""
    summary = report.summary.model_dump(exclude={"findings"})

    rows = []
    for field, value in summary.items():
        if isinstance(value, list):
            display_value = "\n".join(value)
        else:
            display_value = value

        rows.append(
            {
                "field": field,
                "value": display_value,
            }
        )

    return pd.DataFrame(rows)
