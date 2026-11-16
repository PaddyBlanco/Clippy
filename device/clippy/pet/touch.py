# Berührung der Klammer: unterscheidet Antippen von Streicheln.
# Hebt der Finger kurz ab und setzt binnen RELEASE_MS woanders wieder auf, war es ein Aussetzer beim Wischen:
# dieselbe Berührung. Setzt er an derselben Stelle wieder auf, ist es ein neuer Tipper.
import time

import M5

from clippy.pet.draw import FIELD_X, TOUCH_Y

HOLD_MS = 350           # liegt der Finger länger auf ihr, ist es Streicheln statt Antippen
MOVE_PX = 8             # wandert der Finger weiter, ist es auch Streicheln
RELEASE_MS = 200        # so lange kein Kontakt, bis die Berührung als beendet gilt
STILL_PETTING_MS = 1000  # kurzes Berühren so knapp nach dem Streicheln gehört noch dazu
PET_EVERY_MS = 400      # solange gestreichelt wird, so oft ein Ereignis


def _on_pet(x, y):
    return x >= FIELD_X and y >= TOUCH_Y


class Touch:
    def __init__(self):
        self.down = False       # Finger liegt gerade auf
        self.open = False       # eine Berührung läuft noch (Finger auf oder erst kurz abgehoben)
        self.start = self.lifted_at = 0
        self.x0 = self.y0 = self.x = self.y = 0
        self.began_on_pet = self.moved = self.stroked = False
        self.stroke_at = time.ticks_add(time.ticks_ms(), -STILL_PETTING_MS)
        self.taps = []

    def poll(self, now):
        """Liefert eine Liste von Ereignissen: "tap", "grumpy" oder "pet"."""
        events = []
        if M5.Touch.getCount() > 0:
            x, y = M5.Touch.getX(), M5.Touch.getY()
            if self.open and not self.down:  # Finger setzt kurz nach dem Abheben wieder auf
                if self._far(x, y, self.x, self.y):
                    self.moved = True  # woanders: Aussetzer beim Wischen
                else:
                    events += self._end(now)  # an derselben Stelle: der vorige war ein Tipper
            if not self.open:
                self.open, self.start, self.x0, self.y0 = True, now, x, y
                self.began_on_pet, self.moved, self.stroked = _on_pet(x, y), False, False
            self.down, self.x, self.y = True, x, y
            self.moved = self.moved or self._far(x, y, self.x0, self.y0)
            held = time.ticks_diff(now, self.start) > HOLD_MS
            if _on_pet(x, y) and (self.moved or held or not self.began_on_pet):  # von außen hereingewischt zählt auch
                if not self.stroked or time.ticks_diff(now, self.stroke_at) > PET_EVERY_MS:
                    self.stroked, self.stroke_at = True, now
                    events.append("pet")
        else:
            if self.down:
                self.down, self.lifted_at = False, now
            if self.open and time.ticks_diff(now, self.lifted_at) > RELEASE_MS:
                events += self._end(now)
        return events

    @staticmethod
    def _far(x, y, x0, y0):
        return abs(x - x0) + abs(y - y0) > MOVE_PX

    def _end(self, now):
        """Die Berührung ist vorbei: war sie kurz und ruhig auf ihr, ein Tipper."""
        self.open = False
        if not self.began_on_pet or self.stroked:
            return []
        if time.ticks_diff(now, self.stroke_at) < STILL_PETTING_MS + RELEASE_MS:
            return ["pet"]  # gehört noch zum Streicheln
        self.taps = [t for t in self.taps if time.ticks_diff(now, t) < 5000] + [now]
        if len(self.taps) >= 3:  # drei Tipper binnen 5 s machen sie grantig
            self.taps = []
            return ["grumpy"]
        return ["tap"]
