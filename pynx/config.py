from __future__ import annotations

from dataclasses import dataclass
from typing import List
import yaml


class ConfigError(Exception):
    pass


@dataclass
class LocationConfig:
    path: str
    type: str  # "prefix" or "exact"
    upstream: str


@dataclass
class ServerConfig:
    listen: str
    server_name: str
    locations: List[LocationConfig]


@dataclass
class UpstreamServerConfig:
    url: str


@dataclass
class UpstreamConfig:
    name: str
    servers: List[UpstreamServerConfig]


@dataclass
class MetricsConfig:
    enabled: bool = False
    path: str = "/metrics"


@dataclass
class HealthcheckConfig:
    enabled: bool = False
    interval_seconds: int = 5
    timeout_seconds: int = 2
    path: str = "/health"


@dataclass
class PynxConfig:
    servers: List[ServerConfig]
    upstreams: List[UpstreamConfig]
    metrics: MetricsConfig
    healthcheck: HealthcheckConfig


def _validate(raw: dict):
    servers = raw.get("servers")
    if not servers:
        raise ConfigError("At least one server block is required.")

    for i, srv in enumerate(servers):
        if "listen" not in srv:
            raise ConfigError(f"server[{i}]: 'listen' is required.")
        if "server_name" not in srv:
            raise ConfigError(f"server[{i}]: 'server_name' is required.")
        if "locations" not in srv or not srv["locations"]:
            raise ConfigError(f"server[{i}]: at least one location is required.")
        for j, loc in enumerate(srv["locations"]):
            if "path" not in loc:
                raise ConfigError(f"server[{i}].locations[{j}]: 'path' is required.")
            if "upstream" not in loc:
                raise ConfigError(f"server[{i}].locations[{j}]: 'upstream' is required.")

    upstreams = raw.get("upstreams")
    if not upstreams:
        raise ConfigError("At least one upstream is required.")
    for name, up in upstreams.items():
        if "servers" not in up or not up["servers"]:
            raise ConfigError(f"upstream '{name}': at least one server is required.")
        for j, srv in enumerate(up["servers"]):
            if "url" not in srv:
                raise ConfigError(f"upstream '{name}'.servers[{j}]: 'url' is required.")

    for srv in servers:
        for loc in srv.get("locations") or []:
            up_name = loc["upstream"]
            if up_name not in upstreams:
                raise ConfigError(f"upstream '{up_name}' referenced by location '{loc['path']}' not defined.")


def load_config(path: str) -> PynxConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    _validate(raw)

    servers: List[ServerConfig] = []
    for srv in raw.get("servers") or []:
        locs: List[LocationConfig] = []
        for loc in srv.get("locations") or []:
            locs.append(LocationConfig(
                path=str(loc["path"]),
                type=str(loc.get("type", "prefix")),
                upstream=str(loc["upstream"]),
            ))
        servers.append(ServerConfig(
            listen=str(srv["listen"]),
            server_name=str(srv["server_name"]),
            locations=locs,
        ))

    upstreams: List[UpstreamConfig] = []
    for name, up in (raw.get("upstreams") or {}).items():
        servers_raw = up.get("servers") or []
        upstreams.append(UpstreamConfig(
            name=str(name),
            servers=[UpstreamServerConfig(url=str(s["url"])) for s in servers_raw],
        ))

    metrics_raw = raw.get("metrics") or {}
    metrics = MetricsConfig(
        enabled=bool(metrics_raw.get("enabled", False)),
        path=str(metrics_raw.get("path", "/metrics")),
    )

    hc_raw = raw.get("healthcheck") or {}
    healthcheck = HealthcheckConfig(
        enabled=bool(hc_raw.get("enabled", False)),
        interval_seconds=int(hc_raw.get("interval_seconds", 5)),
        timeout_seconds=int(hc_raw.get("timeout_seconds", 2)),
        path=str(hc_raw.get("path", "/health")),
    )

    return PynxConfig(
        servers=servers,
        upstreams=upstreams,
        metrics=metrics,
        healthcheck=healthcheck,
    )
