# Die Büroklammer zeichnen: eine Haltung (pose) hinein, ein Bild heraus.
# Koordinaten gelten im eigenen Feld (FIELD_W × FIELD_H); wo das Feld am Desktop liegt, sagen FIELD_X/Y.
import math
import random

HEADROOM = 24  # Luft über dem Kopf, damit sie springen kann
FIELD_W, FIELD_H = 122, 152 + HEADROOM
FIELD_X, FIELD_Y = 320 - FIELD_W, 212 - FIELD_H
# Zum Umfallen braucht sie Platz nach links: breitere Bühne, nur solange sie kippt oder liegt
STAGE_W = 252
STAGE_X = 320 - STAGE_W

SILVER = (0x4A4A55, 0xA8A8B8, 0xE4E4EE)  # Draht: Kontur, Fläche, Glanzlicht
ANGRY = (0x6A1818, 0xD85050, 0xFFB8B8)   # dasselbe, wenn sie rot anläuft
WHITE = 0xFFFFFF
BLACK = 0x000000
YELLOW = 0xFFE000

# Draht als Mittellinien. Bögen: (Mitte x, Mitte y, Radius, Winkel von, bis), 0° zeigt nach rechts, im Uhrzeigersinn.
ARCS = ((49, 25, 20, 180, 360), (55, 109, 14, 0, 180), (56, 118, 27, 0, 180))
# Gerade Stücke: linkes Bein, mittleres Bein, inneres Ende
STICKS = ((29, 25, 29, 118), (69, 25, 69, 109), (41, 109, 41, 78))
# Das freie Ende rechts ist der Arm: Schulter unten, Ellbogen, Unterarm
SHOULDER, ELBOW, FOREARM = (83, 118), (83, 98), 24
EYES = ((29, 47), (71, 55))
EYE_RX, EYE_RY = 17, 14
BROWS = ((14, 33, 26, 24), (26, 24, 43, 23), (62, 30, 78, 31), (78, 31, 91, 42))
FOOT = (14, 147)  # um diesen Punkt links unten kippt sie

REST = {"look": (0, 0), "lid": 0.0, "brow": 0, "bob": 0, "stretch": 0, "lean": 0, "arm": 0, "red": False,
        "weight": False, "stick": False, "drum": False, "spark": False, "zzz": 0, "snot": 0}


