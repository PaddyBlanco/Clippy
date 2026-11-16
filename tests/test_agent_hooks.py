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

# Statuszeile von Claude: Nutzung auswerten, Clippy antwortet mit der Zeile für unten im Fenster
from clippy.agent_hooks import usage
now = time.time()
status = {"model": {"display_name": "Opus 5.5"}, "workspace": {"project_dir": "C:\\Projects\\Clippy"},
          "cost": {"total_cost_usd": 1.234, "total_lines_added": 120, "total_lines_removed": 30},
          "context_window": {"used_percentage": 31.4},
          "rate_limits": {"five_hour": {"used_percentage": 42.2, "resets_at": now + 3600},
                          "seven_day": {"used_percentage": 18, "resets_at": now + 86400 * 3}}}
u = AGENTS["claude"]().usage(status)
assert u["five_hour"] == (42, now + 3600) and u["seven_day"][0] == 18 and "context" not in u
assert u["project"] == "Clippy" and u["model"] == "Opus 5.5" and u["added"] == 120
assert usage.status_line(u) == "Clippy · 5h 42% · Woche 18%"
assert AGENTS["codex"]().usage(status) is None  # Codex gibt keine Zahlen heraus
no_plan = AGENTS["claude"]().usage({"cost": {"total_cost_usd": 0.5}})  # ohne Pro/Max: keine Limits
assert no_plan["five_hour"] is None and usage.status_line(no_plan) == "Clippy"
assert usage.percent((90, now - 10)) == 0  # Fenster vorbei: wieder bei null
high = dict(u, five_hour=(81, now + 3600))
assert usage.crossed(u, high) and not usage.crossed(high, high) and usage.crossed(high, dict(high, five_hour=(85, now + 9000)))

hooks.answer = lambda agent, kind, body: usage.status_line(AGENTS[agent]().usage(body))
got, text, _ = curl(["--data-binary", "@-", base + "/claude/status"], json.dumps(status).encode())
assert got is None and text.strip() == "Clippy · 5h 42% · Woche 18%", text

# Ausgabe von `claude -p /usage` (so am PC gesehen; „·“ kommt aus PowerShell oft als „?“ an)
from clippy.agent_hooks.claude import _when
usage_out = """You are currently using your subscription to power your Claude Code usage

Current session: 9% used · resets Nov 16, 11:49pm (Europe/Vienna)
Current week (all models): 8% used ? resets Nov 21, 9:59pm (Europe/Vienna)
Current week (Fable): 4% used · resets Nov 21, 9:59pm (Europe/Vienna)
"""
t = AGENTS["claude"]().usage_text(usage_out, today=(11, 16))
assert t["five_hour"] == (9, "23:49") and t["seven_day"] == (8, "21.11. 21:59") and t["cost"] is None
assert usage.reset_text(t["five_hour"]) == "bis 23:49" and usage.percent(t["seven_day"]) == 8
assert _when("12:05am", (1, 1)) == "00:05" and _when("Dec 3, 12pm", (1, 1)) == "3.12. 12:00" and _when("?", (1, 1)) == ""
assert AGENTS["claude"]().usage_text("Error: not logged in") is None
assert AGENTS["codex"]().usage_text(usage_out) is None
hooks.answer = lambda agent, kind, body: usage.status_line(AGENTS[agent]().usage_text(body, today=(11, 16)))
got, text, _ = curl(["--data-binary", "@-", base + "/claude/usage"], usage_out.encode())
assert got is None and text.strip() == "Clippy · 5h 9% · Woche 8%", text
hooks.answer = lambda agent, kind, body: 1 / 0  # Fehler beim Auswerten: Server bleibt heil
assert curl(["--data-binary", "@-", base + "/claude/usage"], b"x")[0] is None
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

# Arbeitswort: erscheint, sobald ein Agent arbeitet, in seiner Farbe; weg, wenn keiner mehr arbeitet
picks = iter(["Flibbertigibbeting", "Percolating"])  # erst zu lang (18 Buchstaben), dann passend
pet_agents.phrases.pick = lambda name: next(picks)
inbox.append(("claude", {"hook_event_name": "UserPromptSubmit", "cwd": "C:\\Projects\\Clippy"}))
tracker.poll(140000)
assert tracker.verb == "Percolating"
inbox.append(("claude", {"hook_event_name": "PostToolUse"}))  # ohne cwd: Projekt bleibt, Zeit läuft weiter
tracker.poll(152500)
assert tracker.console(152500) == {"agent": "Claude", "project": "Clippy", "verb": "Percolating",
                                   "color": 0xD97757, "seconds": 12}
inbox.append(("claude", {"hook_event_name": "Stop"}))
tracker.poll(153000)
assert tracker.verb is None and tracker.console(153000) is None

# Statuszeile über 80 %: einmal "usage_high", die Nutzung ist für das Fenster gemerkt
assert tracker._answer("claude", "status", dict(status, rate_limits={"five_hour": {"used_percentage": 85}})).startswith("Clippy")
assert tracker.poll(131000) == ["usage_high"] and tracker.poll(132000) == []
assert tracker.usage["Claude"][0]["five_hour"] == (85, None)

# /usage: Clippy bittet nur um Zahlen, wenn die letzten älter als 3 Minuten sind, und nie zweimal gleichzeitig
T0 = time.ticks_ms() + 10 ** 7  # gespielte Zeit, deutlich nach allem bisher
time.ticks_ms = lambda: T0
assert tracker._answer("claude", "usage", None) == "bitte"          # letzte Zahlen sind uralt
assert tracker._answer("claude", "usage", None) == "danke"          # schon gefragt, Antwort läuft noch
assert tracker._answer("claude", "usage", usage_out).startswith("Clippy · 5h 9% · Woche 8%")
merged = tracker.usage["Claude"][0]
assert merged["cost"] == 1.234 and merged["model"] == "Opus 5.5"    # Kosten und Modell bleiben von der Statuszeile
time.ticks_ms = lambda: T0 + pet_agents.USAGE_MS // 2 + 5000
assert tracker._answer("claude", "usage", None) == "danke"          # frisch genug
time.ticks_ms = lambda: T0 + pet_agents.USAGE_MS + 1000
assert tracker._answer("claude", "usage", None) == "bitte"
print("ok")
