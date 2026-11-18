# Wetterzeichen aus Kreisen und Strichen, in jeder Größe: draw(g, Art, Mitte x, Mitte y, Größe).
# Art wie in forecast.WORDS. Größe ist etwa die halbe Breite des Zeichens in Pixeln.
import math

SUN, RAY = 0xF0C000, 0xE09000
MOON = 0xE8E8B0
CLOUD, CLOUD_EDGE, GREY_CLOUD = 0xFFFFFF, 0x808080, 0xA0A0A8
DROP, SNOW, BOLT, FOG = 0x2060E0, 0xFFFFFF, 0xF0D000, 0x909090


def _sun(g, x, y, r):
    for i in range(8):
        a = math.radians(i * 45)
        g.drawLine(int(x + math.cos(a) * r * 1.3), int(y + math.sin(a) * r * 1.3),
                   int(x + math.cos(a) * r * 1.8), int(y + math.sin(a) * r * 1.8), RAY)
    g.fillCircle(x, y, r, SUN)


def _moon(g, x, y, r, back):
    g.fillCircle(x, y, r, MOON)
    g.fillCircle(x + r // 2, y - r // 3, r - 1, back)  # Sichel: ein Kreis in der Farbe dahinter frisst sie aus


def _cloud(g, x, y, s, c):
    # drei Bauschen und ein flacher Boden; x, y ist die Mitte
    r = s * 2 // 5
    for dx, dy, k in ((-s // 2, 0, r), (0, -r // 2, r + s // 8), (s // 2, 0, r)):
        g.fillCircle(x + dx, y + dy, k + 1, CLOUD_EDGE)
    g.fillRect(x - s // 2, y, s, r + 2, CLOUD_EDGE)
    for dx, dy, k in ((-s // 2, 0, r), (0, -r // 2, r + s // 8), (s // 2, 0, r)):
        g.fillCircle(x + dx, y + dy, k, c)
    g.fillRect(x - s // 2, y, s, r + 1, c)


def _below(g, x, y, s, what):
    # unter der Wolke: Tropfen, Flocken oder ein Blitz
    step = max(3, s // 2)
    for i in (-1, 0, 1):
        px = x + i * step
        if what == "drop":
            g.drawLine(px + 2, y, px, y + max(3, s // 3), DROP)
            g.drawLine(px + 3, y, px + 1, y + max(3, s // 3), DROP)
        elif what == "small":
            g.fillCircle(px, y + 2, 1, DROP)
        else:
            g.fillCircle(px, y + 2 + (i % 2) * 3, max(1, s // 8), SNOW)
            g.drawCircle(px, y + 2 + (i % 2) * 3, max(1, s // 8) + 1, CLOUD_EDGE)


def _bolt(g, x, y, s):
    h = max(6, s * 2 // 3)
    g.fillTriangle(x + 2, y, x - h // 3, y + h // 2 + 1, x + 1, y + h // 2 + 1, BOLT)
    g.fillTriangle(x - 1, y + h // 2 - 1, x + h // 3, y + h // 2 - 1, x - 2, y + h, BOLT)


def draw(g, kind, x, y, s, day=True, back=0xC0C0C0):
    """Zeichnet die Art kind mit Mitte (x, y) und halber Breite s. back: Farbe dahinter (für den Mond)."""
    if kind in ("sun", "partly"):
        r = s // 2 if kind == "sun" else s * 2 // 5
        cx, cy = (x, y) if kind == "sun" else (x - s // 3, y - s // 3)
        if day:
            _sun(g, cx, cy, r)
        else:
            _moon(g, cx, cy, r + 1, back)
        if kind == "partly":
            _cloud(g, x + s // 5, y + s // 4, s * 3 // 4, CLOUD)
        return
    if kind == "fog":
        for i in range(4):
            g.fillRect(x - s + (i % 2) * s // 4, y - s // 2 + i * s // 3, s * 7 // 4, max(2, s // 8), FOG)
        return
    dark = kind in ("rain", "storm", "snow")
    cy = y - s // 4
    _cloud(g, x, cy, s, GREY_CLOUD if dark else CLOUD)
    under = cy + s * 2 // 5 + 3
    if kind == "drizzle":
        _below(g, x, under, s, "small")
    elif kind == "rain":
        _below(g, x, under, s, "drop")
    elif kind == "snow":
        _below(g, x, under, s, "flake")
    elif kind == "storm":
        _bolt(g, x, under - 1, s)
