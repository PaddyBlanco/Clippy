# Bewegungen der Klammer: jede liefert Bild für Bild eine Haltung (siehe draw.REST).
# Neue Bewegung = neue Funktion dieser Art; in habits.py bei IDLE (von selbst) oder REACT (auf ein Ereignis) eintragen.
import math
import random

from clippy.pet.draw import REST


def blink():
    for lid in (0.5, 1.0, 1.0, 0.5):
        yield dict(REST, lid=lid)


def glance():
    side = random.choice((-5, 5))
    for _ in range(14):
        yield dict(REST, look=(side, 1), brow=1)


def nod():
    # Sekundenschlaf: Lider fallen zu, sie sackt ab und schreckt hoch
    for lid, bob in ((0.3, 0), (0.5, 1), (0.7, 2), (0.9, 3), (1.0, 4), (1.0, 5), (1.0, 6), (1.0, 6), (1.0, 6)):
        yield dict(REST, lid=lid, bob=bob)
        yield dict(REST, lid=lid, bob=bob)
    for bob in (-4, -3, -1, 0):
        yield dict(REST, bob=bob, brow=4)


def lean_on():
    # lehnt sich lässig rechts an den Bildschirmrand
    for lean in (-4, -8, -12, -15):
        yield dict(REST, lean=lean)
    for i in range(40):
        yield dict(REST, lean=-15, lid=0.25, look=(-4, 1), brow=1 if i % 20 < 10 else 0)
    for lean in (-10, -5):
        yield dict(REST, lean=lean)


def attention():
    # will beachtet werden: hüpft hin und her und winkt
    for dx in (-6, 6, -6, 0):
        for bob, stretch in ((-5, 4), (-11, 7), (-5, 2), (0, -5)):
            yield dict(REST, dx=dx, bob=bob, stretch=stretch, brow=4)
    for i in range(18):
        yield dict(REST, arm=(10, 30, 50, 30)[i % 4], brow=4, bob=-1 if i % 2 else 0)


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


def hit():
    # ein einzelner Schlag auf die Trommel, wenn jemand mittrommelt
    for arm in (78, 78, 50):
        yield dict(REST, arm=arm, stick=True, drum=True, bob=1 if arm == 78 else 0, brow=2, look=(4, 3))


def fall():
    # umfallen: kippt über den linken Fuß, bleibt liegen, rappelt sich auf
    for lean in (6, 16, 32, 54, 78, 88, 84, 88):
        yield dict(REST, lean=lean, brow=4, look=(-3, 1))
    for _ in range(16):
        yield dict(REST, lean=88, lid=1.0)
    for lean in (74, 56, 36, 18, 6):
        yield dict(REST, lean=lean, brow=2)


def dizzy():
    # geschüttelt: Augen kreisen, sie schwankt
    for i in range(24):
        yield dict(REST, look=(int(5 * math.cos(i * 0.8)), int(4 * math.sin(i * 0.8))), bob=i % 4 - 1, brow=2)


def startle():
    # Schreck: sie springt hoch und streckt sich, landet gestaucht und federt nach
    for bob, stretch in ((-6, 6), (-14, 10), (-17, 8), (-14, 4), (-6, 0), (0, -7), (0, -4), (0, 3), (0, 0), (0, 0)):
        yield dict(REST, bob=bob, stretch=stretch, brow=5)


def flinch():
    # angetippt: sie duckt sich mit zugekniffenen Augen und schüttelt dann den Kopf
    for stretch in (-5, -8, -8, -4):
        yield dict(REST, lid=1.0, stretch=stretch, brow=-2)
    for side in (-5, 5, -5, 5, 0):
        yield dict(REST, look=(side, 0), brow=3, stretch=2)


DROWSY = dict(REST, lid=0.5)  # schwere Lider, entspannte Brauen, solange es finster ist


def drowsy():
    # müde im Finstern: langsam blinzeln, oder die Augen fallen zu und gehen mühsam wieder auf
    if random.random() < 0.5:
        lids = (0.6, 0.6, 0.7, 0.7, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6)
    else:
        lids = (0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.0, 1.0, 1.0, 1.0, 0.3, 0.25, 0.3, 0.35, 0.4, 0.45)
    for lid in lids:
        yield dict(DROWSY, lid=lid, bob=1 if lid >= 1 else 0)


def threaten():
    # richtig grantig: rot angelaufen droht sie mit dem Drahtende
    for i in range(32):
        yield dict(REST, red=True, brow=0, frown=True, lid=0.3, arm=(15, 40, 62, 40)[i % 4], bob=i % 2, look=(0, 2))


def enjoy():
    # gestreichelt: Augen zu, sie wiegt sich wohlig
    for bob in (0, 1, 2, 2, 1, 0):
        yield dict(REST, lid=1.0, brow=3, bob=bob, stretch=-1)


def cheer():
    # freut sich: springt zweimal hoch, reckt das Drahtende und winkt damit
    for _ in range(2):
        for bob, stretch in ((0, -4), (-8, 5), (-14, 7), (-8, 4), (0, -4)):
            yield dict(REST, bob=bob, stretch=stretch, arm=-15, brow=5)
    for i in range(8):
        yield dict(REST, arm=(-15, 15)[i // 2 % 2], brow=4)


def perk():
    # aufmerken: Brauen hoch, sie reckt sich
    for _ in range(10):
        yield dict(REST, brow=3, bob=-1)


def yawn():
    for lid in (0.3, 0.5, 0.7, 0.9, 0.9, 0.9, 0.6, 0.4):
        yield dict(REST, lid=lid, brow=2)


def zap():
    # unter Strom: sie zittert, Blitze zucken
    for i in range(16):
        yield dict(REST, bob=(i % 2) * 3 - 1, brow=4, look=(i % 3 - 1, 0), spark=True)
