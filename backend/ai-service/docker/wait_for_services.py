from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse


def wait_for(host: str, port: int, service_name: str, timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"{service_name} is reachable at {host}:{port}")
                return
        except OSError:
            time.sleep(2)
    raise RuntimeError(f"Timed out waiting for {service_name} at {host}:{port}")


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def wait_for_any(hosts: list[str], port: int, service_name: str, timeout_seconds: int = 90) -> str:
    last_error: RuntimeError | None = None
    for host in _unique(hosts):
        try:
            wait_for(host, port, service_name, timeout_seconds=timeout_seconds)
            return host
        except RuntimeError as exc:
            last_error = exc
            print(f"{service_name} not reachable at {host}:{port}; trying next host candidate")
    host_list = ", ".join(_unique(hosts))
    if last_error is not None:
        raise RuntimeError(f"Timed out waiting for {service_name}. Tried hosts: {host_list}") from last_error
    raise RuntimeError(f"No host candidates configured for {service_name}")


def main() -> int:
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://host.docker.internal:27017")
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_fallback_hosts = os.getenv("QDRANT_FALLBACK_HOSTS", "host.docker.internal,127.0.0.1")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

    parsed = urlparse(mongo_uri)
    mongo_host = parsed.hostname or "localhost"
    mongo_port = parsed.port or 27017

    wait_for(mongo_host, mongo_port, "MongoDB")
    qdrant_hosts = [qdrant_host, *qdrant_fallback_hosts.split(",")]
    selected_qdrant_host = wait_for_any(qdrant_hosts, qdrant_port, "Qdrant")
    os.environ["QDRANT_HOST"] = selected_qdrant_host
    print(f"Using Qdrant host: {selected_qdrant_host}")

    process = subprocess.run(
        [
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            os.getenv("APP_PORT", "7000"),
        ],
        check=False,
    )
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
