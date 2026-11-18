# Zeichen der Coding-Agents für das Desktop-Symbol „Agent“: Kacheln 32×32 aus Grundformen, ohne Bilddateien.
# Claude: der Stern mit zwölf Strahlen auf Orange. Codex: der Knoten von OpenAI auf Grün. Sonst das Prozentzeichen.
import math

from clippy import win98
from clippy.win98 import DARK, LIGHT

TILE = {"Claude": 0xD97757, "Codex": 0x10A37F}  # Farbe der Kachel je Agent (wie `color` in agent_hooks/)
PLAIN = 0x208080                                 # Kachel, solange kein Agent bekannt ist
CREAM = 0xF4EDE4                                 # der Stern von Claude


def frame(g, x, y, color):
    # Kachel mit heller Kante oben und links; auch für die Symbole mit Buchstaben (shell.icon)
    g.fillRect(x, y, 32, 32, color)
    g.drawRect(x, y, 32, 32, DARK)
    g.drawLine(x + 1, y + 1, x + 30, y + 1, LIGHT)
    g.drawLine(x + 1, y + 1, x + 1, y + 30, LIGHT)


def _claude(g, cx, cy):
    # zwölf Strahlen, abwechselnd lang und kurz, jeder ein schmaler Keil aus der Mitte
    for i in range(12):
        a = math.radians(i * 30 + 15)
        r = 12 if i % 2 == 0 else 9
        dx, dy = math.cos(a), math.sin(a)
        bx, by = cx + dx * 3, cy + dy * 3        # Basis des Keils nahe der Mitte, 3 Pixel breit
        px, py = -dy * 1.6, dx * 1.6
        g.fillTriangle(int(round(cx + dx * r)), int(round(cy + dy * r)), int(round(bx + px)), int(round(by + py)),
                       int(round(bx - px)), int(round(by - py)), CREAM)
    g.fillCircle(cx, cy, 3, CREAM)


def _codex(g, cx, cy):
    # das Sechseck des Knotens, dicke Kanten, von jeder Ecke eine Speiche ein Stück nach innen
    corners = [(cx + math.cos(math.radians(i * 60 + 30)) * 11, cy + math.sin(math.radians(i * 60 + 30)) * 11)
               for i in range(6)]
    for i, (x0, y0) in enumerate(corners):
        x1, y1 = corners[(i + 1) % 6]
        edge, spoke = (x0, y0, x1, y1), (x0, y0, cx + (x0 - cx) * 0.45, cy + (y0 - cy) * 0.45)
        for ox, oy in ((0, 0), (1, 0), (0, 1)):  # drei Linien übereinander ergeben die Dicke
            for line in (edge, spoke):
                ax, ay, bx, by = [int(round(v)) for v in line]
                g.drawLine(ax + ox, ay + oy, bx + ox, by + oy, LIGHT)


def tile(g, x, y, agent):
    """Kachel 32×32 bei (x, y) für den Agent (Name wie in agent_hooks/) oder None."""
    frame(g, x, y, TILE.get(agent, PLAIN))
    if agent == "Claude":
        _claude(g, x + 16, y + 16)
    elif agent == "Codex":
        _codex(g, x + 16, y + 16)
    else:
        win98.text(g, "%", x + 16, y + 9, LIGHT, PLAIN, bold=True, align="center")
