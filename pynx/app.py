from __future__ import annotations

import time
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from .router import Router
from .upstreams import UpstreamRegistry
from .proxy import forward
from .metrics import REQ_COUNT, REQ_LATENCY, metrics_response


def create_app(router: Router, upstreams: UpstreamRegistry, metrics_enabled: bool, metrics_path: str) -> Starlette:
    async def handler(request: Request) -> Response:
        start = time.perf_counter()

        location = router.resolve(request)
        if not location:
            return PlainTextResponse("No matching server/location", status_code=404)

        upstream = upstreams.get(location.upstream)
        backend = upstream.balancer.next()
        if not backend:
            return PlainTextResponse("No healthy upstream backend", status_code=503)

        resp = await forward(request, backend.url)

        duration = time.perf_counter() - start
        server_name = (request.headers.get("host") or "").split(":")[0]

        REQ_COUNT.labels(server_name=server_name, upstream=location.upstream, method=request.method, status=str(resp.status_code)).inc()
        REQ_LATENCY.labels(server_name=server_name, upstream=location.upstream).observe(duration)

        return resp

    routes = [
        Route("/{path:path}", endpoint=handler, methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
    ]

    if metrics_enabled:
        async def metrics_endpoint(request: Request):
            return metrics_response()
        routes.insert(0, Route(metrics_path, endpoint=metrics_endpoint, methods=["GET"]))

    return Starlette(routes=routes)
