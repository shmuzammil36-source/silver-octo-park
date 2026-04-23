from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from playwright.async_api import Browser, async_playwright

from models import PageResult
from qa_checks.content import run_content_checks
from qa_checks.images import run_image_checks
from qa_checks.links import run_link_checks
from qa_checks.performance import run_performance_checks
from qa_checks.responsive import run_responsive_checks
from qa_checks.security import run_security_checks
from qa_checks.seo_accessibility import run_seo_accessibility_checks
from qa_checks.utils import ensure_dir, with_retries
from reporter import write_json_report, write_pdf_report

logger = logging.getLogger(__name__)


async def _open_browser() -> Browser:
    playwright = await async_playwright().start()
    return await playwright.chromium.launch(headless=True)


async def scan_page(url: str, reports_root: str = "reports") -> PageResult:
    report_id = f"report-{uuid4().hex[:8]}"
    page_dir = ensure_dir(Path(reports_root) / report_id)

    async def _scan() -> PageResult:
        browser = await _open_browser()
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=45000)

        issues = []
        issues += await run_content_checks(page)
        issues += await run_link_checks(page, url)
        issues += await run_image_checks(page)
        responsive_issues, screenshots = await run_responsive_checks(page, page_dir)
        issues += responsive_issues
        issues += await run_seo_accessibility_checks(page)
        issues += await run_security_checks(page)
        metrics = await run_performance_checks(page)

        result = PageResult(
            url=url,
            checked_at=datetime.utcnow(),
            issues=issues,
            metrics=metrics,
            screenshots=screenshots,
            status="success",
        )

        report_data = result.model_dump()
        write_json_report(report_data, page_dir, "qa_report")
        write_pdf_report(report_data, page_dir, "qa_report")

        await context.close()
        await browser.close()
        return result

    try:
        return await with_retries(_scan, retries=2, delay_seconds=2)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to scan %s", url)
        return PageResult(
            url=url,
            checked_at=datetime.utcnow(),
            issues=[],
            metrics={},
            screenshots={},
            status=f"failed: {exc}",
        )
