"""Selbsttest am PC: python tests/test_agent_hook.py"""
import json
import os
import socket
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
os.environ["CLIPPY_HOST"] = "127.0.0.1"  # nicht ans echte Gerät schicken
import agent_hook
from agents import AGENTS


def state(agent, event, **extra):
    return AGENTS[agent]().state(dict(extra, hook_event_name=event))


# Gemeinsame Hook-Namen
for agent in AGENTS:
    assert state(agent, "UserPromptSubmit") == "working"
    assert state(agent, "PostToolUse") == "working"
    assert state(agent, "PermissionRequest") == "waiting"
    assert state(agent, "Stop") == "done"
    assert state(agent, "SessionEnd") == "gone"
    assert state(agent, "PreToolUse") is None
    assert AGENTS[agent]().state({}) is None
    assert len(AGENTS[agent].short) == 2

# Was je Agent anders ist
assert state("claude", "StopFailure") == "done"
assert state("claude", "Notification", notification_type="permission_prompt") == "waiting"
assert state("claude", "Notification", notification_type="idle_prompt") is None
assert state("codex", "Interrupt") == "done"
assert state("codex", "Notification", notification_type="permission_prompt") is None
assert state("copilot", "notification", notification_type="permission_prompt") == "waiting"
assert state("copilot", "notification", notification_type="agent_idle") is None

# Kürzel unterscheiden sich, sonst sind die Kästchen nicht auseinanderzuhalten
assert len({a.short for a in AGENTS.values()}) == len(AGENTS)

# Ganzer Weg: stdin -> UDP-Paket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as rx:
    rx.bind(("127.0.0.1", agent_hook.PORT))
    rx.settimeout(2)
    sent = agent_hook.main(["agent_hook.py", "Claude"], '{"hook_event_name": "Stop", "x": "Grüße"}'.encode())
    assert sent == {"agent": "Claude", "short": "Cl", "state": "done"}
    assert json.loads(rx.recv(512)) == sent
    assert agent_hook.main(["agent_hook.py", "unbekannt"], b"{}") is None
    assert agent_hook.main(["agent_hook.py", "codex"], b'{"hook_event_name": "PreToolUse"}') is None
print("ok")
