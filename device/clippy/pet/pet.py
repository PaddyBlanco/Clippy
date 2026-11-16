# Die Klammer als Ganzes: zeichnet sich in ihr Feld, lebt im Ruhezustand von selbst, reagiert auf ihre Sinne.
import random
import time

from clippy.pet import moves, phrases, sleep
from clippy.pet.bubble import Bubble
from clippy.pet.draw import REST
from clippy.pet.habits import IDLE, ONGOING, REACT, SNOT_CHANCE, SOMETIMES, SPOKEN, TIRED, URGENT
from clippy.pet.idle import Idle
from clippy.pet.rest import rest_pose
from clippy.pet.stage import Stage


class Pet:
    def __init__(self, display, senses, paint):
        """paint(g): zeichnet den ganzen Desktop nach g, z. B. nach dem Umdrehen."""
        self.d = display
        self.senses = senses
        self.stage = Stage(display, paint, senses.agents)
        self.then_say = None     # Spruch, der nach der laufenden Bewegung kommt
        self.bubble = Bubble(display)
        self.pose = dict(REST)
        self.move = None
        self.asleep = False
        now = time.ticks_ms()
        self.idle = Idle(IDLE)
        self.tired = Idle(TIRED)  # im Finstern statt idle
        self.last = {}           # Ereignis -> wann zuletzt darauf reagiert
        self.awake_since = now
        self.slow_due = now
        self.snore = 0
        self.snot = False        # schläft sie diesmal mit Rotzblase
        self.nodded = None       # awake_since beim letzten Einnicken: je Ruhezeit nur einmal
        self.level = None        # aktuelle Display-Helligkeit
        self._light()            # nach einem Abbruch im Schlaf wäre es sonst noch gedimmt
        self.until = {}          # Andauerndes (Trommeln, Streicheln): Ereignis -> gilt bis zu diesem Zeitpunkt
        self.show()

    def _ongoing(self, event, now):
        return event in self.until and time.ticks_diff(self.until[event], now) > 0

    def show(self):
        if self.stage.needs_wide(self.pose):
            self.bubble.hush()  # die Blase läge mitten auf der Bühne
        self.stage.show(self.pose)

    def refresh(self):
        """Nach einer App: Der Desktop wurde neu gezeichnet, also auch sich selbst, und die Blase ist weg."""
        self.bubble.box = None
        self.stage.was_wide = False
        self.awake_since = time.ticks_ms()
        self.show()

    def play(self, move):
        """Startet eine Bewegung sofort, z. B. clippy.play(moves.curl)."""
        self.move = move()

    def say(self, s, seconds=6, urgent=False):
        """Sprechblase. Solange ein Agent arbeitet, nur wenn es wichtig ist (urgent)."""
        if s and (urgent or not self.senses.agents.working()):
            self.bubble.say(s.replace("{agent}", self.senses.agents.last), seconds)

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
        self.asleep = False
        if event == "agent_working":
            self.bubble.hush()  # ein Agent arbeitet: kein Gerede, nur das Arbeitswort
        if event == "flip":  # Display mitdrehen, Desktop neu; sie selbst zeichnet gleich tumble
            self.stage.turn(self.senses.flipped)
            self.bubble.box = None
        if event in SOMETIMES and random.random() < SOMETIMES[event][2]:
            self.play(SOMETIMES[event][0])
            self.then_say = phrases.pick(SOMETIMES[event][1])
            return
        self.play(move)
        if random.random() < chatty:
            self.say(phrases.pick(event), urgent=event in URGENT)

    def _rest_pose(self):
        return rest_pose(self.senses, self._ongoing("beat", time.ticks_ms()))

    def _light(self):
        level = sleep.brightness(self.senses, self.asleep)
        if level != self.level:
            self.level = level
            self.d.setBrightness(level)

    def _every_second(self, now):
        for event in self.senses.slow():
            self.react(event)
        limit = sleep.limit(self.senses)
        quiet = time.ticks_diff(now, self.awake_since) / 1000
        if limit is None:
            self.asleep = False  # es ist wieder hell: aufwachen
        elif not self.asleep and quiet > limit:
            self.asleep, self.move = True, None
            self.snot = random.random() < SNOT_CHANCE
            self.say(phrases.pick("sleep"), 4)
        elif not self.asleep and quiet > limit / 2 and self.nodded != self.awake_since and self.move is None:
            self.nodded = self.awake_since  # müde: einmal einnicken und hochschrecken
            self.play(moves.nod)
            if random.random() < 0.5:
                self.say(phrases.pick("nod"))

    def step(self):
        """Einmal je Schleifendurchlauf aufrufen."""
        now = time.ticks_ms()
        self.bubble.step()
        for event in self.senses.poll():
            self.react(event)
        if time.ticks_diff(now, self.slow_due) > 0:
            self.slow_due = time.ticks_add(now, 1000)
            self._every_second(now)
        self._light()

        busy = self._ongoing("beat", now) or self._ongoing("pet", now)
        if self.move is None and not self.asleep and not busy:
            idle = self.tired if self.senses.dark else self.idle
            m = idle.next(now, time.ticks_diff(now, self.awake_since))
            if m:
                self.move = m()
                if m in SPOKEN and random.random() < 0.5:
                    self.say(phrases.pick(SPOKEN[m]))
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
                self.pose = sleep.pose(self.snore // 2, self.snot)
                self.show()
        elif self.pose != self._rest_pose() or self.senses.agents.verb:  # Neigung, Schlagzeug, Arbeitswort dreht sich
            self.pose = self._rest_pose()
            self.show()
