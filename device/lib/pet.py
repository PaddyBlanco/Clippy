# Die Büroklammer: Zeichnung aus einer Haltung (pose) und ihr Ruheverhalten.
# Koordinaten gelten im eigenen Feld (FIELD_W × FIELD_H); wo das Feld am Desktop liegt, sagen FIELD_X/Y.
import math
import random
import time

from lib import win98

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


# --- Bewegungen: jede liefert Bild für Bild eine Haltung. Neue Bewegung = neue Funktion dieser Art. ---

def blink():
    for lid in (0.5, 1.0, 1.0, 0.5):
        yield dict(REST, lid=lid)


def glance():
    side = random.choice((-5, 5))
    for _ in range(14):
        yield dict(REST, look=(side, 1), brow=1)


def curl():
    # Hantel greifen, viermal heben, weglegen
    for arm in (30, 60, 90, 105):
        yield dict(REST, arm=arm, look=(4, 3))
    for _ in range(4):
        for arm in (105, 85, 65, 45, 30, 20, 20):
            yield dict(REST, arm=arm, weight=True, brow=-2, lid=0.25, bob=1)
        for arm in (35, 55, 75, 95, 105, 105):
            yield dict(REST, arm=arm, weight=True, brow=1)
    for arm in (90, 60, 30):
        yield dict(REST, arm=arm)


BUBBLE_X, BUBBLE_W, BUBBLE_BOTTOM = 72, 124, FIELD_Y + 46
PAPER = 0xFFFFE1


def _wrap(g, s, width):
    lines, line = [], ""
    for word in s.split():
        trial = (line + " " + word).strip()
        if line and win98.text_width(g, trial) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


class Pet:
    def __init__(self, display):
        self.d = display
        self.work = display.newCanvas(FIELD_W, FIELD_H, 16, True)
        self.back = self.work.newCanvas(FIELD_W, FIELD_H, 16, True)  # Desktop-Ausschnitt, einmal geholt
        win98.backdrop(self.back, FIELD_X, FIELD_Y)
        self.pose = dict(REST)
        self.move = None
        now = time.ticks_ms()
        self.due = {blink: now + 2500, glance: now + 6000, curl: now + 9000}
        self.pause = {blink: (2500, 6000), glance: (8000, 20000), curl: (45000, 90000)}
        self.bubble = None  # (x, y, w, h, Ende in ms)
        self.show()

    def show(self):
        self.back.push(0, 0)
        draw(self.work, self.pose)
        self.work.push(FIELD_X, FIELD_Y)

    def play(self, move):
        """Startet eine Bewegung sofort, z. B. pet.play(curl)."""
        self.move = move()

    def say(self, s, seconds=6):
        self.hush()
        lines = _wrap(self.d, s, BUBBLE_W - 14)
        h = len(lines) * (win98.FONT_H + 1) + 10
        x, y = BUBBLE_X, BUBBLE_BOTTOM - h
        self.d.fillRoundRect(x, y, BUBBLE_W, h, 6, PAPER)
        self.d.drawRoundRect(x, y, BUBBLE_W, h, 6, BLACK)
        # Zipfel zeigt nach rechts unten zur Klammer
        self.d.fillTriangle(x + BUBBLE_W - 30, y + h - 1, x + BUBBLE_W - 14, y + h - 1, x + BUBBLE_W - 6, y + h + 11, PAPER)
        self.d.drawLine(x + BUBBLE_W - 30, y + h - 1, x + BUBBLE_W - 6, y + h + 11, BLACK)
        self.d.drawLine(x + BUBBLE_W - 14, y + h - 1, x + BUBBLE_W - 6, y + h + 11, BLACK)
        for i, line in enumerate(lines):
            win98.text(self.d, line, x + 7, y + 5 + i * (win98.FONT_H + 1), BLACK, PAPER)
        self.bubble = (x, y, BUBBLE_W, h + 12, time.ticks_add(time.ticks_ms(), seconds * 1000))

    def hush(self):
        if self.bubble:
            x, y, w, h, _ = self.bubble
            c = self.d.newCanvas(w, h, 16, True)
            win98.backdrop(c, x, y)
            c.push(x, y)
            c.delete()
            self.bubble = None

    def step(self):
        """Einmal je Schleifendurchlauf aufrufen."""
        now = time.ticks_ms()
        if self.bubble and time.ticks_diff(now, self.bubble[4]) > 0:
            self.hush()
        if self.move is None:
            for move, due in self.due.items():
                if time.ticks_diff(now, due) > 0:
                    lo, hi = self.pause[move]
                    self.due[move] = time.ticks_add(now, random.randint(lo, hi))
                    self.move = move()
                    break
        if self.move:
            try:
                self.pose = next(self.move)
            except StopIteration:
                self.move, self.pose = None, dict(REST)
            self.show()
