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
