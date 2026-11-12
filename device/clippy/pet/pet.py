# Die Klammer als Ganzes: zeichnet sich in ihr Feld, bewegt sich im Ruhezustand von selbst, kann sprechen.
import random
import time

from clippy import win98
from clippy.pet import moves
from clippy.pet.bubble import Bubble
from clippy.pet.draw import FIELD_H, FIELD_W, FIELD_X, FIELD_Y, REST, draw

# Was sie von selbst tut: Bewegung -> (erstes Mal nach ms, danach Pause von, bis in ms)
IDLE = {
    moves.blink: (2500, 2500, 6000),
    moves.glance: (6000, 8000, 20000),
    moves.curl: (9000, 45000, 90000),
}


class Pet:
    def __init__(self, display):
        self.work = display.newCanvas(FIELD_W, FIELD_H, 16, True)
        self.back = self.work.newCanvas(FIELD_W, FIELD_H, 16, True)  # Desktop-Ausschnitt, einmal geholt
        win98.backdrop(self.back, FIELD_X, FIELD_Y)
        self.bubble = Bubble(display)
        self.pose = dict(REST)
        self.move = None
        now = time.ticks_ms()
        self.due = {m: time.ticks_add(now, first) for m, (first, _, _) in IDLE.items()}
        self.show()

    def show(self):
        self.back.push(0, 0)
        draw(self.work, self.pose)
        self.work.push(FIELD_X, FIELD_Y)

    def play(self, move):
        """Startet eine Bewegung sofort, z. B. clippy.play(moves.curl)."""
        self.move = move()

    def say(self, s, seconds=6):
        self.bubble.say(s, seconds)

    def step(self):
        """Einmal je Schleifendurchlauf aufrufen."""
        now = time.ticks_ms()
        self.bubble.step()
        if self.move is None:
            for m, due in self.due.items():
                if time.ticks_diff(now, due) > 0:
                    _, lo, hi = IDLE[m]
                    self.due[m] = time.ticks_add(now, random.randint(lo, hi))
                    self.move = m()
                    break
        if self.move:
            try:
                self.pose = next(self.move)
            except StopIteration:
                self.move, self.pose = None, dict(REST)
            self.show()
