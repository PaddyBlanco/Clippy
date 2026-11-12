# Die Büroklammer zeichnen: eine Haltung (pose) hinein, ein Bild heraus.
# Koordinaten gelten im eigenen Feld (FIELD_W × FIELD_H); wo das Feld am Desktop liegt, sagen FIELD_X/Y.
import math

FIELD_W, FIELD_H = 122, 152
FIELD_X, FIELD_Y = 320 - FIELD_W, 212 - FIELD_H

OUTLINE = 0x4A4A55
WIRE = 0xA8A8B8
SHINE = 0xE4E4EE
WHITE = 0xFFFFFF
BLACK = 0x000000

# Draht als Mittellinien. Bögen: (Mitte x, Mitte y, Radius, Winkel von, bis), 0° zeigt nach rechts, im Uhrzeigersinn.
ARCS = ((49, 25, 20, 180, 360), (55, 109, 14, 0, 180), (56, 118, 27, 0, 180))
# Gerade Stücke: linkes Bein, mittleres Bein, inneres Ende
STICKS = ((29, 25, 29, 118), (69, 25, 69, 109), (41, 109, 41, 78))
# Das freie Ende rechts ist der Arm: Schulter unten, Ellbogen, Unterarm
SHOULDER, ELBOW, FOREARM = (83, 118), (83, 98), 24
EYES = ((29, 47), (71, 55))
EYE_RX, EYE_RY = 17, 14

REST = {"look": (0, 0), "lid": 0.0, "brow": 0, "bob": 0, "arm": 0, "weight": False}


def _stick(g, x0, y0, x1, y1, t, c):
    # Dicke Linie mit runden Enden
    dx, dy = x1 - x0, y1 - y0
    n = math.sqrt(dx * dx + dy * dy) or 1
    px, py = -dy * t / 2 / n, dx * t / 2 / n
    ax, ay, bx, by = int(x0 + px), int(y0 + py), int(x0 - px), int(y0 - py)
    cx, cy, ex, ey = int(x1 + px), int(y1 + py), int(x1 - px), int(y1 - py)
    g.fillTriangle(ax, ay, bx, by, cx, cy, c)
    g.fillTriangle(bx, by, cx, cy, ex, ey, c)
    g.fillCircle(int(x0), int(y0), t // 2, c)
    g.fillCircle(int(x1), int(y1), t // 2, c)


def _hand(arm):
    # Ende des Unterarms; arm in Grad: 0 = gerade nach oben, 110 = hängt nach außen
    a = math.radians(arm)
    return ELBOW[0] + FOREARM * math.sin(a), ELBOW[1] - FOREARM * math.cos(a)


def draw(g, pose):
    """Zeichnet die Klammer nach g. pose: siehe REST und docs/pet.md."""
    oy = pose["bob"]
    hx, hy = _hand(pose["arm"])
    sticks = STICKS + ((SHOULDER[0], SHOULDER[1], ELBOW[0], ELBOW[1]), (ELBOW[0], ELBOW[1], hx, hy))
    for t, c in ((7, OUTLINE), (5, WIRE), (1, SHINE)):
        shift = 0 if t > 1 else -1  # Glanzlicht sitzt leicht links oben
        for cx, cy, r, a0, a1 in ARCS:
            g.fillArc(cx + shift, cy + oy + shift, r - t // 2, r + t // 2, a0, a1, c)
        for x0, y0, x1, y1 in sticks:
            if t > 1:
                _stick(g, x0, y0 + oy, x1, y1 + oy, t, c)
            else:
                g.drawLine(int(x0) - 1, int(y0) + oy, int(x1) - 1, int(y1) + oy, c)

    if pose["weight"]:  # Hantel quer zum Unterarm
        a = math.radians(pose["arm"])
        ux, uy = math.cos(a) * 9, math.sin(a) * 9
        _stick(g, hx - ux, hy + oy - uy, hx + ux, hy + oy + uy, 3, 0x707070)
        for s in (-1, 1):
            g.fillCircle(int(hx + s * ux), int(hy + oy + s * uy), 6, 0x202020)
            g.fillCircle(int(hx + s * ux) - 2, int(hy + oy + s * uy) - 2, 1, 0x909090)

    lx, ly = pose["look"]
    ry = max(1, int(EYE_RY * (1 - pose["lid"])))
    for ex, ey in EYES:
        ey += oy
        g.fillEllipse(ex, ey, EYE_RX + 1, ry + 1, BLACK)
        g.fillEllipse(ex, ey, EYE_RX, ry, WHITE)
        if ry > 7:
            g.fillCircle(ex + lx, ey + ly, 8, BLACK)
            g.fillCircle(ex + lx - 3, ey + ly - 3, 2, WHITE)
    b = oy - pose["brow"]  # brow > 0 hebt die Brauen
    _stick(g, 14, 33 + b, 26, 24 + b, 4, BLACK)
    _stick(g, 26, 24 + b, 43, 23 + b, 4, BLACK)
    _stick(g, 62, 30 + b, 78, 31 + b, 4, BLACK)
    _stick(g, 78, 31 + b, 91, 42 + b, 4, BLACK)

