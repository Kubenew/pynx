import pytest
from pynx.upstreams import UpstreamRegistry


def test_register_and_get():
    registry = UpstreamRegistry()
    registry.register("api", ["http://localhost:5000", "http://localhost:5001"])

    up = registry.get("api")
    assert up.name == "api"
    assert len(up.balancer.backends) == 2


def test_get_missing():
    registry = UpstreamRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_all_backends():
    registry = UpstreamRegistry()
    registry.register("a", ["http://a1", "http://a2"])
    registry.register("b", ["http://b1"])

    backends = registry.all_backends()
    assert len(backends) == 3
    assert all(b.healthy for b in backends)
