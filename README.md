# pynx

[![PyPI - Version](https://img.shields.io/pypi/v/pynx-proxy)](https://pypi.org/project/pynx-proxy/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pynx-proxy)](https://pypi.org/project/pynx-proxy/)
[![PyPI - License](https://img.shields.io/pypi/l/pynx-proxy)](https://github.com/Kubenew/pynx/blob/main/LICENSE)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/Kubenew/pynx)](https://github.com/Kubenew/pynx)
[![Downloads](https://pepy.tech/badge/pynx-proxy)](https://pepy.tech/project/pynx-proxy)

**pynx** is a minimal Nginx-like async reverse proxy / edge router written in Python.

## Features (MVP)
- Reverse proxy (HTTP)
- Virtual hosts (server blocks)
- Location routing (prefix + exact match)
- Load balancing (round-robin)
- Basic health checks (optional)
- Prometheus metrics (optional)

## Quickstart

### Install from PyPI
```bash
pip install pynx-proxy
```

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
