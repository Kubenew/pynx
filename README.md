# pynx

**pynx** is a minimal Nginx-like async reverse proxy / edge router written in Python.

## Features (MVP)
- Reverse proxy (HTTP)
- Virtual hosts (server blocks)
- Location routing (prefix + exact match)
- Load balancing (round-robin)
- Basic health checks (optional)
- Prometheus metrics (optional)

## Quickstart

### Install (dev)
```bash
pip install -e .
```

### Run with YAML config
```bash
pynx run -c examples/pynx.yml
```

### Example curl
```bash
curl -H "Host: example.com" http://localhost:8080/
```

## Config format
See `examples/pynx.yml`.

## Roadmap
- TLS termination + ACME
- HTTP/2 + HTTP/3
- Middleware pipeline (rate limit, auth, rewrite)
- TCP/UDP proxy
- Admin API + dashboard
