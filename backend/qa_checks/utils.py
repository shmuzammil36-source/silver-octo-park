from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar


T = TypeVar("T")
logger = logging.getLogger(__name__)


def ensure_dir(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


async def with_retries(
    fn: Callable[[], Awaitable[T]], retries: int = 2, delay_seconds: float = 1.0
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return await fn()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Attempt %s failed: %s", attempt, exc)
            if attempt <= retries:
                await asyncio.sleep(delay_seconds * attempt)
    assert last_error is not None
    raise last_error
