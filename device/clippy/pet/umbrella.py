# Schirm bei Regen: Die App Wetter sagt per ctx.weather, ob es nass ist; solange hält die Klammer einen
# aufgespannten Schirm über den Kopf. Wie das Tanzen beim Radio, nur im eigenen Feld, nie auf der breiten Bühne.
from clippy.pet.draw import REST

ARM = -8        # Unterarm leicht nach innen, so steht der Schirm über ihr
_on = [False]   # spannt sie gerade den Schirm auf


def rain(on):
    """True: es ist nass, Schirm auf. False: Schirm zu."""
    _on[0] = bool(on)


def raining():
    return _on[0]


def hold():
    # steht unter dem Schirm, wippt ein wenig, schaut in der Mitte hinauf, ob es noch regnet; gut vier Sekunden
    for i in range(48):
        if not _on[0]:
            return  # trocken geworden oder Fenster zu: Schirm gleich weg, nicht erst nach der Runde
        up = 16 <= i < 32
        yield dict(REST, umbrella=True, arm=ARM + (i // 6 % 2) * 2, bob=(0, 0, 1, 1)[i // 3 % 4],
                   look=(2, -5) if up else (0, 1), brow=3 if up else 0)
