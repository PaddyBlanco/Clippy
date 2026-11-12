# Die Klammer

Code: `device/clippy/pet/`. Sie sitzt rechts unten am Desktop, lebt im Ruhezustand von selbst, reagiert auf ihre Sinne
und spricht in Sprüchen aus `apps/phrases.json`.

## Dateien

| Datei | Aufgabe |
|---|---|
| `draw.py` | Maße der Figur und `draw(g, pose)`: eine Haltung hinein, ein Bild heraus |
| `moves.py` | Bewegungen: Blinzeln, Umschauen, Langeweile, Sekundenschlaf, Curls, Trommelschlag, Schwindel, Schreck, ... |
| `bubble.py` | Sprechblase samt Zeilenumbruch |
| `senses.py` | Sinne: liest Sensoren, meldet Ereignisse als Wörter |
| `phrases.py` | Wählt zu einem Ereignis einen Spruch |
| `habits.py` | Tabellen zum Einstellen: `IDLE` (was sie von selbst tut, wie oft), `REACT` (Reaktion je Ereignis), Schlafzeiten, Helligkeit |
| `pet.py` | Klasse `Pet`: hält alles zusammen und führt die Tabellen aus |

## Wie sie gezeichnet wird

Die Klammer ist keine Bilddatei, sondern wird aus Bögen, Balken und Ellipsen gezeichnet: `draw.draw(g, pose)`.
Eine **Haltung** (`pose`) ist ein Dictionary; `draw.REST` ist die Ruhehaltung.

| Schlüssel | Bedeutung | Ruhe |
|---|---|---|
| `look` | Blickrichtung als (x, y) in Pixeln, etwa −5 bis 5 | (0, 0) |
| `lid` | Augenlid: 0 = offen, 1 = zu | 0 |
| `brow` | Brauen: positiv = gehoben, negativ = gesenkt | 0 |
| `bob` | ganze Figur nach unten versetzt, in Pixeln; negativ = Sprung nach oben (bis etwa −20) | 0 |
| `stretch` | positiv = sie streckt sich nach oben, negativ = sie staucht sich, in Pixeln | 0 |
| `red` | Draht läuft rot an | False |
| `lean` | Neigung nach links in Grad, um den linken Fuß: 0 = steht, 88 = liegt | 0 |
| `arm` | Unterarm (freies Drahtende, rechts) in Grad: 0 = gerade nach oben, 105 = hängt nach außen | 0 |
| `weight` | Hantel in der Hand | False |
| `stick` | Schlägel in der Hand | False |
| `drum` | Trommel rechts unten | False |
| `spark` | Blitze rund um die Figur („unter Strom“) | False |
| `zzz` | Schlaf-Zs: 0 = keine, sonst ein Zähler; mit jedem Schritt steigen die drei Zs weiter auf und treiben davon | 0 |
| `snot` | Radius der Rotzblase in Pixeln, 0 = keine | 0 |

Alle Maße stehen als Konstanten oben in `draw.py` (`ARCS`, `STICKS`, `EYES`, ...). Ein Bild kostet am Gerät 20 ms.

## Neue Bewegung

Eine Bewegung ist eine Funktion in `moves.py`, die Bild für Bild eine Haltung liefert. Beispiel:

```python
def blink():
    for lid in (0.5, 1.0, 1.0, 0.5):
        yield dict(REST, lid=lid)
```

- Sofort abspielen: `clippy.play(moves.blink)`.
- Von selbst im Ruhezustand: in `habits.py` bei `IDLE` eintragen (erstes Mal nach, danach Pause von–bis,
  alles in Millisekunden). Soll sie manchmal etwas dazu sagen: zusätzlich bei `SPOKEN`.
- Das Tempo gibt die Hauptschleife in `device/clippy/desktop.py` vor: etwa 12 Bilder pro Sekunde.

Ansehen ohne Gerät: `python tools/preview.py device/main.py local/preview.png 200`. Die letzte Zahl ist die
Anzahl der Schleifendurchläufe; so lässt sich ein bestimmter Moment einer Bewegung festhalten.

## Sinne und Reaktionen

`senses.py` übersetzt Sensorwerte in Ereignisse, `habits.py` ordnet jedem Ereignis in `REACT` eine Bewegung zu.
Der Spruch dazu kommt aus `apps/phrases.json` unter demselben Namen.

