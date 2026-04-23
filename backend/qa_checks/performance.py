from __future__ import annotations

from playwright.async_api import Page


async def run_performance_checks(page: Page) -> dict:
    metrics = await page.evaluate(
        """
        () => new Promise((resolve) => {
          const nav = performance.getEntriesByType('navigation')[0];
          const lcpEntry = performance.getEntriesByType('largest-contentful-paint').slice(-1)[0];
          let cls = 0;
          for (const e of performance.getEntriesByType('layout-shift')) {
            if (!e.hadRecentInput) cls += e.value;
          }
          resolve({
            page_load_time_ms: nav ? nav.duration : null,
            dom_content_loaded_ms: nav ? nav.domContentLoadedEventEnd : null,
            largest_contentful_paint_ms: lcpEntry ? lcpEntry.startTime : null,
            cumulative_layout_shift: cls,
          });
        })
        """
    )
    return metrics
