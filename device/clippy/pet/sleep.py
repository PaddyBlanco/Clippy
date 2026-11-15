# Müdigkeit der Klammer: wann sie einnickt und einschläft, wie hell das Display ist, wie sie im Schlaf aussieht.
from clippy.pet.draw import REST
from clippy.pet.habits import BRIGHT, DIM, DUSK, SLEEP_AFTER_COVERED, SLEEP_AFTER_DARK, SLEEP_AFTER_NIGHT


def limit(senses):
    """Sekunden ohne Ereignis, bis sie einschläft; None = sie ist nicht müde und bleibt wach."""
    if senses.dark:
        return SLEEP_AFTER_COVERED
    if senses.night:
        return SLEEP_AFTER_NIGHT
    if senses.light <= 1:
        return SLEEP_AFTER_DARK
    return None


def brightness(senses, asleep):
    return DIM if asleep else DUSK if senses.dark else BRIGHT


def pose(n, snot):
    """Bild n des Schlafs: Zs treiben weiter, sie atmet; snot: mit Rotzblase."""
    breath = abs(n % 20 - 10)  # 0 bis 10 und zurück
    return dict(REST, lid=1.0, zzz=n, bob=breath // 5, snot=3 + breath * 0.6 if snot else 0)
