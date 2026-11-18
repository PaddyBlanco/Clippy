# Die Büroklammer zeichnen: eine Haltung (pose) hinein, ein Bild heraus.
# Koordinaten gelten im eigenen Feld (FIELD_W × FIELD_H); wo das Feld am Desktop liegt, sagen FIELD_X/Y.
import math

from clippy.pet import extras

HEADROOM = 60  # Luft über dem Kopf: dort springt sie, und dort steht die Konsole, wenn ein Agent arbeitet
FIELD_W, FIELD_H = 122, 152 + HEADROOM
FIELD_X, FIELD_Y = 320 - FIELD_W, 212 - FIELD_H   # von ganz oben bis zur Taskleiste
TOUCH_Y = 36   # Antippen zählt erst ab hier, also unter der Konsole
# Zum Umfallen und Rollen braucht sie Platz nach links: Bühne über die ganze Breite, nur solange sie kippt oder rollt
STAGE_W = 320
STAGE_X = 0

SILVER = (0x4A4A55, 0xA8A8B8, 0xE4E4EE)  # Draht: Kontur, Fläche, Glanzlicht
ANGRY = (0x6A1818, 0xD85050, 0xFFB8B8)   # dasselbe, wenn sie rot anläuft
WHITE = 0xFFFFFF
BLACK = 0x000000

# Draht als Mittellinien. Bögen: (Mitte x, Mitte y, Radius, Winkel von, bis), 0° zeigt nach rechts, im Uhrzeigersinn.
ARCS = ((49, 25, 20, 180, 360), (55, 109, 14, 0, 180), (56, 118, 27, 0, 180))
# Gerade Stücke: linkes Bein, mittleres Bein, inneres Ende
STICKS = ((29, 25, 29, 118), (69, 25, 69, 109), (41, 109, 41, 78))
# Das freie Ende rechts ist der Arm: Schulter unten, Ellbogen, Unterarm
SHOULDER, ELBOW, FOREARM = (83, 118), (83, 98), 24
POGO_X, POGO_BEND = 56, 152  # Pogostick: von der Schulter schräg unter die Mitte, dann gerade hinunter
EYES = ((29, 47), (71, 55))
EYE_RX, EYE_RY = 17, 14
PUPIL_R = 8
BROWS = ((14, 33, 26, 24), (26, 24, 43, 23), (62, 30, 78, 31), (78, 31, 91, 42))
ANGRY_BROWS = ((12, 22, 44, 36), (58, 40, 92, 26))  # böser Blick: gerade Striche, außen hoch, innen tief
FOOT = (14, 147)  # um diesen Punkt links unten kippt sie
FOOT_RIGHT = (90, 147)
BOTTOM = ARCS[2][1] + ARCS[2][2]  # tiefster Punkt der Figur in Ruhe
CENTER = (52, 80)  # um diesen Punkt rollt sie
# Umriss zum Rollen: Punkte auf den Bögen und die Enden der Stücke; der tiefste davon bleibt am Boden
HULL = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        for cx, cy, r, a0, a1 in ARCS for a in range(a0, a1 + 1, 15)] + [p for s in STICKS for p in (s[:2], s[2:])]

REST = {"look": (0, 0), "lid": 0.0, "brow": 0, "frown": False, "bob": 0, "dx": 0, "stretch": 0, "lean": 0, "roll": 0,
        "arm": 0, "pogo": 0, "red": False, "weight": False, "stick": False, "drum": False, "spark": False, "zzz": 0,
        "snot": 0, "umbrella": False}


def _arc(g, x, y, r0, r1, a0, a1, c):
    # Bogen mit beliebigen Winkeln; über 0° hinweg in zwei Stücken
    a0, a1 = a0 % 360, a1 % 360 or 360
    if a0 < a1:
        g.fillArc(x, y, r0, r1, a0, a1, c)
    else:
        g.fillArc(x, y, r0, r1, a0, 360, c)
        g.fillArc(x, y, r0, r1, 0, a1, c)


def _pupil(g, ex, ey, rx, ry, px, py):
    # Pupille in voller Größe, Zeile für Zeile nur so weit, wie das Auge (Ellipse um ex, ey) offen ist
    for dy in range(-PUPIL_R, PUPIL_R + 1):
        t = py + dy - ey  # Zeile, vom Augenmittelpunkt aus
        if abs(t) >= ry:
            continue
        half = rx * math.sqrt(1 - t * t / (ry * ry))  # so breit ist das Auge in dieser Zeile
        w = math.sqrt(PUPIL_R * PUPIL_R - dy * dy)
        x0, x1 = max(px - w, ex - half), min(px + w, ex + half)
        if x0 <= x1:
            g.drawLine(int(x0), py + dy, int(x1), py + dy, BLACK)
    if abs(py - 3 - ey) < ry - 2:  # Glanzpunkt, wenn er im offenen Teil liegt
        g.fillCircle(px - 3, py - 3, 2, WHITE)


