from pathlib import Path

from src.demo_presentation import (
    APP_CSS,
    CONTROL_BOUNDARY_HTML,
    HERO_HTML,
    PIPELINE_HTML,
)


def test_presentation_is_centered_and_business_first():
    assert "max-width: 1080px" in APP_CSS
    assert "What did this document say" in HERO_HTML
    assert "traced back to the source" in HERO_HTML


def test_presentation_explains_document_intelligence_boundary():
    assert "What this agent does" in CONTROL_BOUNDARY_HTML
    assert "What this agent does not claim" in CONTROL_BOUNDARY_HTML
    assert "does not prove that the document is true" in CONTROL_BOUNDARY_HTML


def test_pipeline_makes_source_lineage_explicit():
    assert "Parse" in PIPELINE_HTML
    assert "Structure" in PIPELINE_HTML
    assert "Preserve lineage" in PIPELINE_HTML
    assert "Search" in PIPELINE_HTML
    assert "Export" in PIPELINE_HTML


def test_streamlit_app_uses_real_observable_parser():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "parse_document_iter" in app_source
    assert "st.status" in app_source
    assert "Source lineage" in app_source
    assert "Search the original source" in app_source
