# Die Coding-Agents am PC: merkt sich je Agent den Zustand aus seinen Hook-Meldungen und die Nutzung aus seiner
# Statuszeile (docs/agent-hooks.md) und meldet der Klammer Ereignisse. Annehmen und Auswerten: clippy.agent_hooks.
import time

from clippy.agent_hooks import AGENTS, usage
from clippy.agent_hooks.server import HookServer
from clippy.pet import phrases

REPEAT_MS = 30000          # wartet ein Agent noch auf dich, ruft sie nach dieser Zeit wieder ...
CALLS = 3                  # ... aber höchstens so oft insgesamt; danach bleibt nur das rote Kästchen
EXPIRE_MS = 30 * 60 * 1000  # so lange ohne Meldung, dann ist der Agent vergessen
VERB_MS = 20000            # bei langer Arbeit so oft ein neues Arbeitswort
VERB_MAX = 13              # längere Wörter passen nicht in die Konsole über der Klammer (173 von 187 passen)
EVENTS = {"working": "agent_working", "waiting": "agent_waiting", "done": "agent_done"}
AGENTS_BY_NAME = {c.name: c for c in AGENTS.values()}


class Agents:
    def __init__(self):
        self.server = HookServer(self._status)
        self.known = {}       # Name -> {"short", "state", "heard": letzte Meldung, "called": letzter Ruf, "seen"}
        self.usage = {}       # Name -> (Nutzung als dict, wann gemeldet in ms)
        self.pending = []     # Ereignisse aus der Statuszeile, gehen mit dem nächsten poll hinaus
        self.last = "Agent"   # wer zuletzt etwas gemeldet hat; steht im Spruch für {agent}
        self.verb, self.verb_at = None, 0  # Arbeitswort in der Konsole über der Klammer, None = keiner arbeitet

    def _status(self, path, payload):
        """Statuszeile eines Agents: Nutzung merken, Warnung vormerken, Zeile zurückgeben."""
        agent_class = AGENTS.get(path)
        data = agent_class().usage(payload) if agent_class else None
        if not data:
            return ""
        old = self.usage.get(agent_class.name)
        self.usage[agent_class.name] = (data, time.ticks_ms())
        if usage.crossed(old[0] if old else None, data):
            self.last = agent_class.name
            self.pending.append("usage_high")
        return usage.status_line(data)

    def poll(self, now):
        """Liefert eine Liste von Ereignissen: "agent_working", "agent_waiting", "agent_done", "usage_high"."""
        got = self.server.poll(now)
        events, self.pending = self.pending, []
        agent_class = AGENTS.get(got[0]) if got else None
        state = agent_class().state(got[1]) if agent_class else None
        if state == "gone":
            self.known.pop(agent_class.name, None)
        elif state:
            name = agent_class.name
            old = self.known.get(name, {})
            began = state == "working" and old.get("state") != "working"
            self.known[name] = {"short": agent_class.short, "state": state, "heard": now, "called": now,
                                "calls": 1, "seen": False,
                                "project": agent_class().project(got[1]) or old.get("project", ""),
                                "since": now if began else old.get("since", now)}  # arbeitet seit
            self.last = name
            events.append(EVENTS[state])
            if began:  # beginnt zu arbeiten: gleich ein neues Wort
                self.verb_at = time.ticks_add(now, -VERB_MS)
        for name, a in list(self.known.items()):
            if time.ticks_diff(now, a["heard"]) > EXPIRE_MS:
                del self.known[name]
            elif (a["state"] == "waiting" and not a["seen"] and a["calls"] < CALLS
                  and time.ticks_diff(now, a["called"]) > REPEAT_MS):
                a["called"], a["calls"], self.last = now, a["calls"] + 1, name
                events.append("agent_waiting")
        if not self.working():
            self.verb = None
        elif self.verb is None or time.ticks_diff(now, self.verb_at) >= VERB_MS:
            self.verb_at = now
            for _ in range(5):  # nur Wörter, die über der Klammer Platz haben
                self.verb = phrases.pick("agent_verbs")
                if self.verb is None or len(self.verb) <= VERB_MAX:
                    break
        return events

    def acknowledge(self):
        """Du hast sie angetippt: Wer wartet, ruft nicht mehr; das Kästchen bleibt, bis der Agent weitermacht."""
        for a in self.known.values():
            a["seen"] = True

    def working(self):
        return any(a["state"] == "working" for a in self.known.values())

    def console(self, now):
        """Für die Konsole über der Klammer: {"agent", "project", "verb", "color", "seconds"}, oder None,
        wenn keiner arbeitet. Arbeiten mehrere, der, der sich zuletzt gemeldet hat."""
        busy = [(a["heard"], n) for n, a in self.known.items() if a["state"] == "working"]
        if not self.verb or not busy:
            return None
        name = max(busy)[1]
        a = self.known[name]
        return {"agent": name, "project": a["project"], "verb": self.verb, "color": AGENTS_BY_NAME[name].color,
                "seconds": max(0, time.ticks_diff(now, a["since"]) // 1000)}

    def summary(self):
        """Für die Taskleiste: ((Kürzel, Zustand), ...), immer gleich sortiert."""
        return tuple(sorted((a["short"], a["state"]) for a in self.known.values()))
