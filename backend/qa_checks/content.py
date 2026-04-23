from __future__ import annotations

import re
from collections import Counter

from playwright.async_api import Page
from spellchecker import SpellChecker

from models import QAIssue, Severity

spell = SpellChecker()


async def run_content_checks(page: Page) -> list[QAIssue]:
    issues: list[QAIssue] = []

    headings = await page.eval_on_selector_all(
        "h1, h2, h3, h4, h5, h6", "els => els.map(el => el.textContent.trim())"
    )
    if not headings:
        issues.append(
            QAIssue(category="Content", severity=Severity.high, message="No headings found")
        )

    duplicates = [h for h, count in Counter(headings).items() if count > 1 and h]
    for dup in duplicates:
        issues.append(
            QAIssue(
                category="Content",
                severity=Severity.medium,
                message=f"Duplicate heading detected: '{dup}'",
            )
        )

    empty_sections = await page.eval_on_selector_all(
        "section, .elementor-section",
        "els => els.filter(el => !el.innerText.trim()).map(el => el.className || el.tagName)",
    )
    for section in empty_sections:
        issues.append(
            QAIssue(
                category="Content",
                severity=Severity.low,
                message=f"Empty section detected: {section}",
            )
        )

    body_text = await page.text_content("body") or ""
    tokens = re.findall(r"[A-Za-z]{4,}", body_text.lower())
    unknown = [w for w in spell.unknown(tokens) if len(w) > 6][:15]
    for word in unknown:
        issues.append(
            QAIssue(
                category="Content",
                severity=Severity.low,
                message=f"Possible spelling issue: {word}",
            )
        )

    return issues
