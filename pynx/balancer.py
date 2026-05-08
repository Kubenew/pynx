from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Backend:
    url: str
    healthy: bool = True


class RoundRobin:
    def __init__(self, backends: List[Backend]):
        if not backends:
            raise ValueError("Upstream must have at least one backend.")
        self.backends = backends
        self._cycle = itertools.cycle(range(len(backends)))

    def next(self) -> Optional[Backend]:
        for _ in range(len(self.backends)):
            idx = next(self._cycle)
            b = self.backends[idx]
            if b.healthy:
                return b
        return None
