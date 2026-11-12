# Die Klammer als Ganzes: zeichnet sich in ihr Feld, lebt im Ruhezustand von selbst, reagiert auf ihre Sinne.
import random
import time

from clippy import win98
from clippy.pet import moves, phrases
from clippy.pet.bubble import Bubble
from clippy.pet.draw import FIELD_H, FIELD_W, FIELD_X, FIELD_Y, REST, STAGE_W, STAGE_X, draw
from clippy.pet.habits import (BRIGHT, DIM, IDLE, ONGOING, QUIET, REACT, SLEEP_AFTER_DARK, SLEEP_AFTER_NIGHT,
                               SNOT_CHANCE, SOMETIMES, SPOKEN)


class Pet:
    def __init__(self, display, senses):
        self.d = display
        self.senses = senses
        self.work = display.newCanvas(FIELD_W, FIELD_H, 16, True)
        self.back = self.work.newCanvas(FIELD_W, FIELD_H, 16, True)  # Desktop-Ausschnitt, einmal geholt
        win98.backdrop(self.back, FIELD_X, FIELD_Y)
        self.stage = None        # breite Bühne zum Umfallen, wird erst beim ersten Sturz angelegt
        self.was_wide = False
        self.then_say = None     # Spruch, der nach der laufenden Bewegung kommt
        self.bubble = Bubble(display)
        self.pose = dict(REST)
        self.move = None
        self.asleep = False
        now = time.ticks_ms()
        self.due = {m: time.ticks_add(now, first) for m, (first, _, _) in IDLE.items()}
        self.last = {}           # Ereignis -> wann zuletzt darauf reagiert
        self.awake_since = now
        self.slow_due = now
        self.snore = 0
        self.snot = False        # schläft sie diesmal mit Rotzblase
        display.setBrightness(BRIGHT)  # nach einem Abbruch im Schlaf wäre es sonst noch gedimmt
        self.until = {}          # Andauerndes (Trommeln, Streicheln): Ereignis -> gilt bis zu diesem Zeitpunkt
        self.show()

    def _ongoing(self, event, now):
        return event in self.until and time.ticks_diff(self.until[event], now) > 0

    def show(self):
        wide = self.pose["lean"] > 0  # nur der Sturz nach links braucht mehr Platz
        if wide or self.was_wide:  # kippt, liegt oder steht gerade wieder auf: breite Bühne
            if self.stage is None:
                work = self.d.newCanvas(STAGE_W, FIELD_H, 16, True)
                back = work.newCanvas(STAGE_W, FIELD_H, 16, True)
                win98.backdrop(back, STAGE_X, FIELD_Y)
                self.stage = (work, back)
            self.bubble.hush()  # die Blase läge mitten auf der Bühne
            work, back = self.stage
            back.push(0, 0)
            draw(work, self.pose, STAGE_W - FIELD_W)
            work.push(STAGE_X, FIELD_Y)
        else:
            self.back.push(0, 0)
            draw(self.work, self.pose)
            self.work.push(FIELD_X, FIELD_Y)
        self.was_wide = wide

    def refresh(self):
        """Nach einer App: Der Desktop wurde neu gezeichnet, also auch sich selbst, und die Blase ist weg."""
        self.bubble.box = None
        self.was_wide = False
        self.awake_since = time.ticks_ms()
        self.show()

    def play(self, move):
        """Startet eine Bewegung sofort, z. B. clippy.play(moves.curl)."""
        self.move = move()

    def say(self, s, seconds=6):
        if s:
            self.bubble.say(s, seconds)

    def react(self, event):
        move, gap, chatty = REACT[event]
        now = time.ticks_ms()
        self.awake_since = now
        if event in self.last and time.ticks_diff(now, self.last[event]) < gap * 1000:
            return
        self.last[event] = now
        if event in ONGOING:  # nur zu Beginn etwas sagen, dann die Frist verlängern
            name, ms = ONGOING[event]
            if not self._ongoing(event, now) and random.random() < 0.5:
                self.say(phrases.pick(name))
            self.until[event] = time.ticks_add(now, ms)
        if self.asleep:
            self.asleep = False
            self.d.setBrightness(BRIGHT)
        if event in SOMETIMES and random.random() < SOMETIMES[event][2]:
            self.play(SOMETIMES[event][0])
            self.then_say = phrases.pick(SOMETIMES[event][1])
            return
        self.play(move)
        if random.random() < chatty:
            self.say(phrases.pick(event))

    def _rest_pose(self):
        if self._ongoing("beat", time.ticks_ms()):  # wartet mit erhobenem Schlägel auf den nächsten Schlag
            return dict(REST, arm=50, stick=True, drum=True, brow=2, look=(4, 3))
        # Ruhehaltung: nachts müde Lider, der Blick folgt der Seitenneigung
        return dict(REST, lid=0.4 if self.senses.night else 0.0, look=(self.senses.tilt, 0))

    def _every_second(self, now):
        for event in self.senses.slow():
            self.react(event)
        s = self.senses
        limit = SLEEP_AFTER_NIGHT if s.night else SLEEP_AFTER_DARK if s.light <= 1 else None
        if limit and not self.asleep and time.ticks_diff(now, self.awake_since) > limit * 1000:
            self.asleep, self.move = True, None
            self.snot = random.random() < SNOT_CHANCE
            self.say(phrases.pick("sleep"), 4)
            self.d.setBrightness(DIM)

    def step(self):
        """Einmal je Schleifendurchlauf aufrufen."""
        now = time.ticks_ms()
        self.bubble.step()
        for event in self.senses.poll():
            self.react(event)
        if time.ticks_diff(now, self.slow_due) > 0:
            self.slow_due = time.ticks_add(now, 1000)
            self._every_second(now)

        busy = self._ongoing("beat", now) or self._ongoing("pet", now)
        if self.move is None and not self.asleep and not busy:
            for m, due in self.due.items():
                if time.ticks_diff(now, due) > 0:
                    _, lo, hi = IDLE[m]
                    self.due[m] = time.ticks_add(now, random.randint(lo, hi))
                    if m is moves.zap and not self.senses.charging:
                        continue
                    if m in QUIET and time.ticks_diff(now, self.awake_since) < QUIET[m] * 1000:
                        continue
                    self.move = m()
                    if m in SPOKEN and random.random() < 0.5:
                        self.say(phrases.pick(SPOKEN[m]))
                    break
        if self.move:
            try:
                self.pose = next(self.move)
            except StopIteration:
                self.move, self.pose = None, self._rest_pose()
            self.show()
            if self.move is None and self.then_say:
                self.say(self.then_say)
                self.then_say = None
        elif self.asleep:
            self.snore += 1
            if self.snore % 2 == 0:  # jedes zweite Bild: Zs treiben weiter, sie atmet
                breath = abs(self.snore // 2 % 20 - 10)  # 0 bis 10 und zurück
                self.pose = dict(REST, lid=1.0, zzz=self.snore // 2, bob=breath // 5,
                                 snot=3 + breath * 0.6 if self.snot else 0)
                self.show()
        elif self.pose != self._rest_pose():  # Neigung geändert oder Schlagzeug weggeräumt
            self.pose = self._rest_pose()
            self.show()