def _stick(g, x0, y0, x1, y1, t, c):
    # Dicke Linie mit runden Enden
    dx, dy = x1 - x0, y1 - y0
    n = math.sqrt(dx * dx + dy * dy) or 1
    px, py = -dy * t / 2 / n, dx * t / 2 / n
    g.fillTriangle(int(x0 + px), int(y0 + py), int(x0 - px), int(y0 - py), int(x1 + px), int(y1 + py), c)
    g.fillTriangle(int(x0 - px), int(y0 - py), int(x1 + px), int(y1 + py), int(x1 - px), int(y1 - py), c)
    g.fillCircle(int(x0), int(y0), t // 2, c)
    g.fillCircle(int(x1), int(y1), t // 2, c)


def _arc(g, x, y, r0, r1, a0, a1, c):
    # Bogen mit beliebigen Winkeln; über 0° hinweg in zwei Stücken
    a0, a1 = a0 % 360, a1 % 360 or 360
    if a0 < a1:
        g.fillArc(x, y, r0, r1, a0, a1, c)
    else:
        g.fillArc(x, y, r0, r1, a0, 360, c)
        g.fillArc(x, y, r0, r1, 0, a1, c)


def draw(g, pose, ox=0):
    """Zeichnet die Klammer nach g, um ox nach rechts versetzt. pose: siehe REST und docs/pet.md."""
    lean, bob = pose["lean"], pose["bob"]
    ca, sa = math.cos(math.radians(-lean)), math.sin(math.radians(-lean))

    # Beim Kippen rollt sie auf dem unteren Bogen ab: so weit absenken, dass er am Boden bleibt statt zu schweben
    ux, uy = ARCS[2][0] - FOOT[0], ARCS[2][1] - FOOT[1]
    drop = max(0, -int(ux * sa + uy * ca) - ARCS[2][2] - 5)

    stretch = pose["stretch"]

    def at(x, y):  # Punkt der Figur -> Punkt im Bild: strecken, wippen, um den Fuß kippen, versetzen
        if y < 70:  # obere Hälfte wandert beim Strecken nach oben, die Beine werden länger
            y -= stretch
        dx, dy = x - FOOT[0], y + bob - FOOT[1]
        return int(ox + FOOT[0] + dx * ca - dy * sa), int(HEADROOM + FOOT[1] + drop + dx * sa + dy * ca)

    a = math.radians(pose["arm"])  # Unterarm: 0 = gerade nach oben, 105 = hängt nach außen
    hand = (ELBOW[0] + FOREARM * math.sin(a), ELBOW[1] - FOREARM * math.cos(a))
    sticks = STICKS + (SHOULDER + ELBOW, ELBOW + hand)
    for t, c in zip((7, 5, 1), ANGRY if pose["red"] else SILVER):
        shift = 0 if t > 1 else -1  # Glanzlicht sitzt leicht links oben
        for cx, cy, r, a0, a1 in ARCS:
            x, y = at(cx + shift, cy + shift)
            _arc(g, x, y, r - t // 2, r + t // 2, a0 - lean, a1 - lean, c)
        for x0, y0, x1, y1 in sticks:
            p, q = at(x0 + shift, y0), at(x1 + shift, y1)
            if t > 1:
                _stick(g, p[0], p[1], q[0], q[1], t, c)
            else:
                g.drawLine(p[0], p[1], q[0], q[1], c)

    hx, hy = at(hand[0], hand[1])
    if pose["weight"]:  # Hantel quer zum Unterarm
        ux, uy = math.cos(a) * 9, math.sin(a) * 9
        _stick(g, hx - ux, hy - uy, hx + ux, hy + uy, 3, 0x707070)
        for s in (-1, 1):
            g.fillCircle(int(hx + s * ux), int(hy + s * uy), 6, 0x202020)
            g.fillCircle(int(hx + s * ux) - 2, int(hy + s * uy) - 2, 1, 0x909090)
    if pose["drum"]:  # kleine Trommel rechts unten
        x, y = at(109, 110)
        g.fillRect(x - 12, y, 25, 14, 0xB03030)
        g.fillEllipse(x, y + 14, 12, 4, 0xB03030)
        g.fillEllipse(x, y, 12, 4, 0x303030)
        g.fillEllipse(x, y, 11, 3, 0xF0F0E0)
    if pose["stick"]:  # Schlägel, im Handgelenk nach unten abgewinkelt
        w = math.radians(pose["arm"] + 70)
        _stick(g, hx, hy, hx + 16 * math.sin(w), hy - 16 * math.cos(w), 2, 0x8B5A2B)

    lx, ly = pose["look"]
    gap = max(1, int(EYE_RY * (1 - pose["lid"])))  # wie weit das Auge offen ist
    rx, ry = (gap, EYE_RX) if lean > 45 else (EYE_RX, gap)  # liegt sie, liegen auch die Augen quer
    for ex, ey in EYES:
        x, y = at(ex, ey)
        g.fillEllipse(x, y, rx + 1, ry + 1, BLACK)
        g.fillEllipse(x, y, rx, ry, WHITE)
        if gap > 7:
            g.fillCircle(x + lx, y + ly, 8, BLACK)
            g.fillCircle(x + lx - 3, y + ly - 3, 2, WHITE)
    for x0, y0, x1, y1 in BROWS:  # brow > 0 hebt die Brauen
        p, q = at(x0, y0 - pose["brow"]), at(x1, y1 - pose["brow"])
        _stick(g, p[0], p[1], q[0], q[1], 4, BLACK)

    if pose["spark"]:  # unter Strom: Blitze an zufälligen Stellen
        for _ in range(4):
            x, y = ox + random.randint(4, FIELD_W - 12), random.randint(6, FIELD_H - 22)
            for dx in (0, 1):
                g.drawLine(x + 6 + dx, y, x + dx, y + 7, YELLOW)
                g.drawLine(x + dx, y + 7, x + 6 + dx, y + 7, YELLOW)
                g.drawLine(x + 6 + dx, y + 7, x + dx, y + 14, YELLOW)
    if pose["snot"]:  # Rotzblase unter den Augen; snot ist ihr Radius
        r = int(pose["snot"])
        x, y = at(50 + r, 68 + r)
        g.fillCircle(x, y, r, 0xC8ECF4)
        g.drawCircle(x, y, r, 0x5090A8)
        g.fillCircle(x - r // 3, y - r // 3, 1, WHITE)
    for k in range(3 if pose["zzz"] else 0):  # Schlaf: drei Zs steigen auf, wachsen und treiben davon; zzz zählt hoch
        t = (pose["zzz"] + k * 8) % 24
        x, y, n = ox + 56 + t + (t // 3 % 2) * 2, HEADROOM + 6 - t - t // 4, 3 + t // 4
        for dy in (0, 1):
            g.drawLine(x, y + dy, x + n, y + dy, 0x101060)
            g.drawLine(x + n, y + dy, x, y + n + dy, 0x101060)
            g.drawLine(x, y + n + dy, x + n, y + n + dy, 0x101060)
