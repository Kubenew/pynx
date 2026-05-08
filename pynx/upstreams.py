from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .balancer import Backend, RoundRobin


@dataclass
class Upstream:
    name: str
    balancer: RoundRobin


class UpstreamRegistry:
    def __init__(self):
        self._upstreams: Dict[str, Upstream] = {}

    def register(self, name: str, urls: List[str]):
        backends = [Backend(url=u) for u in urls]
        self._upstreams[name] = Upstream(name=name, balancer=RoundRobin(backends))

    def get(self, name: str) -> Upstream:
        if name not in self._upstreams:
            raise KeyError(f"Upstream not found: {name}")
        return self._upstreams[name]

    def all_backends(self) -> List[Backend]:
        out: List[Backend] = []
        for up in self._upstreams.values():
            out.extend(up.balancer.backends)
        return out
