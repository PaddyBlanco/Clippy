# Müdigkeit der Klammer: wann sie einnickt und einschläft, wie hell das Display ist, wie sie im Schlaf aussieht.
import random
import time

from clippy.pet import moves, phrases
from clippy.pet.draw import REST
from clippy.pet.habits import BRIGHT, DIM, DUSK, SLEEP_AFTER_COVERED, SLEEP_AFTER_DARK, SLEEP_AFTER_NIGHT, SNOT_CHANCE


def limit(senses):
    """Sekunden ohne Ereignis, bis sie einschläft; None = sie ist nicht müde und bleibt wach."""
    if senses.dark:
        return SLEEP_AFTER_COVERED
    if senses.night:
        return SLEEP_AFTER_NIGHT
    if senses.light <= 1:
        return SLEEP_AFTER_DARK
    return None


def check(pet, now):
    """Einmal je Sekunde: aufwachen, wenn es hell ist; einschlafen nach langer Ruhe; nach der halben Zeit einnicken."""
    most = limit(pet.senses)
    quiet = time.ticks_diff(now, pet.awake_since) / 1000
    if most is None:
        pet.asleep = False  # es ist wieder hell: aufwachen
    elif not pet.asleep and quiet > most:
        pet.asleep, pet.move = True, None
        pet.snot = random.random() < SNOT_CHANCE
        pet.say(phrases.pick("sleep"), 4)
    elif not pet.asleep and quiet > most / 2 and pet.nodded != pet.awake_since and pet.move is None:
        pet.nodded = pet.awake_since  # müde: einmal einnicken und hochschrecken
        pet.play(moves.nod)
        if random.random() < 0.5:
            pet.say(phrases.pick("nod"))


def brightness(senses, asleep):
    return DIM if asleep else DUSK if senses.dark else BRIGHT


def pose(n, snot):
    """Bild n des Schlafs: Zs treiben weiter, sie atmet; snot: mit Rotzblase."""
    breath = abs(n % 20 - 10)  # 0 bis 10 und zurück
    return dict(REST, lid=1.0, zzz=n, bob=breath // 5, snot=3 + breath * 0.6 if snot else 0)
