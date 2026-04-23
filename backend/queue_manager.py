from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import uuid4

from models import JobStatus
from scanner import scan_page


class BulkQueue:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[tuple[str, list[str]]] = asyncio.Queue()
        self.jobs: dict[str, JobStatus] = {}
        self.worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._worker())

    async def enqueue(self, urls: list[str]) -> str:
        job_id = uuid4().hex
        self.jobs[job_id] = JobStatus(
            job_id=job_id,
            status="queued",
            created_at=datetime.utcnow(),
            total=len(urls),
            completed=0,
        )
        await self.queue.put((job_id, urls))
        return job_id

    def get_status(self, job_id: str) -> JobStatus | None:
        return self.jobs.get(job_id)

    async def _worker(self) -> None:
        while True:
            job_id, urls = await self.queue.get()
            job = self.jobs[job_id]
            job.status = "running"
            for index, url in enumerate(urls, start=1):
                result = await scan_page(url)
                job.results.append(result)
                job.completed = index
                job.progress = (index / len(urls)) * 100
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.queue.task_done()
