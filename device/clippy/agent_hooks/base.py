# Schnittstelle für einen Coding-Agent: übersetzt seine Hook-Meldung in einen der vier Zustände, die Clippy kennt.
# Je Agent eine Unterklasse, die nur ändert, was bei ihm anders ist (docs/agent-hooks.md).

STATES = ("working", "waiting", "done", "gone")


class Agent:
    name = "Agent"      # Anzeige, steht in den Sprüchen für {agent}
    short = "Ag"        # Kürzel im Kästchen der Taskleiste, zwei Zeichen
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