| Ereignis | Auslöser | Reaktion |
|---|---|---|
| `shake` | Gerät schütteln | Augen kreisen, sie schwankt; in etwa einem Drittel der Fälle fällt sie um (`SOMETIMES`) |
| `face_down` | Sensor unter dem Display zugehalten | läuft rot an, „finster“ |
| `near` | Hand nähert sich dem Sensor | merkt auf |
| `tap` | Klammer kurz antippen | duckt sich, schüttelt den Kopf |
| `pet` | Finger länger als 0,35 s auf der Klammer lassen oder darüber streichen | schließt die Augen und wiegt sich, solange gestreichelt wird |
| `grumpy` | dreimal antippen innerhalb von 5 Sekunden | läuft rot an und droht mit dem Drahtende |
| `loud` | ein einzelnes lautes Geräusch | springt hoch, streckt sich, landet gestaucht |
| `beat` | drei Schläge binnen 1,5 s (Klopfen aufs Gehäuse oder den Tisch), dann jeder weitere | spielt Schlagzeug, ein Schlag je Klopfer, bis 1,5 s Ruhe ist |
| `plugged` | Ladekabel angesteckt | zittert, Blitze; danach alle 20 bis 40 s wieder, solange sie lädt |
| `low_battery` | Akku unter 15 %, alle 5 Minuten | gähnt, hat Hunger |

Dazu ohne Ereignis: Seitliches Kippen lässt die Augen mitrollen. Nachts (23 bis 6 Uhr) hängen die Lider.
Passiert länger nichts, wird sie stufenweise müde: nach 2 Minuten Langeweile, nach 3,5 Minuten
Sekundenschlaf (`QUIET` in `habits.py`). Ist es dunkel oder Nacht und passiert 5 bzw. 3 Minuten nichts, schläft sie ein: Lider zu, Zs steigen auf
und treiben davon, das Display dimmt. Bei jedem zehnten Einschlafen bläst sie dabei eine Rotzblase auf (`SNOT_CHANCE`). Jedes Ereignis weckt sie.

Die Schwellen stehen als Konstanten oben in `senses.py` und sind am Gerät gemessen
(Annäherung frei 0–6, Finger drauf ca. 300; Mikrofon leise bis ca. 500, Klatschen bis 32767).
Die Klopf-Schwelle `KNOCK` ist geschätzt, nicht gemessen.

**Neue Reaktion:** Ereignis in `senses.py` melden, Bewegung in `moves.py` schreiben, beides in `REACT`
eintragen, Sprüche unter dem Ereignisnamen in `apps/phrases.json` ergänzen.

**Ton:** Solange die Klammer lauscht, ist der Lautsprecher aus; Mikrofon und Lautsprecher teilen sich am Gerät
eine Leitung. Wer Ton ausgeben will, muss das Mikrofon vorher beenden (`M5.Mic.end()`, `M5.Speaker.begin()`).

## Sprüche

`apps/phrases.json`: je Ereignis eine Liste, daraus wird zufällig gewählt. Oberösterreichisch. Der Satzbau
„Schaut aus, ois dadst ...“ ist das Markenzeichen, soll aber selten bleiben (ein bis zwei Sprüche), sonst
wirkt es eintönig. Höchstens etwa 100 Zeichen, sonst passt es nicht in die Blase. Erlaubt sind die
Zeichen der Geräte-Schrift: ASCII, Umlaute, ß und einige Satzzeichen (siehe `tools/make_font.py`).
Neben den Ereignissen von oben gibt es `start`, `sleep`, `curl`, `drum`, `bored`, `nod` und `fall`.

## Sprechblase

`clippy.say("Text", seconds=6)` zeigt eine gelbe Sprechblase links neben dem Kopf, bricht den Text selbst um und
räumt sie nach der Zeit wieder weg. `clippy.hush()` entfernt sie sofort. Platz ist für etwa sechs Zeilen zu je
rund 18 Zeichen.

## Feld

Die Klammer lebt in einem Feld von 122×176 Pixeln rechts unten (`FIELD_X`, `FIELD_Y` in `draw.py`).
Nur beim Umfallen (`lean` ungleich 0) zeichnet sie auf einer breiteren Bühne (`STAGE_W`), die bis an die
Symbol-Spalte reicht; die Sprechblase wird dafür weggeräumt. Nur dieses Feld wird je
Bild neu gezeichnet. Wer dort etwas anderes zeichnet, wird beim nächsten Bild überschrieben.
