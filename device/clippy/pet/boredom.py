# Was die Klammer aus Langeweile tut: jedes Mal eines davon, zufällig. Einschlafen gehört nicht dazu.
import random

from clippy.pet import moves
from clippy.pet.draw import REST


def roll_eyes():
    # Augen verdrehen, einmal im Kreis
    for look in ((0, -4), (3, -4), (5, -2), (5, 0), (3, 2), (0, 3), (-3, 2), (-5, 0), (-3, -3), (0, -4)):
        yield dict(REST, look=look, lid=0.3, brow=-1)
        yield dict(REST, look=look, lid=0.3, brow=-1)


def stretch():
    # streckt sich lang nach oben, Augen zu, und sackt wieder zusammen
    for s in (2, 4, 6, 8, 9):
        yield dict(REST, stretch=s, arm=-s, lid=0.5, brow=2)
    for i in range(10):
        yield dict(REST, stretch=9 + i % 2, arm=-10, lid=1.0, brow=3)
    for s in (6, 2, -3, -2, 0):
        yield dict(REST, stretch=s, lid=0.4)


def drum_solo():
    # Schlagzeug-Solo: Schläge in wechselndem Takt, zum Schluss ein kräftiger
    kit = dict(REST, stick=True, drum=True, look=(4, 3))
    for arm in (30, 50):
        yield dict(kit, arm=arm)
    for pause in (2, 2, 1, 1, 2, 0, 0, 1, 0, 0, 0, 2, 1, 1, 0, 0, 0, 0):
        yield dict(kit, arm=78, bob=1, brow=2)
        for _ in range(pause + 1):
            yield dict(kit, arm=50, brow=1)
    for arm, brow in ((20, 4), (20, 4), (82, 5), (82, 5), (82, 5), (60, 3)):
        yield dict(kit, arm=arm, brow=brow, bob=1 if arm == 82 else 0)


def headstand():
    # rollt auf den Kopf, strampelt kurz verkehrt herum und rollt zurück
    for roll in range(0, 181, 20):
        yield dict(REST, roll=roll, dx=-6, brow=3)
    for i in range(14):
        yield dict(REST, roll=180 + (4 if i % 4 < 2 else -4), dx=-6, look=(0, 3), brow=2)
    for roll in range(160, -1, -20):
        yield dict(REST, roll=roll, dx=-6, brow=1)


def pogo():
    # hüpft auf dem Drahtende wie auf einem Pogostick
    for p in (8, 13, 17, 20):
        yield dict(REST, pogo=p, bob=-p, brow=2)
    for _ in range(7):
        for h in (0, 4, 7, 8, 7, 4, 0):
            yield dict(REST, pogo=20, bob=-20 - h, brow=4 if h else 2, stretch=-3 if h == 0 else 1)
    for p in (17, 13, 8, 0):
        yield dict(REST, pogo=p, bob=-p)


def bored():
    yield from random.choice((roll_eyes, stretch, drum_solo, moves.curl, headstand, pogo))()
