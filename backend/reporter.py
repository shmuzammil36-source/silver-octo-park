from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pdfkit

from qa_checks.utils import ensure_dir


def write_json_report(report_data: dict[str, Any], output_dir: str | Path, report_name: str) -> str:
    output = ensure_dir(output_dir) / f"{report_name}.json"
    output.write_text(json.dumps(report_data, indent=2, default=str), encoding="utf-8")
    return str(output)


def write_pdf_report(report_data: dict[str, Any], output_dir: str | Path, report_name: str) -> str | None:
    html = f"""
    <html><body>
    <h1>WordPress Elementor QA Report</h1>
    <h2>{report_data.get('url', 'Bulk Report')}</h2>
    <pre>{json.dumps(report_data, indent=2, default=str)}</pre>
    </body></html>
    """
    output = ensure_dir(output_dir) / f"{report_name}.pdf"
    try:
        pdfkit.from_string(html, str(output))
        return str(output)
    except Exception:
        return None
