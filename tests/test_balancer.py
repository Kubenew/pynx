import pytest
from pynx.balancer import Backend, RoundRobin


def test_round_robin_cycle():
    backends = [Backend(url="a"), Backend(url="b"), Backend(url="c")]
    rr = RoundRobin(backends)

    assert rr.next().url == "a"
    assert rr.next().url == "b"
    assert rr.next().url == "c"
    assert rr.next().url == "a"


def test_skip_unhealthy():
    backends = [Backend(url="a", healthy=False), Backend(url="b"), Backend(url="c", healthy=False)]
    rr = RoundRobin(backends)

    assert rr.next().url == "b"
    assert rr.next().url == "b"


def test_all_unhealthy():
    backends = [Backend(url="a", healthy=False), Backend(url="b", healthy=False)]
    rr = RoundRobin(backends)

    assert rr.next() is None


def test_empty_raises():
    with pytest.raises(ValueError):
        RoundRobin([])


def test_single_backend():
    backends = [Backend(url="only")]
    rr = RoundRobin(backends)

    assert rr.next().url == "only"
    assert rr.next().url == "only"
