#!/usr/bin/env python3
"""Start a GNS3 server and verify its local version API."""

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", default="/usr/local/bin/gns3server")
    parser.add_argument(
        "--config-sample",
        default="/usr/local/etc/gns3/gns3_server.conf.sample",
    )
    parser.add_argument("--expected-version", default="3.0.6")
    args = parser.parse_args()

    binary = Path(args.binary)
    sample = Path(args.config_sample)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        parser.error(f"server binary is missing or not executable: {binary}")
    if not sample.is_file():
        parser.error(f"configuration sample is missing: {sample}")

    port = free_port()
    with tempfile.TemporaryDirectory(prefix="gns3-smoke-") as temp:
        root = Path(temp)
        home = root / "home"
        data = home / "GNS3"
        for directory in ("images", "projects", "appliances", "symbols", "configs", "secrets"):
            (data / directory).mkdir(parents=True, exist_ok=True)

        config = root / "gns3_server.conf"
        text = sample.read_text(encoding="utf-8")
        text = text.replace("/var/db/gns3", str(home))
        text = text.replace("port = 3080", f"port = {port}")
        config.write_text(text, encoding="utf-8")

        log = root / "gns3_server.log"
        env = os.environ.copy()
        env["HOME"] = str(home)
        proc = subprocess.Popen(
            [str(binary), "--config", str(config), "--log", str(log)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        url = f"http://127.0.0.1:{port}/v3/version"
        payload = None
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    break
                try:
                    with urlopen(url, timeout=2) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                    break
                except (OSError, URLError, TimeoutError):
                    time.sleep(0.5)
            else:
                payload = None

            if proc.poll() is not None or not isinstance(payload, dict):
                details = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
                raise RuntimeError(f"server did not answer {url}\n{details[-4000:]}")
            version = payload.get("version")
            if version != args.expected_version:
                raise RuntimeError(f"unexpected version response: {payload!r}")
            print(f"GET {url} -> version {version}")
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
