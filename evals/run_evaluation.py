from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from src.document_parser import parse_document


SAMPLE_PATH = Path("sample_docs/sample_business_memo.txt")
OUTPUT_DIR = Path("outputs")


def _contains(items: list[str], needle: str) -> bool:
    target = needle.lower()
    return any(target in item.lower() for item in items)


def _evaluate_report(case: dict, report) -> tuple[bool, list[str]]:
    failures: list[str] = []
    summary = report.summary

    if len(report.chunks) < case.get("min_chunks", 0):
        failures.append(f"expected at least {case['min_chunks']} chunks, got {len(report.chunks)}")

    if len(summary.findings) < case.get("min_findings", 0):
        failures.append(
            f"expected at least {case['min_findings']} findings, got {len(summary.findings)}"
        )

    if len(summary.key_facts) < case.get("min_key_facts", 0):
        failures.append(
            f"expected at least {case['min_key_facts']} key facts, got {len(summary.key_facts)}"
        )

    if len(summary.risks_or_issues) != case.get("risk_count", len(summary.risks_or_issues)):
        failures.append(
            f"expected {case['risk_count']} risks, got {len(summary.risks_or_issues)}"
        )

    if len(summary.action_items) != case.get("action_count", len(summary.action_items)):
        failures.append(
            f"expected {case['action_count']} actions, got {len(summary.action_items)}"
        )

    for expected_date in case.get("required_dates", []):
        if expected_date not in summary.important_dates:
            failures.append(f"missing expected date: {expected_date}")

    for expected_risk in case.get("required_risk_snippets", []):
        if not _contains(summary.risks_or_issues, expected_risk):
            failures.append(f"missing expected risk snippet: {expected_risk}")

    for expected_action in case.get("required_action_snippets", []):
        if not _contains(summary.action_items, expected_action):
            failures.append(f"missing expected action snippet: {expected_action}")

    if case.get("expect_no_findings") and summary.findings:
        failures.append(f"expected no findings, got {len(summary.findings)}")

    if case.get("expected_summary") and summary.executive_summary != case["expected_summary"]:
        failures.append("executive summary did not match expected safe fallback")

    if summary.findings:
        unlinked = [finding.finding_id for finding in summary.findings if finding.page_number < 1]
        if unlinked:
            failures.append(f"findings missing valid page lineage: {unlinked}")

    return not failures, failures


def main() -> int:
    cases = [
        {
            "case_id": "northstar_sample",
            "title": "Synthetic Northstar operations memo",
            "source_path": SAMPLE_PATH,
            "min_chunks": 1,
            "min_findings": 10,
            "required_dates": ["March 15, 2026", "April 30, 2026", "Q2 2026"],
            "required_risk_snippets": ["scanned PDFs"],
            "required_action_snippets": ["synthetic"],
        },
        {
            "case_id": "risk_action_note",
            "title": "Risk and action extraction",
            "text": (
                "Atlas Compliance Team will review the vendor renewal on May 20, 2026. "
                "There is a risk that supporting evidence will arrive late. "
                "The compliance lead should review exceptions before approval."
            ),
            "min_chunks": 1,
            "min_findings": 4,
            "required_dates": ["May 20, 2026"],
            "required_risk_snippets": ["supporting evidence"],
            "required_action_snippets": ["review exceptions"],
        },
        {
            "case_id": "neutral_note",
            "title": "Neutral factual note",
            "text": (
                "Orion Facilities completed the lobby repainting project. "
                "Employees attended the quarterly community event."
            ),
            "min_chunks": 1,
            "min_key_facts": 2,
            "risk_count": 0,
            "action_count": 0,
        },
        {
            "case_id": "empty_document",
            "title": "Empty document safe fallback",
            "text": "",
            "min_chunks": 0,
            "expect_no_findings": True,
            "expected_summary": "No usable text was extracted from the document.",
        },
    ]

    results = []
    with tempfile.TemporaryDirectory(prefix="agent5_eval_") as temp_dir:
        for case in cases:
            source_path = case.get("source_path")
            if source_path is None:
                source_path = Path(temp_dir) / f"{case['case_id']}.txt"
                source_path.write_text(case.get("text", ""), encoding="utf-8")

            try:
                report = parse_document(str(source_path))
                passed, failures = _evaluate_report(case, report)
                results.append(
                    {
                        "case_id": case["case_id"],
                        "title": case["title"],
                        "passed": passed,
                        "failures": failures,
                        "chunk_count": len(report.chunks),
                        "finding_count": len(report.summary.findings),
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "case_id": case["case_id"],
                        "title": case["title"],
                        "passed": False,
                        "failures": [str(exc)],
                        "chunk_count": 0,
                        "finding_count": 0,
                    }
                )

    passed_cases = sum(1 for result in results if result["passed"])
    summary = {
        "total_cases": len(results),
        "passed_cases": passed_cases,
        "failed_cases": len(results) - passed_cases,
        "case_accuracy": passed_cases / len(results) if results else 0.0,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "evaluation_results.json").write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"[{status}] {result['case_id']}: chunks={result['chunk_count']} "
            f"findings={result['finding_count']}"
        )
        for failure in result["failures"]:
            print(f"  - {failure}")

    print(json.dumps(summary, indent=2))
    print(OUTPUT_DIR / "evaluation_results.json")
    print(OUTPUT_DIR / "evaluation_summary.json")

    return 0 if passed_cases == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
