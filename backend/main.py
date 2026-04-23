from __future__ import annotations

import csv
import io
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import BulkRequest, PageRequest
from queue_manager import BulkQueue
from scanner import scan_page

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Elementor QA API", version="1.0.0")
queue = BulkQueue()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    await queue.start()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/check-page")
async def check_page(request: PageRequest):
    result = await scan_page(str(request.url))
    return result


@app.post("/check-bulk")
async def check_bulk(request: BulkRequest):
    urls = [str(u) for u in request.urls]
    if not urls:
        raise HTTPException(status_code=400, detail="At least one URL is required")
    job_id = await queue.enqueue(urls)
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = queue.get_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/{job_id}/summary.csv")
async def get_job_csv(job_id: str):
    job = queue.get_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["url", "status", "issues", "high", "medium", "low"])

    for result in job.results:
        severities = {"high": 0, "medium": 0, "low": 0}
        for issue in result.issues:
            severities[issue.severity.value] += 1
        writer.writerow(
            [
                result.url,
                result.status,
                len(result.issues),
                severities["high"],
                severities["medium"],
                severities["low"],
            ]
        )

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={job_id}-summary.csv"},
    )
