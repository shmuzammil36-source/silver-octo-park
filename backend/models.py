from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class QAIssue(BaseModel):
    category: str
    severity: Severity
    message: str
    selector: str | None = None
    metadata: dict[str, Any] | None = None


class PageRequest(BaseModel):
    url: HttpUrl


class BulkRequest(BaseModel):
    urls: list[HttpUrl]


class PageResult(BaseModel):
    url: str
    checked_at: datetime
    issues: list[QAIssue]
    metrics: dict[str, Any]
    screenshots: dict[str, str]
    status: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    progress: float = 0
    total: int = 0
    completed: int = 0
    results: list[PageResult] = Field(default_factory=list)
    error: str | None = None
