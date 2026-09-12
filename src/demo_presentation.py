APP_CSS = """
<style>
    .block-container {
        max-width: 1080px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .doc-hero {
        padding: 1.45rem 1.55rem;
        border: 1px solid rgba(120, 120, 120, 0.25);
        border-radius: 18px;
        margin-bottom: 1rem;
    }
    .doc-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.72;
        margin-bottom: 0.35rem;
    }
    .doc-hero h1 {
        font-size: 2.15rem;
        line-height: 1.15;
        margin: 0 0 0.65rem 0;
    }
    .doc-hero p {
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0;
        opacity: 0.9;
    }
    .principle-card, .boundary-card {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(120, 120, 120, 0.22);
        border-radius: 14px;
        min-height: 100%;
    }
    .principle-card strong, .boundary-card strong {
        display: block;
        margin-bottom: 0.3rem;
    }
    .pipeline-step {
        padding: 0.85rem 1rem;
        margin: 0.45rem 0;
        border-left: 4px solid rgba(100, 120, 220, 0.75);
        background: rgba(120, 120, 120, 0.06);
        border-radius: 0 12px 12px 0;
    }
    .summary-callout {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(120, 120, 120, 0.22);
        border-radius: 14px;
        margin-bottom: 0.75rem;
    }
    .lineage-note {
        padding: 0.9rem 1rem;
        border-radius: 12px;
        background: rgba(80, 130, 210, 0.08);
        border: 1px solid rgba(80, 130, 210, 0.22);
    }
</style>
"""


HERO_HTML = """
<div class="doc-hero">
  <div class="doc-eyebrow">Agent 5 · Document Intelligence</div>
  <h1>What did this document say — and can every extracted item be traced back to the source?</h1>
  <p>
    Long documents become useful only when people can turn them into structured work products without losing
    the connection to the original text. This agent parses a document, creates page-aware chunks, extracts
    lightweight structured intelligence, preserves source lineage, supports search, and exports an auditable record.
  </p>
</div>
"""


WHY_IT_MATTERS_HTML = """
<div class="principle-card">
  <strong>The business problem</strong>
  Analysts often re-read documents, copy facts into spreadsheets, and lose track of which page supported a conclusion.
</div>
"""


CONTROL_BOUNDARY_HTML = """
<div class="boundary-card">
  <strong>What this agent does</strong>
  Converts selectable PDF/TXT text into structured, searchable, source-linked outputs using transparent local rules.
</div>
<div style="height: 0.65rem"></div>
<div class="boundary-card">
  <strong>What this agent does not claim</strong>
  It does not prove that the document is true, perform OCR on scanned pages, or replace expert review of consequential documents.
</div>
"""


PIPELINE_HTML = """
<div class="pipeline-step"><strong>1 · Parse</strong><br>Read selectable PDF or plain-text content and record extraction notes.</div>
<div class="pipeline-step"><strong>2 · Structure</strong><br>Create validated metadata, page-aware chunks, and lightweight summary fields.</div>
<div class="pipeline-step"><strong>3 · Preserve lineage</strong><br>Attach extracted facts, dates, entities, risks, and actions to their source page and chunk.</div>
<div class="pipeline-step"><strong>4 · Search</strong><br>Search the original document chunks rather than searching only a rewritten summary.</div>
<div class="pipeline-step"><strong>5 · Export</strong><br>Produce structured JSON/CSV records that preserve the extraction and source references.</div>
"""


LIMITS_MARKDOWN = """
### Interpretation boundary

The structured findings are **extractions from the supplied document**, not independent verification that the document is correct.

- Summary generation uses transparent deterministic rules, not a hosted LLM.
- Source lineage means an extracted item can be traced back to the page/chunk where it appeared.
- Source lineage does **not** mean the source statement is true.
- Scanned PDFs without selectable text may require OCR and are intentionally reported as a limitation rather than silently guessed.
- Tables, complex layouts, nuanced entity resolution, and multi-document comparison remain production-upgrade opportunities.
- High-stakes legal, medical, financial, compliance, or client documents should receive expert review.
"""


ARCHITECTURE_MARKDOWN = """
### Engineering architecture

```text
PDF / TXT
   ↓
Deterministic text extraction
   ↓
Page-aware normalized text
   ↓
Overlapping document chunks
   ↓
Transparent structured extraction
   ├─ executive summary
   ├─ key facts
   ├─ entities
   ├─ dates
   ├─ risks
   └─ action items
   ↓
Source-lineage mapping
   ├─ page number
   └─ chunk ID
   ↓
Validated Pydantic report
   ├─ search
   ├─ JSON export
   └─ CSV export
```

**Control principle:** parsing and extraction are deterministic application logic. The system does not ask an LLM to invent structure or provenance.
"""
