# Schnittstelle für einen Coding-Agent: übersetzt die Hook-Meldung des Agents in einen der vier Zustände,
# die das Gerät kennt. Je Agent eine Unterklasse, die nur ändert, was bei ihm anders ist.

STATES = ("working", "waiting", "done", "gone")


class Agent:
    name = "Agent"      # Anzeige am Gerät, steht in den Sprüchen
    short = "Ag"        # Kürzel im Kästchen der Taskleiste, zwei Zeichen
    # Hook-Namen je Zustand, klein geschrieben; die meisten Agents nennen ihre Hooks gleich
    hooks = {
        "working": {"userpromptsubmit", "posttooluse"},
        "waiting": {"permissionrequest"},
        "done": {"stop"},
        "gone": {"sessionend"},
    }
    # Benachrichtigungen (notification_type), die „wartet auf dich“ bedeuten
    waiting_notifications = set()

    def state(self, payload):
        """payload: das JSON-Objekt, das der Hook auf stdin bekommt. Liefert einen Zustand aus STATES oder None."""
        event = str(payload.get("hook_event_name", "")).lower()
        if event == "notification":
            return "waiting" if payload.get("notification_type") in self.waiting_notifications else None
        for state, names in self.hooks.items():
            if event in names:
                return state
        return None

    def message(self, state):
        """Was ans Gerät geht."""
        return {"agent": self.name, "short": self.short, "state": state}
