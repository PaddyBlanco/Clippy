# Die Klammer

Code: `device/clippy/pet/`. Stand: Sie sitzt rechts unten am Desktop, blinzelt, schaut sich um, macht ab und zu
Bizepscurls und kann sprechen. Stimmungen, Sensoren und Sprüche aus einer Datei folgen.

## Dateien

| Datei | Aufgabe |
|---|---|
| `draw.py` | Maße der Figur und `draw(g, pose)`: eine Haltung hinein, ein Bild heraus |
| `moves.py` | Bewegungen: Blinzeln, Umschauen, Curls |
| `bubble.py` | Sprechblase samt Zeilenumbruch |
| `pet.py` | Klasse `Pet`: hält alles zusammen, entscheidet, wann welche Bewegung kommt |

## Wie sie gezeichnet wird

Die Klammer ist keine Bilddatei, sondern wird aus Bögen, Balken und Ellipsen gezeichnet: `draw.draw(g, pose)`.
Eine **Haltung** (`pose`) ist ein Dictionary; `draw.REST` ist die Ruhehaltung.

| Schlüssel | Bedeutung | Ruhe |
|---|---|---|
| `look` | Blickrichtung als (x, y) in Pixeln, etwa −5 bis 5 | (0, 0) |
| `lid` | Augenlid: 0 = offen, 1 = zu | 0 |
| `brow` | Brauen: positiv = gehoben, negativ = gesenkt | 0 |
| `bob` | ganze Figur nach unten versetzt, in Pixeln | 0 |
| `arm` | Unterarm (freies Drahtende, rechts) in Grad: 0 = gerade nach oben, 105 = hängt nach außen | 0 |
| `weight` | Hantel in der Hand | False |

Alle Maße stehen als Konstanten oben in `draw.py` (`ARCS`, `STICKS`, `EYES`, ...). Ein Bild kostet am Gerät 20 ms.

## Neue Bewegung

Eine Bewegung ist eine Funktion in `moves.py`, die Bild für Bild eine Haltung liefert. Beispiel:

```python
def blink():
    for lid in (0.5, 1.0, 1.0, 0.5):
        yield dict(REST, lid=lid)
```

- Sofort abspielen: `clippy.play(moves.blink)`.
- Von selbst im Ruhezustand: in `pet.py` bei `IDLE` eintragen (erstes Mal nach, danach Pause von–bis,
  alles in Millisekunden).
- Das Tempo gibt die Hauptschleife in `device/clippy/desktop.py` vor: etwa 12 Bilder pro Sekunde.

Ansehen ohne Gerät: `python tools/preview.py device/main.py local/preview.png 200`. Die letzte Zahl ist die
Anzahl der Schleifendurchläufe; so lässt sich ein bestimmter Moment einer Bewegung festhalten.

## Sprechblase

`clippy.say("Text", seconds=6)` zeigt eine gelbe Sprechblase links neben dem Kopf, bricht den Text selbst um und
räumt sie nach der Zeit wieder weg. `clippy.hush()` entfernt sie sofort. Platz ist für etwa sechs Zeilen zu je
rund 18 Zeichen.

## Feld

Die Klammer lebt in einem Feld von 122×152 Pixeln rechts unten (`FIELD_X`, `FIELD_Y` in `draw.py`). Nur dieses Feld wird je
Bild neu gezeichnet. Wer dort etwas anderes zeichnet, wird beim nächsten Bild überschrieben.
