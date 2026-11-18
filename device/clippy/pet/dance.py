# Tanzen, solange Musik läuft (App Radio): drei Figuren, die sich abwechseln. Jede dauert gut drei Sekunden;
# läuft die Musik weiter, beginnt die nächste. Alles bleibt im Feld der Klammer, nichts braucht die breite Bühne.
import random

from clippy.pet.draw import REST

BOUNCE = (0, -2, -4, -2, 0, 1)  # ein Takt: hoch und wieder runter, unten kurz in die Knie


def sway():
    # wippt im Takt und schwingt von Seite zu Seite, der Blick geht mit, das Drahtende winkt
    for i in range(48):
        side = -5 if i // 12 % 2 == 0 else 5
        yield dict(REST, dx=side, bob=BOUNCE[i % 6], look=(side // 2, 0), arm=(-15, 15)[i // 3 % 2], brow=3)


def hop():
    # hüpft auf der Stelle, streckt sich oben, landet gestaucht; die Augen zu vor Vergnügen
    for i in range(8):
        for bob, stretch in ((0, -4), (-6, 4), (-10, 6), (-6, 3), (0, -4), (1, -2)):
            yield dict(REST, bob=bob, stretch=stretch, lid=1.0 if i % 4 >= 2 else 0.0, brow=4, arm=-15)


def groove():
    # lässig: kleiner Wipper, halbe Lider, das Drahtende kreist langsam
    for i in range(48):
        yield dict(REST, bob=BOUNCE[i % 6] // 2, dx=(-2, 0, 2, 0)[i // 6 % 4], lid=0.5, brow=2,
                   arm=(0, 20, 40, 20)[i // 4 % 4], look=(3, -1))


def dance():
    yield from random.choice((sway, hop, groove))()
