from starlette.requests import Request
from pynx.router import Router, ServerBlock, Location


def make_request(host: str, path: str):
    return Request({
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"host", host.encode())],
        "query_string": b"",
        "server": ("127.0.0.1", 8080),
        "client": ("127.0.0.1", 12345),
        "scheme": "http",
    })


def test_longest_location_match():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[
                Location(path="/", type="prefix", upstream="a"),
                Location(path="/api", type="prefix", upstream="b"),
            ],
        )
    ])

    req = make_request("example.com", "/api/users")
    loc = router.resolve(req)
    assert loc is not None
    assert loc.upstream == "b"


def test_exact_match():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[
                Location(path="/", type="prefix", upstream="a"),
                Location(path="/api", type="exact", upstream="b"),
            ],
        )
    ])

    loc = router.resolve(make_request("example.com", "/api"))
    assert loc is not None
    assert loc.upstream == "b"

    loc = router.resolve(make_request("example.com", "/api/users"))
    assert loc is not None
    assert loc.upstream == "a"


def test_segment_boundary_matching():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[
                Location(path="/api", type="prefix", upstream="api_upstream"),
            ],
        )
    ])

    loc = router.resolve(make_request("example.com", "/api/users"))
    assert loc is not None

    loc = router.resolve(make_request("example.com", "/apixyz"))
    assert loc is None, "/api should not match /apixyz"

    loc = router.resolve(make_request("example.com", "/api"))
    assert loc is not None


def test_root_prefix_matches_everything():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[
                Location(path="/", type="prefix", upstream="default"),
            ],
        )
    ])

    assert router.resolve(make_request("example.com", "/")) is not None
    assert router.resolve(make_request("example.com", "/anything")) is not None


def test_no_matching_server():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[Location(path="/", type="prefix", upstream="a")],
        )
    ])

    loc = router.resolve(make_request("other.com", "/"))
    assert loc is None


def test_no_matching_location():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[Location(path="/api", type="exact", upstream="a")],
        )
    ])

    loc = router.resolve(make_request("example.com", "/"))
    assert loc is None


def test_host_header_with_port():
    router = Router([
        ServerBlock(
            listen="0.0.0.0:8080",
            server_name="example.com",
            locations=[Location(path="/", type="prefix", upstream="a")],
        )
    ])

    req = make_request("example.com:8080", "/")
    loc = router.resolve(req)
    assert loc is not None
