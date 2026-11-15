"""Selbsttest am PC: python tests/test_agent_hooks.py
Auswertung je Agent und der Webserver am Gerät, angesprochen mit echtem curl wie in manual/verbinden.txt."""
import json
import os
import subprocess
import sys
import threading
import time
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "device"))
sys.modules["M5"] = types.ModuleType("M5")
time.ticks_ms = lambda: int(time.monotonic() * 1000)  # MicroPython-Zeitfunktionen
time.ticks_add = lambda a, b: a + b
time.ticks_diff = lambda a, b: a - b
from clippy import wifi
from clippy.agent_hooks import AGENTS, server


def state(agent, event, **extra):
    return AGENTS[agent]().state(dict(extra, hook_event_name=event))


# Gemeinsame Hook-Namen, unabhängig von der Schreibweise
for agent in AGENTS:
    assert state(agent, "UserPromptSubmit") == "working"
    assert state(agent, "PostToolUse") == "working"
    assert state(agent, "PermissionRequest") == "waiting"
    assert state(agent, "Stop") == "done"
    assert state(agent, "SessionEnd") == "gone"
    assert state(agent, "PreToolUse") is None
    assert AGENTS[agent]().state({}) is None
    assert len(AGENTS[agent].short) == 2
assert len({a.short for a in AGENTS.values()}) == len(AGENTS)  # Kästchen auseinanderzuhalten

# Was je Agent anders ist
assert state("claude", "StopFailure") == "done"
assert state("claude", "Notification", notification_type="permission_prompt") == "waiting"
assert state("claude", "Notification", notification_type="idle_prompt") is None
assert state("codex", "Interrupt") == "done"
assert state("copilot", "notification", notification_type="permission_prompt") == "waiting"

# Große oder kaputte Meldungen: nur die nötigen Felder
big = json.dumps({"hook_event_name": "PostToolUse", "tool_input": {"content": "x" * 200000}}).encode()
assert server.parse(big) == {"hook_event_name": "PostToolUse"}
assert server.parse(b'{"hook_event_name": "Notification", "notification_type": "permission_prompt", "x": ') == {
    "hook_event_name": "Notification", "notification_type": "permission_prompt"}

# Webserver mit echtem curl, so wie die Hooks es tun
wifi.connected = lambda: True
server.HOST = "127.0.0.1"
hooks = server.HookServer()
base = "http://127.0.0.1:%d" % server.config.AGENT_PORT


def curl(args, stdin=b""):
    """Startet curl im Hintergrund, bedient derweil den Server; liefert (Ergebnis, Ausgabe, Sekunden)."""
    out, start = [], time.monotonic()
    t = threading.Thread(target=lambda: out.append(subprocess.run(["curl.exe", "-s", "-m", "3"] + args, input=stdin,
                                                                 capture_output=True).stdout.decode()))
    t.start()
    got = None
    while t.is_alive():
        got = hooks.poll(time.ticks_ms() + 2000) or got
    t.join()
    return got, out[0], time.monotonic() - start


got, text, _ = curl([base + "/"])
assert got is None and "Clippy" in text
got, text, _ = curl([base + "/claude/probe"])
assert got == ("claude", {"hook_event_name": "Stop"}) and "freut" in text
got, _, _ = curl(["--data-binary", "@-", base + "/codex"], b'{"hook_event_name": "PermissionRequest"}\n')
assert got == ("codex", {"hook_event_name": "PermissionRequest"})
got, _, seconds = curl(["--data-binary", "@-", base + "/claude"], big)  # curl fragt hier „100-continue“
assert got == ("claude", {"hook_event_name": "PostToolUse"}) and seconds < 0.9, seconds
hooks.sock.close()

# Wartet ein Agent, ruft die Klammer höchstens dreimal (sofort, nach 30 und nach 60 s)
from clippy.pet import agents as pet_agents
tracker = pet_agents.Agents()
inbox = [("codex", {"hook_event_name": "PermissionRequest"})]
tracker.server = types.SimpleNamespace(poll=lambda now: inbox.pop(0) if inbox else None)
calls = sum(tracker.poll(t * 1000).count("agent_waiting") for t in range(0, 120, 2))
assert calls == pet_agents.CALLS == 3, calls
assert tracker.summary() == (("Cx", "waiting"),)  # das rote Kästchen bleibt
inbox.append(("codex", {"hook_event_name": "SessionEnd"}))
tracker.poll(130000)
assert tracker.summary() == ()
print("ok")
