# Elementor QA Automation (FastAPI + React + Tailwind)

Full-stack local web app for automated QA of WordPress Elementor pages.

## Features

- **Single and bulk URL checks** with async processing and queue worker.
- **Content QA**: missing headings, duplicate headings, empty sections, spelling warnings.
- **Buttons/Links QA**: broken links, clickable issues, external target checks.
- **Image QA**: missing alt tags, broken images, >500 KB optimization warnings.
- **Responsive QA**: screenshots at mobile/tablet/desktop/large-monitor + overflow/cut-off checks.
- **SEO/Accessibility QA**: title/description checks, heading hierarchy, labels, basic contrast checks.
- **Performance**: page load time, LCP, CLS metrics.
- **Security**: insecure HTTP resources + non-HTTPS page checks.
- **Reports**: JSON + PDF generation backend, JSON/PDF download in frontend, CSV export for bulk summary.
- **Retries and logging** implemented for scan reliability.

---

## Project Structure

```
backend/
  main.py
  models.py
  queue_manager.py
  scanner.py
  reporter.py
  qa_checks/
frontend/
  src/
```

---

## Local Setup

### 1) Backend

```bash
cd backend
pip install fastapi uvicorn playwright pdfkit requests python-magic spellchecker
pip install -r requirements.txt
playwright install
uvicorn main:app --reload
```

API runs at: `http://localhost:8000`

### 2) Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at: `http://localhost:3000`

---

## API Endpoints

- `POST /check-page`
  - Body: `{ "url": "https://example.com" }`
- `POST /check-bulk`
  - Body: `{ "urls": ["https://example.com", "https://example.org"] }`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/summary.csv`

---

## Sample Code Snippets

### 1) Checking links and buttons

```python
links = await page.eval_on_selector_all(
    "a, button",
    "els => els.map(el => ({tag: el.tagName.toLowerCase(), href: el.href || null, target: el.target || null}))",
)
for link in links:
    if link["href"]:
        response = requests.head(link["href"], timeout=8, allow_redirects=True)
        if response.status_code >= 400:
            ...
```

### 2) Capturing screenshots at multiple resolutions

```python
for name, viewport in VIEWPORTS.items():
    await page.set_viewport_size(viewport)
    await page.wait_for_timeout(600)
    await page.screenshot(path=f"reports/{name}.png", full_page=True)
```

### 3) Detecting missing headings and alt tags

```python
headings = await page.eval_on_selector_all("h1, h2, h3, h4, h5, h6", "els => els.map(el => el.textContent.trim())")
if not headings:
    issues.append("No headings found")

images = await page.eval_on_selector_all("img", "els => els.map(el => ({src: el.currentSrc || el.src, alt: el.alt || ''}))")
for image in images:
    if not image["alt"].strip():
        issues.append("Missing alt tag")
```

### 4) Measuring performance metrics

```python
metrics = await page.evaluate("""
() => {
  const nav = performance.getEntriesByType('navigation')[0];
  return {
    page_load_time_ms: nav ? nav.duration : null,
    lcp: performance.getEntriesByType('largest-contentful-paint').slice(-1)[0]?.startTime || null,
    cls: performance.getEntriesByType('layout-shift').reduce((sum, e) => sum + (e.hadRecentInput ? 0 : e.value), 0)
  };
}
""")
```

### 5) Generating JSON/PDF reports

```python
json_path = write_json_report(report_data, "reports", "qa_report")
pdf_path = write_pdf_report(report_data, "reports", "qa_report")
```

### 6) React report rendering + downloads

```jsx
<button onClick={downloadJson}>Download JSON</button>
<button onClick={downloadPdf}>Download PDF</button>
{results.map(result => <ReportCard key={result.url} data={result} />)}
```

---

## Optional/Advanced Features to Extend

- Slack/email notifications for failed QA runs.
- Scheduler (APScheduler/Celery beat/cron) for recurring checks.
- Admin dashboard for multiple sites and historical trends.
- AI-based design suggestions (spacing/typography/CTA prominence).
- Detection of redundant plugins/scripts from page script/resource inventory.
