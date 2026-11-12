# Sprechblase links neben dem Kopf der Klammer.
import time

from clippy import win98
from clippy.pet.draw import FIELD_Y

X, W, BOTTOM = 72, 124, FIELD_Y + 46
PAPER = 0xFFFFE1
BLACK = 0x000000
LINE_H = win98.FONT_H + 1


def wrap(s, width, measure):
    """Bricht s in Zeilen um, die laut measure(zeile) höchstens width breit sind."""
    lines, line = [], ""
    for word in s.split():
        trial = (line + " " + word).strip()
        if line and measure(trial) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


class Bubble:
    def __init__(self, display):
        self.d = display
        self.box = None  # (x, y, w, h, Ende in ms), solange eine Blase steht

    def say(self, s, seconds=6):
        self.hush()
        d = self.d
        lines = wrap(s, W - 14, lambda t: win98.text_width(d, t))
        h = len(lines) * LINE_H + 10
        y = BOTTOM - h
        d.fillRoundRect(X, y, W, h, 6, PAPER)
        d.drawRoundRect(X, y, W, h, 6, BLACK)
        # Zipfel zeigt nach rechts unten zur Klammer
        tx, ty = X + W - 6, y + h + 11
        d.fillTriangle(X + W - 30, y + h - 1, X + W - 14, y + h - 1, tx, ty, PAPER)
        d.drawLine(X + W - 30, y + h - 1, tx, ty, BLACK)
        d.drawLine(X + W - 14, y + h - 1, tx, ty, BLACK)
        for i, line in enumerate(lines):
            win98.text(d, line, X + 7, y + 5 + i * LINE_H, BLACK, PAPER)
        self.box = (X, y, W, h + 12, time.ticks_add(time.ticks_ms(), seconds * 1000))

    def hush(self):
        if self.box:
            x, y, w, h, _ = self.box
            c = self.d.newCanvas(w, h, 16, True)
            win98.backdrop(c, x, y)
            c.push(x, y)
            c.delete()
            self.box = None

    def step(self):
        if self.box and time.ticks_diff(time.ticks_ms(), self.box[4]) > 0:
            self.hush()
