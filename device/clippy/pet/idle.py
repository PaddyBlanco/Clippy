# Was die Klammer von selbst tut: führt eine Tabelle wie IDLE aus habits.py aus und wählt die nächste fällige Bewegung.
import random
import time

from clippy.pet.habits import QUIET


class Idle:
    def __init__(self, table):
        """table: Bewegung -> (erstes Mal nach ms, danach Pause von, bis in ms), z. B. habits.IDLE."""
        self.table = table
        now = time.ticks_ms()
        self.due = {m: time.ticks_add(now, first) for m, (first, _, _) in table.items()}

    def next(self, now, quiet_ms):
        """Die nächste fällige Bewegung oder None. quiet_ms: so lange war kein Ereignis."""
        for m, due in self.due.items():
            if time.ticks_diff(now, due) > 0:
                _, lo, hi = self.table[m]
                self.due[m] = time.ticks_add(now, random.randint(lo, hi))
                if m in QUIET and quiet_ms < QUIET[m] * 1000:
                    continue
                return m
        return None