def _pivot(pose, ca, sa):
    """Drehpunkt und wie weit die Figur dabei abgesenkt wird, damit sie am Boden bleibt."""
    if pose["roll"]:  # rollen: um die Mitte, der tiefste Punkt des Umrisses liegt am Boden
        cx, cy = CENTER
        return CENTER, BOTTOM - max(cy + (x - cx) * sa + (y - cy) * ca for x, y in HULL)
    foot = FOOT if pose["lean"] >= 0 else FOOT_RIGHT  # nach links über den linken Fuß, nach rechts über den rechten
    # Beim Kippen rollt sie auf dem unteren Bogen ab: so weit absenken, dass er am Boden bleibt statt zu schweben
    ux, uy = ARCS[2][0] - foot[0], ARCS[2][1] - foot[1]
    return foot, max(0, -int(ux * sa + uy * ca) - ARCS[2][2] - 5)


def draw(g, pose, ox=0):
    """Zeichnet die Klammer nach g, um ox nach rechts versetzt. pose: siehe REST und docs/pet.md."""
    turn, bob, stretch = pose["lean"] + pose["roll"], pose["bob"], pose["stretch"]
    ca, sa = math.cos(math.radians(-turn)), math.sin(math.radians(-turn))
    (px, py), drop = _pivot(pose, ca, sa)
    ox += pose["dx"]

    def at(x, y):  # Punkt der Figur -> Punkt im Bild: strecken, wippen, drehen, versetzen
        if y < 70:  # obere Hälfte wandert beim Strecken nach oben, die Beine werden länger
            y -= stretch
        dx, dy = x - px, y + bob - py
        return int(ox + px + dx * ca - dy * sa), int(HEADROOM + py + drop + dx * sa + dy * ca)

    a = math.radians(pose["arm"])  # Unterarm: 0 = gerade nach oben, 105 = hängt nach außen
    hand = (ELBOW[0] + FOREARM * math.sin(a), ELBOW[1] - FOREARM * math.cos(a))
    if pose["pogo"]:  # das freie Ende steht als Stick unter ihr
        arm = (SHOULDER + (POGO_X, POGO_BEND), (POGO_X, POGO_BEND, POGO_X, BOTTOM + 2 + pose["pogo"]))
    else:
        arm = (SHOULDER + ELBOW, ELBOW + hand)
    for t, c in zip((7, 5, 1), ANGRY if pose["red"] else SILVER):
        shift = 0 if t > 1 else -1  # Glanzlicht sitzt leicht links oben
        for cx, cy, r, a0, a1 in ARCS:
            x, y = at(cx + shift, cy + shift)
            _arc(g, x, y, r - t // 2, r + t // 2, a0 - turn, a1 - turn, c)
        for x0, y0, x1, y1 in STICKS + arm:
            p, q = at(x0 + shift, y0), at(x1 + shift, y1)
            if t > 1:
                extras.stick(g, p[0], p[1], q[0], q[1], t, c)
            else:
                g.drawLine(p[0], p[1], q[0], q[1], c)
    extras.in_hand(g, pose, at, hand)

    lx, ly = pose["look"]
    gap = max(1, int(EYE_RY * (1 - pose["lid"])))  # wie weit das Auge offen ist
    rx, ry = (gap, EYE_RX) if 45 < turn % 180 < 135 else (EYE_RX, gap)  # liegt sie, liegen auch die Augen quer
    for ex, ey in EYES:
        x, y = at(ex, ey)
        g.fillEllipse(x, y, rx + 1, ry + 1, BLACK)
        if pose["lid"] >= 1:  # ganz zu: nur der dunkle Lidstrich, kein weißer Spalt
            continue
        g.fillEllipse(x, y, rx, ry, WHITE)
        _pupil(g, x, y, rx, ry, x + lx, y + ly)
    for x0, y0, x1, y1 in ANGRY_BROWS if pose["frown"] else BROWS:  # brow > 0 hebt die Brauen
        p, q = at(x0, y0 - pose["brow"]), at(x1, y1 - pose["brow"])
        extras.stick(g, p[0], p[1], q[0], q[1], 4, BLACK)
    extras.around(g, pose, at, ox, FIELD_W, FIELD_H, HEADROOM)
