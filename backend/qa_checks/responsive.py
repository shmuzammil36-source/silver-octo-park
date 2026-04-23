from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from models import QAIssue, Severity

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1366, "height": 768},
    "large_monitor": {"width": 1920, "height": 1080},
}


async def run_responsive_checks(page: Page, output_dir: Path) -> tuple[list[QAIssue], dict[str, str]]:
    issues: list[QAIssue] = []
    screenshots: dict[str, str] = {}

    for name, viewport in VIEWPORTS.items():
        await page.set_viewport_size(viewport)
        await page.wait_for_timeout(600)
        path = output_dir / f"{name}.png"
        await page.screenshot(path=str(path), full_page=True)
        screenshots[name] = str(path)

        overflow_nodes = await page.evaluate(
            """
            () => {
              const nodes = Array.from(document.querySelectorAll('body *'));
              return nodes
                .filter(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.right > window.innerWidth + 2 || rect.bottom > document.documentElement.scrollHeight + 2;
                })
                .slice(0, 10)
                .map(el => el.tagName + (el.className ? '.' + el.className : ''));
            }
            """
        )
        for node in overflow_nodes:
            issues.append(
                QAIssue(
                    category="Responsive",
                    severity=Severity.medium,
                    message=f"Possible cut-off/overflow element at {name}: {node}",
                )
            )

    return issues, screenshots
