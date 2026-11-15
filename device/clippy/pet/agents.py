# Die Coding-Agents am PC: merkt sich je Agent den Zustand aus seinen Hook-Meldungen (docs/agent-hooks.md)
# und meldet der Klammer Ereignisse. Annehmen und Auswerten der Meldungen: clippy.agent_hooks.
import time

from clippy.agent_hooks import AGENTS
from clippy.agent_hooks.server import HookServer

REPEAT_MS = 30000          # wartet ein Agent noch auf dich, ruft sie nach dieser Zeit wieder ...
CALLS = 3                  # ... aber höchstens so oft insgesamt; danach bleibt nur das rote Kästchen
EXPIRE_MS = 30 * 60 * 1000  # so lange ohne Meldung, dann ist der Agent vergessen
EVENTS = {"working": "agent_working", "waiting": "agent_waiting", "done": "agent_done"}


class Agents:
    def __init__(self):
        self.server = HookServer()
        self.known = {}       # Name -> {"short", "state", "heard": letzte Meldung, "called": letzter Ruf, "seen"}
        self.last = "Agent"   # wer zuletzt etwas gemeldet hat; steht im Spruch für {agent}

    def poll(self, now):
        """Liefert eine Liste von Ereignissen: "agent_working", "agent_waiting", "agent_done"."""
        events = []
        got = self.server.poll(now)
        agent_class = AGENTS.get(got[0]) if got else None
        state = agent_class().state(got[1]) if agent_class else None
        if state == "gone":
            self.known.pop(agent_class.name, None)
        elif state:
            name = agent_class.name
            self.known[name] = {"short": agent_class.short, "state": state, "heard": now, "called": now,
                                "calls": 1, "seen": False}
            self.last = name
            events.append(EVENTS[state])
        for name, a in list(self.known.items()):
            if time.ticks_diff(now, a["heard"]) > EXPIRE_MS:
                del self.known[name]
            elif (a["state"] == "waiting" and not a["seen"] and a["calls"] < CALLS
                  and time.ticks_diff(now, a["called"]) > REPEAT_MS):
                a["called"], a["calls"], self.last = now, a["calls"] + 1, name
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
