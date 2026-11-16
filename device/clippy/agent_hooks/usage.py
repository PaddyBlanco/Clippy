# Nutzung eines Agents in Worten: Statuszeile für Claude Code, Zurücksetz-Zeiten, Warnschwelle.
import time

WARN = 80  # ab so viel Prozent beim 5-Stunden-Limit warnt die Klammer, und die Balken werden rot
DAYS = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")


def clock_set():
    return time.localtime()[0] >= 2024  # vorher hat Clippy die Uhr noch nicht übers WLAN gestellt


def percent(window):
    """Prozent eines Fensters; ist die Zurücksetz-Zeit schon vorbei, wieder 0. None = nicht gemeldet."""
    if not window:
        return None
    pct, resets = window
    if isinstance(resets, str):  # aus `/usage`: Zeit nur als Text, dort nicht nachrechenbar
        return pct
    return 0 if resets and clock_set() and time.time() >= resets else pct


def reset_text(window):
    """„bis 14:30“, an einem anderen Tag „bis Mo 09:00“; leer ohne gestellte Uhr."""
    if window and isinstance(window[1], str):  # aus `/usage`: schon fertig als Text
        return "bis " + window[1] if window[1] else ""
    if not window or not window[1] or not clock_set():
        return ""
    t, now = time.localtime(window[1]), time.localtime()
    day = "" if t[:3] == now[:3] else DAYS[t[6]] + " "
    return "bis %s%02d:%02d" % (day, t[3], t[4])


def status_line(u):
    """Die Zeile, die Claude Code unten anzeigt."""
    parts = ["Clippy"]
    for label, key in (("5h", "five_hour"), ("Woche", "seven_day")):
        if percent(u[key]) is not None:
            parts.append("%s %d%%" % (label, percent(u[key])))
    if u["context"] is not None:
        parts.append("Kontext %d%%" % u["context"])
    return " · ".join(parts)


def crossed(old, new):
    """Hat das 5-Stunden-Limit gerade die Warnschwelle erreicht? Einmal je Zeitfenster."""
    if not new["five_hour"] or new["five_hour"][0] < WARN:
        return False
    if not old or not old["five_hour"]:
        return True
    return old["five_hour"][0] < WARN or old["five_hour"][1] != new["five_hour"][1]
