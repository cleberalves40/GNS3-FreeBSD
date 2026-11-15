#!/usr/bin/env python3
"""Teste de fumaca do uBridge instalado (protocolo do hypervisor).

Uso:
    python3 scripts/smoke-ubridge.py [/usr/local/bin/ubridge] [--tap]

Sem --tap roda apenas o relay UDP (nao precisa de root). Com --tap, cria um
NIO TAP e exige privilegios (o binario do port e setuid root, entao basta
executa-lo como usuario comum).
"""
import argparse
import socket
import subprocess
import sys
import time


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Hypervisor:
    def __init__(self, binary, tap=False):
        self.port = free_port()
        self.proc = subprocess.Popen(
            [binary, "-H", f"127.0.0.1:{self.port}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.8)
        self.sock = socket.create_connection(("127.0.0.1", self.port), timeout=5)
        self.sock.settimeout(10)
        self.buf = b""

    def send(self, text):
        self.sock.sendall((text + "\n").encode())
        lines = []
        while True:
            while b"\n" not in self.buf:
                chunk = self.sock.recv(4096)
                if not chunk:
                    return " | ".join(lines)
                self.buf += chunk
            line, self.buf = self.buf.split(b"\n", 1)
            value = line.decode(errors="replace").strip()
            lines.append(value)
            if value.startswith("100"):
                return " | ".join(lines)

    def close(self):
        self.sock.close()
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", nargs="?", default="/usr/local/bin/ubridge")
    parser.add_argument("--tap", action="store_true", help="testa tambem NIO TAP")
    args = parser.parse_args()

    commands = [
        "bridge create br0",
        "bridge add_nio_udp br0 20000 127.0.0.1 20001",
        "bridge add_nio_udp br0 20002 127.0.0.1 20003",
    ]
    if args.tap:
        commands.append("bridge add_nio_tap br0 tap0")
    commands += [
        "bridge start br0",
        "bridge stop br0",
        "bridge delete br0",
    ]

    hv = Hypervisor(args.binary, tap=args.tap)
    failures = 0
    try:
        for cmd in commands:
            reply = hv.send(cmd)
            ok = any(line.startswith("100") for line in reply.split(" | "))
            failures += 0 if ok else 1
            print(f"[{'OK  ' if ok else 'FAIL'}] {cmd} -> {reply[:100]}")
    finally:
        hv.close()

    print(f"\n{len(commands) - failures}/{len(commands)} comandos OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
