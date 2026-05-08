from __future__ import annotations

import asyncio
import typer
import uvicorn

from .config import load_config
from .router import Router, ServerBlock, Location
from .upstreams import UpstreamRegistry
from .app import create_app
from .healthcheck import HealthChecker

app = typer.Typer(help="pynx - Nginx-like async reverse proxy in Python")


@app.command()
def run(config: str = typer.Option(..., "--config", "-c", help="Path to pynx YAML config file")):
    cfg = load_config(config)

    upstreams = UpstreamRegistry()
    for up in cfg.upstreams:
        upstreams.register(up.name, [s.url for s in up.servers])

    server_blocks = []
    for srv in cfg.servers:
        locations = [Location(path=l.path, type=l.type, upstream=l.upstream) for l in srv.locations]
        server_blocks.append(ServerBlock(listen=srv.listen, server_name=srv.server_name, locations=locations))

    router = Router(server_blocks)

    if not server_blocks:
        raise typer.BadParameter("No servers configured.")

    listen = server_blocks[0].listen
    host, port = "0.0.0.0", 8080
    if ":" in listen:
        host, port_str = listen.split(":", 1)
        port = int(port_str)
    else:
        raise typer.BadParameter(f"Invalid listen address: {listen}")

    starlette_app = create_app(
        router=router,
        upstreams=upstreams,
        metrics_enabled=cfg.metrics.enabled,
        metrics_path=cfg.metrics.path,
    )

    if cfg.healthcheck.enabled:
        checker = HealthChecker(timeout_seconds=cfg.healthcheck.timeout_seconds)

        @starlette_app.on_event("startup")
        async def start_healthcheck():
            asyncio.create_task(
                checker.loop(
                    registry=upstreams,
                    interval_seconds=cfg.healthcheck.interval_seconds,
                    path=cfg.healthcheck.path,
                )
            )

    uvicorn.run(starlette_app, host=host, port=port)
