# Bewegungen der Klammer: jede liefert Bild für Bild eine Haltung.
# Neue Bewegung = neue Funktion dieser Art; eintragen in pet.py bei IDLE, wenn sie von selbst kommen soll.
import random

from clippy.pet.draw import REST


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
