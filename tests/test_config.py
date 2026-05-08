import pytest
import tempfile
import yaml
from pynx.config import load_config, ConfigError


def _write_config(data: dict) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        return f.name


def test_load_valid_config():
    data = {
        "servers": [
            {
                "listen": "0.0.0.0:8080",
                "server_name": "example.com",
                "locations": [
                    {"path": "/", "type": "prefix", "upstream": "app"}
                ],
            }
        ],
        "upstreams": {
            "app": {"servers": [{"url": "http://localhost:5000"}]}
        },
    }
    path = _write_config(data)
    cfg = load_config(path)
    assert len(cfg.servers) == 1
    assert len(cfg.upstreams) == 1
    assert cfg.upstreams[0].name == "app"
    assert not cfg.metrics.enabled
    assert not cfg.healthcheck.enabled


def test_metrics_and_healthcheck_defaults():
    data = {
        "servers": [
            {
                "listen": "0.0.0.0:8080",
                "server_name": "example.com",
                "locations": [{"path": "/", "upstream": "app"}],
            }
        ],
        "upstreams": {"app": {"servers": [{"url": "http://localhost:5000"}]}},
        "metrics": {"enabled": True},
        "healthcheck": {"enabled": True},
    }
    path = _write_config(data)
    cfg = load_config(path)
    assert cfg.metrics.enabled
    assert cfg.metrics.path == "/metrics"
    assert cfg.healthcheck.enabled
    assert cfg.healthcheck.interval_seconds == 5
    assert cfg.healthcheck.path == "/health"


def test_missing_servers():
    data = {"upstreams": {"app": {"servers": [{"url": "http://localhost:5000"}]}}}
    path = _write_config(data)
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_upstreams():
    data = {
        "servers": [
            {
                "listen": "0.0.0.0:8080",
                "server_name": "example.com",
                "locations": [{"path": "/", "upstream": "app"}],
            }
        ],
    }
    path = _write_config(data)
    with pytest.raises(ConfigError):
        load_config(path)


def test_undefined_upstream_reference():
    data = {
        "servers": [
            {
                "listen": "0.0.0.0:8080",
                "server_name": "example.com",
                "locations": [{"path": "/", "upstream": "undefined_upstream"}],
            }
        ],
        "upstreams": {"app": {"servers": [{"url": "http://localhost:5000"}]}},
    }
    path = _write_config(data)
    with pytest.raises(ConfigError):
        load_config(path)
