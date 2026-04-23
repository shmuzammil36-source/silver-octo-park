from __future__ import annotations

from urllib.parse import urlparse

import requests
from playwright.async_api import Page

from models import QAIssue, Severity


async def run_link_checks(page: Page, base_url: str) -> list[QAIssue]:
    issues: list[QAIssue] = []
    links = await page.eval_on_selector_all(
        "a, button",
        "els => els.map(el => ({tag: el.tagName.toLowerCase(), text: el.innerText?.trim(), href: el.href || null, target: el.target || null, disabled: el.disabled || false }))",
    )

    for link in links:
        tag = link.get("tag")
        href = link.get("href")
        text = link.get("text") or tag
        if tag == "button" and not href and link.get("disabled"):
            issues.append(
                QAIssue(
                    category="Buttons",
                    severity=Severity.medium,
                    message=f"Disabled button detected: {text}",
                )
            )
            continue

        if href:
            try:
                response = requests.head(href, timeout=8, allow_redirects=True)
                if response.status_code >= 400:
                    issues.append(
                        QAIssue(
                            category="Buttons",
                            severity=Severity.high,
                            message=f"Broken URL ({response.status_code}): {href}",
                        )
                    )
            except Exception:
                issues.append(
                    QAIssue(
                        category="Buttons",
                        severity=Severity.high,
                        message=f"Unreachable URL: {href}",
                    )
                )

            base_host = urlparse(base_url).hostname
            current_host = urlparse(href).hostname
            if current_host and base_host and current_host != base_host and link.get("target") != "_blank":
                issues.append(
                    QAIssue(
                        category="Buttons",
                        severity=Severity.medium,
                        message=f"External link should open in new tab: {href}",
                    )
                )

    return issues
