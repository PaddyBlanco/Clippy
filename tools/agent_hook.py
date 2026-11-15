"""Hook für Coding-Agents: python tools/agent_hook.py <agent>   (claude, codex, copilot; siehe docs/agent-hooks.md)

Liest die Hook-Meldung von stdin, fragt den Agent nach dem Zustand und schickt ihn per UDP an die Klammer.
Endet immer mit 0 und gibt nichts aus, damit der Agent nie gestört wird, auch wenn das Gerät aus ist.
"""
import json
import os
import socket
import sys
import tempfile
import time

from agents import AGENTS

PORT = 4711  # wie config.AGENT_PORT am Gerät
HOST = os.environ.get("CLIPPY_HOST", "clippy.local")
CACHE = os.path.join(tempfile.gettempdir(), "clippy-address.txt")
KEEP_S, FAIL_S = 600, 60  # gefundene Adresse 10 Minuten merken, einen Fehlschlag 1 Minute


def address():
    """Adresse des Geräts oder None. Gemerkt, weil die Namensauflösung bei ausgeschaltetem Gerät dauert."""
    try:
        with open(CACHE) as f:
            host, addr, at = f.read().split()
        if host == HOST and time.time() - float(at) < (FAIL_S if addr == "-" else KEEP_S):
            return None if addr == "-" else addr
    except (OSError, ValueError):
        pass
    try:
        addr = socket.getaddrinfo(HOST, PORT, socket.AF_INET, socket.SOCK_DGRAM)[0][4][0]
    except OSError:
        addr = "-"
    try:
        with open(CACHE, "w") as f:
            f.write("%s %s %f" % (HOST, addr, time.time()))
    except OSError:
        pass
    return None if addr == "-" else addr


def send(message):
    addr = address()
    if addr:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(json.dumps(message).encode(), (addr, PORT))


def main(argv, raw):
    """argv: Befehlszeile, raw: stdin als Bytes. Liefert die gesendete Nachricht oder None (für die Tests)."""
    agent_class = AGENTS.get(argv[1].lower()) if len(argv) > 1 else None
    if agent_class is None:
        return None
    payload = json.loads(raw.decode("utf-8", "replace") or "{}")
    agent = agent_class()
    state = agent.state(payload)
    if not state:
        return None
    message = agent.message(state)
    send(message)
    return message


if __name__ == "__main__":
    try:
        main(sys.argv, sys.stdin.buffer.read())
    except Exception:
        pass  # nie den Agent stören
    sys.exit(0)
