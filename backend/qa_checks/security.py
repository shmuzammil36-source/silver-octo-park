from __future__ import annotations

from urllib.parse import urlparse

from playwright.async_api import Page

from models import QAIssue, Severity


async def run_security_checks(page: Page) -> list[QAIssue]:
    issues: list[QAIssue] = []

    resources = await page.evaluate(
        """
        () => performance.getEntriesByType('resource').map(r => r.name)
        """
    )

    insecure = [url for url in resources if url.startswith("http://")]
    for item in insecure[:20]:
        issues.append(
            QAIssue(
                category="Security",
                severity=Severity.high,
                message=f"Insecure HTTP resource: {item}",
            )
        )

    page_url = page.url
    if urlparse(page_url).scheme != "https":
        issues.append(
            QAIssue(
                category="Security",
                severity=Severity.high,
                message=f"Page served over non-HTTPS: {page_url}",
            )
        )

    return issues
