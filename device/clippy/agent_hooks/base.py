# Schnittstelle für einen Coding-Agent: übersetzt seine Hook-Meldung in einen der vier Zustände, die Clippy kennt.
# Je Agent eine Unterklasse, die nur ändert, was bei ihm anders ist (docs/agent-hooks.md).

STATES = ("working", "waiting", "done", "gone")


class Agent:
    name = "Agent"      # Anzeige, steht in den Sprüchen für {agent}
    short = "Ag"        # Kürzel im Kästchen der Taskleiste, zwei Zeichen
    color = 0x000080    # Farbe des Arbeitsworts über der Klammer
    # Hook-Namen je Zustand, klein geschrieben; die meisten Agents nennen ihre Hooks gleich
    hooks = {
        "working": ("userpromptsubmit", "posttooluse"),
        "waiting": ("permissionrequest",),
        "done": ("stop",),
        "gone": ("sessionend",),
    }
    # Benachrichtigungen (notification_type), die „wartet auf dich“ bedeuten
    waiting_notifications = ()

    def state(self, payload):
        """payload: die Hook-Meldung als dict. Liefert einen Zustand aus STATES oder None."""
        event = str(payload.get("hook_event_name", "")).lower()
        if event == "notification":
            return "waiting" if payload.get("notification_type") in self.waiting_notifications else None
        for state, names in self.hooks.items():
            if event in names:
                return state
        return None

    def project(self, payload):
        """Name des Projekts, an dem der Agent arbeitet: letzter Teil des Arbeitsordners, oder ""."""
        return str(payload.get("cwd") or "").replace("\\", "/").rstrip("/").split("/")[-1]

    def usage(self, payload):
        """payload: das JSON der Statuszeile. Liefert die Nutzung als dict (siehe Claude.usage) oder None,
        wenn der Agent keine Zahlen herausgibt."""
        return None

    def usage_text(self, text):
        """text: was der Agent auf seinen Nutzungs-Befehl ausgibt (bei Claude `claude -p /usage`). Nutzung als dict
        wie bei usage(), fehlende Werte None; oder None, wenn nichts darin steht."""
        return None
