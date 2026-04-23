from __future__ import annotations

from playwright.async_api import Page

from models import QAIssue, Severity


async def run_seo_accessibility_checks(page: Page) -> list[QAIssue]:
    issues: list[QAIssue] = []

    title = await page.title()
    if not title.strip():
        issues.append(QAIssue(category="SEO", severity=Severity.high, message="Missing meta title"))

    description = await page.get_attribute("meta[name='description']", "content")
    if not description:
        issues.append(
            QAIssue(category="SEO", severity=Severity.medium, message="Missing meta description")
        )

    heading_levels = await page.eval_on_selector_all(
        "h1, h2, h3, h4, h5, h6", "els => els.map(el => Number(el.tagName[1]))"
    )
    for idx in range(1, len(heading_levels)):
        if heading_levels[idx] - heading_levels[idx - 1] > 1:
            issues.append(
                QAIssue(
                    category="SEO",
                    severity=Severity.medium,
                    message="Heading hierarchy skip detected",
                )
            )
            break

    unlabeled_inputs = await page.eval_on_selector_all(
        "input, select, textarea",
        "els => els.filter(el => !el.labels?.length && !el.getAttribute('aria-label')).length",
    )
    if unlabeled_inputs:
        issues.append(
            QAIssue(
                category="Accessibility",
                severity=Severity.high,
                message=f"{unlabeled_inputs} form controls have no label",
            )
        )

    low_contrast_count = await page.evaluate(
        """
        () => {
          const rgbToLum = (rgb) => {
            const c = rgb.match(/\d+/g)?.slice(0,3).map(v => {
              const n = Number(v)/255;
              return n <= 0.03928 ? n/12.92 : Math.pow((n+0.055)/1.055, 2.4);
            });
            if (!c) return null;
            return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2];
          };
          const ratio = (l1,l2) => (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
          let count = 0;
          document.querySelectorAll('p, span, a, button, h1, h2, h3').forEach(el => {
            const style = window.getComputedStyle(el);
            const fg = rgbToLum(style.color);
            const bg = rgbToLum(style.backgroundColor === 'rgba(0, 0, 0, 0)' ? 'rgb(255,255,255)' : style.backgroundColor);
            if (fg !== null && bg !== null && ratio(fg,bg) < 4.5) count += 1;
          });
          return count;
        }
        """
    )
    if low_contrast_count:
        issues.append(
            QAIssue(
                category="Accessibility",
                severity=Severity.medium,
                message=f"Potential low-contrast text elements: {low_contrast_count}",
            )
        )

    return issues
