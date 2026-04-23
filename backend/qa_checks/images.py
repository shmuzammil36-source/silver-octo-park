from __future__ import annotations

import requests
from playwright.async_api import Page

from models import QAIssue, Severity


async def run_image_checks(page: Page) -> list[QAIssue]:
    issues: list[QAIssue] = []

    images = await page.eval_on_selector_all(
        "img",
        "els => els.map(el => ({src: el.currentSrc || el.src, alt: el.alt || ''}))",
    )

    for image in images:
        src = image.get("src")
        alt = (image.get("alt") or "").strip()

        if not alt:
            issues.append(
                QAIssue(
                    category="Images",
                    severity=Severity.medium,
                    message=f"Missing alt tag: {src}",
                )
            )

        if not src:
            issues.append(
                QAIssue(category="Images", severity=Severity.high, message="Image has no source")
            )
            continue

        try:
            response = requests.get(src, timeout=10)
            if response.status_code >= 400:
                issues.append(
                    QAIssue(
                        category="Images",
                        severity=Severity.high,
                        message=f"Broken image: {src}",
                    )
                )
            size_kb = len(response.content) / 1024
            if size_kb > 500:
                issues.append(
                    QAIssue(
                        category="Images",
                        severity=Severity.low,
                        message=f"Image >500KB ({int(size_kb)}KB): {src}",
                    )
                )
        except Exception:
            issues.append(
                QAIssue(
                    category="Images",
                    severity=Severity.high,
                    message=f"Failed to fetch image: {src}",
                )
            )

    return issues
