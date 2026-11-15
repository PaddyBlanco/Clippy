# Gerät auf den Kopf gestellt: Der Desktop hat sich schon umgedreht. Sie hängt noch dort, wo sie vorher war
# (jetzt links oben, verkehrt herum), fällt auf den Kopf, rollt nach rechts an ihren Platz und ist grantig.
import math

from clippy.pet.draw import REST

START_DX = -181  # so weit links hängt sie nach dem Umdrehen, in Pixeln: genau dort, wo sie vorher stand
START_BOB = 31   # so hoch über dem Boden; bob hebt sie, weil sie verkehrt herum ist
STEPS = 12       # Bilder für das Rollen an ihren Platz


def tumble():
    upside = dict(REST, roll=180, dx=START_DX, red=True)
    for _ in range(3):  # hängt kurz verdutzt, dann geht's abwärts
        yield dict(upside, bob=START_BOB, brow=5, look=(0, 3))
    for t in (0.35, 0.6, 0.8, 0.95, 1.0):
        yield dict(upside, bob=int(START_BOB * (1 - t * t)), brow=5)
    for bob in (4, 0, 2, 0):  # prallt am Kopf auf
        yield dict(upside, bob=bob, brow=3, lid=0.3)
    for i in range(8):  # benommen am Kopf
        yield dict(upside, look=(int(5 * math.cos(i * 0.9)), int(4 * math.sin(i * 0.9))), brow=2)
    for i in range(1, STEPS + 1):  # rollt nach rechts zurück an ihren Platz
        yield dict(REST, roll=180 - 180 * i // STEPS, dx=START_DX - START_DX * i // STEPS, red=True, brow=1)
    for i in range(16):  # steht wieder, rot vor Zorn, schüttelt den Kopf
        yield dict(REST, red=True, frown=True, lid=0.3, look=((-4, 4)[i // 2 % 2], 0), bob=i % 2)
