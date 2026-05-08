from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from starlette.requests import Request


@dataclass
class Location:
    path: str
    type: str  # prefix | exact
    upstream: str

    def match(self, request: Request) -> bool:
        if self.type == "exact":
            return request.url.path == self.path
        return request.url.path.startswith(self.path)


@dataclass
class ServerBlock:
    listen: str
    server_name: str
    locations: List[Location]

    def match_host(self, request: Request) -> bool:
        host = (request.headers.get("host") or "").split(":")[0]
        return host == self.server_name


class Router:
    def __init__(self, servers: List[ServerBlock]):
        self.servers = servers

    def resolve(self, request: Request) -> Optional[Location]:
        server = None
        for s in self.servers:
            if s.match_host(request):
                server = s
                break

        if not server:
            return None

        matched = [loc for loc in server.locations if loc.match(request)]
        if not matched:
            return None

        matched.sort(key=lambda l: len(l.path), reverse=True)
        return matched[0]
