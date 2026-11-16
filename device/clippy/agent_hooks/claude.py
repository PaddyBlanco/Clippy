# Claude Code: Hooks siehe https://code.claude.com/docs/en/hooks.md, Statuszeile .../statusline.md
from clippy.agent_hooks.base import Agent

_hooks = dict(Agent.hooks)
_hooks["done"] = ("stop", "stopfailure")  # StopFailure: Antwort wegen eines API-Fehlers beendet


def _window(payload, key):
    """(Prozent, zurückgesetzt um in Unix-Sekunden) eines Limit-Fensters, oder None (kein Pro/Max-Abo)."""
    w = (payload.get("rate_limits") or {}).get(key) or {}
    if w.get("used_percentage") is None:
        return None
    return int(round(w["used_percentage"])), w.get("resets_at")


class Claude(Agent):
    name = "Claude"
    short = "Cl"
    color = 0xD97757  # Claude-Orange
    hooks = _hooks
    waiting_notifications = ("permission_prompt", "agent_needs_input")

    def usage(self, payload):
        cost = payload.get("cost") or {}
        context = (payload.get("context_window") or {}).get("used_percentage")
        project = (payload.get("workspace") or {}).get("project_dir") or payload.get("cwd") or ""
        return {
            "five_hour": _window(payload, "five_hour"),
            "seven_day": _window(payload, "seven_day"),
            "context": None if context is None else int(round(context)),
            "model": (payload.get("model") or {}).get("display_name") or "",
            "cost": cost.get("total_cost_usd"),
            "added": cost.get("total_lines_added"),
            "removed": cost.get("total_lines_removed"),
            "project": project.replace("\\", "/").rstrip("/").split("/")[-1],
        }
