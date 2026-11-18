# Fenster „Agent-Nutzung“ links am Desktop: was der Agent gerade tut, bei Claude Code dazu die Limits wie in der
# Ressourcenanzeige von Windows 98. Die Klammer bleibt rechts sichtbar und lebt weiter (docs/architecture.md).
import time

from clippy import win98
from clippy.agent_hooks import usage
from clippy.win98 import DARK, FACE, LIGHT, NAVY

X, Y, W, H = 2, 2, 194, 206   # Lage am Desktop; rechts davon beginnt das Feld der Klammer
TITLE_H = 20
RED, BLUE = 0xC00000, 0x000080
STATE = {"working": "arbeitet grad", "waiting": "wartet auf di", "done": "is fertig"}


def _bar(g, y, label, pct, note):
    # Beschriftung, rechts die Zeit; darunter ein Fortschrittsbalken aus Blöcken wie bei Windows 98
    win98.text(g, label, 8, y, DARK, FACE)
    win98.text(g, note, W - 8, y, DARK, FACE, align="right")
    win98.bevel(g, 8, y + 17, W - 56, 14, raised=False)
    if pct is None:
        win98.text(g, "-", W - 10, y + 16, DARK, FACE, align="right")
        return
    color = RED if pct >= usage.WARN else BLUE
    for i in range(min(100, pct) * (W - 62) // 100 // 7):
        g.fillRect(11 + i * 7, y + 20, 5, 8, color)
    win98.text(g, "%d%%" % pct, W - 8, y + 16, DARK, FACE, align="right")


def _lines(g, y, lines):
    for i, line in enumerate(lines):
        win98.text(g, line, W // 2, y + i * 20, DARK, FACE, align="center")


class Monitor:
    def __init__(self, display, agents):
        self.d, self.agents = display, agents
        self.open = False
        self.canvas = None

    def hit(self, x, y):
        """Tipper bei offenem Fenster: "close" (das X), "inside" (ins Fenster, wird geschluckt) oder None."""
        if not self.open or not (X <= x < X + W and Y <= y < Y + H):
            return None
        return "close" if x >= X + W - 28 and y < Y + TITLE_H + 6 else "inside"

    def draw(self):
        if not self.open:
            return
        if self.canvas is None:
            self.canvas = self.d.newCanvas(W, H, 16, True)
        g = self.canvas
        win98.bevel(g, 0, 0, W, H)
        g.fillRect(2, 2, W - 4, TITLE_H - 2, NAVY)
        win98.text(g, "Agent-Nutzung", 7, 4, LIGHT, NAVY, bold=True)
        win98.bevel(g, W - 21, 4, 17, 15)
        for dx in (0, 1):
            g.drawLine(W - 16 + dx, 8, W - 10 + dx, 14, DARK)
            g.drawLine(W - 10 + dx, 8, W - 16 + dx, 14, DARK)
        name = self.agents.current()
        if name is None:
            _lines(g, 60, ("Noch kein Agent da.", "Einrichten: Startmenü >", "Mit PC verbinden"))
        else:
            self._agent(g, name)
        g.push(X, Y)

    def _agent(self, g, name):
        got, known = self.agents.usage.get(name), self.agents.known.get(name)
        u = got[0] if got else None
        win98.text(g, (name + " " + (u["model"] if u else ""))[:24], 8, TITLE_H + 6, DARK, FACE, bold=True)
        if got:
            minutes = time.ticks_diff(time.ticks_ms(), got[1]) // 60000
            win98.text(g, "grad eben" if minutes < 1 else "vor %d min" % minutes, W - 8, TITLE_H + 6, win98.SHADOW,
                       FACE, align="right")
        y = TITLE_H + 26
        if known:
            project = known["project"] if known["state"] == "working" and known["project"] else ""
            win98.text(g, (STATE[known["state"]] + (" an " + project if project else ""))[:28], 8, y, DARK, FACE)
            y += 20
        if u is None:  # Codex und Copilot geben ihre Limits nicht heraus; Claude erst mit der nächsten Antwort
            _lines(g, y + 20, ("Zahlen kommen mit der", "nächsten Antwort.") if name == "Claude"
                   else (name + " gibt seine Limits", "nicht heraus; die stehen", "nur am PC."))
            return
        for label, key in (("5 Stunden", "five_hour"), ("Woche", "seven_day")):
            _bar(g, y, label, usage.percent(u[key]), usage.reset_text(u[key]))
            y += 50
        if u["cost"] is not None:
            win98.text(g, ("Sitzung %.2f $" % u["cost"]).replace(".", ","), 8, y + 4, DARK, FACE)
        if u["added"] is not None:
            win98.text(g, "+%d -%d" % (u["added"], u["removed"] or 0), W - 8, y + 4, DARK, FACE, align="right")
