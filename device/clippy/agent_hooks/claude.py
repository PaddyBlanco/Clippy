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


MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")


def _when(text, today):
    """„Nov 16, 11:49pm“ → „23:49“, wenn das heute ist (today: (Monat, Tag)), sonst „16.11. 23:49“; "" wenn unklar."""
    try:
        date, clock = (text.split(",", 1) + [""])[:2] if "," in text else ("", text)
        clock = clock.strip().lower()
        pm, clock = clock.endswith("pm"), clock[:-2].strip()
        hour, minute = (clock.split(":") + ["0"])[:2]
        hour = int(hour) % 12 + (12 if pm else 0)
        hhmm = "%02d:%02d" % (hour, int(minute))
        if not date:
            return hhmm
        month, day = MONTHS.index(date.split()[0][:3].lower()) + 1, int(date.split()[1])
        return hhmm if (month, day) == today else "%d.%d. %s" % (day, month, hhmm)
    except (ValueError, IndexError):
        return ""


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

    def usage_text(self, text, today=None):
        """Ausgabe von `claude -p /usage`: „Current session: 9% used · resets Nov 16, 11:49pm (Europe/Vienna)“
        ist das 5-Stunden-Fenster, „Current week (all models): …“ die Woche. Die Zeit bleibt Text (siehe _when)."""
        if today is None:
            import time
            today = time.localtime()[1:3]
        found = {}
        for line in text.splitlines():
            line = line.strip()
            for key, start in (("five_hour", "Current session:"), ("seven_day", "Current week (all models):")):
                if line.startswith(start) and "%" in line:
                    try:
                        pct = int(line[len(start):].split("%")[0].strip())
                    except ValueError:
                        continue
                    reset = line.split("resets", 1)[1].split("(")[0].strip() if "resets" in line else ""
                    found[key] = (pct, _when(reset, today))
        if not found:
            return None
        return {"five_hour": found.get("five_hour"), "seven_day": found.get("seven_day"), "context": None,
                "model": "", "cost": None, "added": None, "removed": None, "project": ""}
