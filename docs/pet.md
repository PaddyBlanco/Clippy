# Die Klammer

Code: `device/lib/pet.py`. Stand: Sie sitzt rechts unten am Desktop, blinzelt, schaut sich um, macht ab und zu
Bizepscurls und kann sprechen. Stimmungen, Sensoren und Sprüche aus einer Datei folgen.

## Wie sie gezeichnet wird

Die Klammer ist keine Bilddatei, sondern wird aus Bögen, Balken und Ellipsen gezeichnet: `pet.draw(g, pose)`.
Eine **Haltung** (`pose`) ist ein Dictionary; `pet.REST` ist die Ruhehaltung.

| Schlüssel | Bedeutung | Ruhe |
|---|---|---|
| `look` | Blickrichtung als (x, y) in Pixeln, etwa −5 bis 5 | (0, 0) |
| `lid` | Augenlid: 0 = offen, 1 = zu | 0 |
| `brow` | Brauen: positiv = gehoben, negativ = gesenkt | 0 |
| `bob` | ganze Figur nach unten versetzt, in Pixeln | 0 |
| `arm` | Unterarm (freies Drahtende, rechts) in Grad: 0 = gerade nach oben, 105 = hängt nach außen | 0 |
| `weight` | Hantel in der Hand | False |

Alle Maße stehen als Konstanten oben in der Datei (`ARCS`, `STICKS`, `EYES`, ...). Ein Bild kostet am Gerät 20 ms.

## Neue Bewegung

Eine Bewegung ist eine Funktion, die Bild für Bild eine Haltung liefert. Beispiel aus dem Code:

```python
def blink():
    for lid in (0.5, 1.0, 1.0, 0.5):
        yield dict(REST, lid=lid)
```

- Sofort abspielen: `clippy.play(pet.blink)`.
- Von selbst im Ruhezustand: in `Pet.__init__` bei `self.due` (erster Zeitpunkt) und `self.pause`
  (Abstand von–bis in Millisekunden) eintragen.
- Das Tempo gibt die Hauptschleife in `device/main.py` vor: etwa 12 Bilder pro Sekunde.

Ansehen ohne Gerät: `python tools/preview.py device/main.py local/preview.png 200`. Die letzte Zahl ist die
Anzahl der Schleifendurchläufe; so lässt sich ein bestimmter Moment einer Bewegung festhalten.

## Sprechblase

`clippy.say("Text", seconds=6)` zeigt eine gelbe Sprechblase links neben dem Kopf, bricht den Text selbst um und
räumt sie nach der Zeit wieder weg. `clippy.hush()` entfernt sie sofort. Platz ist für etwa sechs Zeilen zu je
rund 18 Zeichen.

## Feld

Die Klammer lebt in einem Feld von 122×152 Pixeln rechts unten (`FIELD_X`, `FIELD_Y`). Nur dieses Feld wird je
Bild neu gezeichnet. Wer dort etwas anderes zeichnet, wird beim nächsten Bild überschrieben.
