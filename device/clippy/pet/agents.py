# Die Coding-Agents am PC: horcht auf ihre Meldungen (UDP, siehe docs/agent-hooks.md), merkt sich je Agent den
# Zustand und meldet der Klammer Ereignisse. Hier gibt es keinen Code je Agent; das Paket nennt Name und Kürzel.
import json
import socket
import time

from clippy import config, wifi

REPEAT_MS = 30000          # wartet ein Agent noch auf dich, ruft sie so oft wieder
EXPIRE_MS = 30 * 60 * 1000  # so lange ohne Meldung, dann ist der Agent vergessen
EVENTS = {"working": "agent_working", "waiting": "agent_waiting", "done": "agent_done"}


class Agents:
    def __init__(self):
        self.sock = None
        self.next_try = time.ticks_ms()
        self.known = {}       # Name -> {"short", "state", "heard": letzte Meldung, "called": letzter Ruf, "seen"}
        self.last = "Agent"   # wer zuletzt etwas gemeldet hat; steht im Spruch für {agent}

    def _listen(self, now):
        """Öffnet den Port, sobald das WLAN steht; bis dahin einmal je Sekunde nachsehen."""
        if self.sock is None and time.ticks_diff(now, self.next_try) > 0:
            self.next_try = time.ticks_add(now, 1000)
            if wifi.connected():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.bind(("0.0.0.0", config.AGENT_PORT))
                    s.setblocking(False)
                    self.sock = s
                except OSError:
                    pass
        return self.sock

    def poll(self, now):
        """Liefert eine Liste von Ereignissen: "agent_working", "agent_waiting", "agent_done"."""
        events = []
        sock = self._listen(now)
        while sock:
            try:
                data = sock.recv(256)
            except OSError:
                break  # nichts mehr da
            try:
                msg = json.loads(data)
                name, short, state = str(msg["agent"])[:12], str(msg.get("short", "?"))[:2], msg["state"]
            except (ValueError, KeyError, TypeError):
                continue
            if state == "gone":
                self.known.pop(name, None)
            elif state in EVENTS:
                self.known[name] = {"short": short, "state": state, "heard": now, "called": now, "seen": False}
                self.last = name
                events.append(EVENTS[state])
        for name, a in list(self.known.items()):
            if time.ticks_diff(now, a["heard"]) > EXPIRE_MS:
                del self.known[name]
            elif a["state"] == "waiting" and not a["seen"] and time.ticks_diff(now, a["called"]) > REPEAT_MS:
                a["called"], self.last = now, name
                events.append("agent_waiting")
        return events

    def acknowledge(self):
        """Du hast sie angetippt: Wer wartet, ruft nicht mehr; das Kästchen bleibt, bis der Agent weitermacht."""
        for a in self.known.values():
            a["seen"] = True

    def working(self):
        return any(a["state"] == "working" for a in self.known.values())

    def summary(self):
        """Für die Taskleiste: ((Kürzel, Zustand), ...), immer gleich sortiert."""
        return tuple(sorted((a["short"], a["state"]) for a in self.known.values()))
