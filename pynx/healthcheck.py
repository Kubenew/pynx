from __future__ import annotations

import asyncio
import httpx

from .upstreams import UpstreamRegistry


class HealthChecker:
    def __init__(self, timeout_seconds: int):
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def _check(self, url: str, path: str) -> bool:
        try:
            r = await self._client.get(url.rstrip("/") + path)
            return 200 <= r.status_code < 400
        except Exception:
            return False

    async def loop(self, registry: UpstreamRegistry, interval_seconds: int, path: str):
        while True:
            for backend in registry.all_backends():
                backend.healthy = await self._check(backend.url, path)
            await asyncio.sleep(interval_seconds)

    async def close(self):
        await self._client.aclose()
