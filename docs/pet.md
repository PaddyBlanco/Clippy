# Die Klammer

Code: `device/clippy/pet/`. Sie sitzt rechts unten am Desktop, lebt im Ruhezustand von selbst, reagiert auf ihre Sinne
und spricht in Sprüchen aus `apps/phrases.json`.

## Dateien

| Datei | Aufgabe |
|---|---|
| `draw.py` | Maße der Figur und `draw(g, pose)`: eine Haltung hinein, ein Bild heraus |
| `extras.py` | Beiwerk zur Zeichnung: Hantel, Trommel, Schlägel, Blitze, Rotzblase, Zs |
| `moves.py` | Bewegungen: Blinzeln, Umschauen, Sekundenschlaf, Curls, Trommelschlag, Schwindel, Schreck, ... |
| `boredom.py` | Was sie aus Langeweile tut: Augen verdrehen, strecken, Schlagzeug-Solo, Hanteln, Kopfrolle, Pogo |
| `sleep.py` | Müdigkeit: wann sie einnickt und einschläft, wie hell das Display ist, wie sie im Schlaf aussieht |
| `bubble.py` | Sprechblase samt Zeilenumbruch |
| `senses.py` | Sinne: liest Sensoren, meldet Ereignisse als Wörter |
| `agents.py` | Horcht auf Meldungen der Coding-Agents am PC, merkt sich je Agent den Zustand ([agent-hooks.md](agent-hooks.md)) |
| `touch.py` | Berührung: unterscheidet Antippen von Streicheln |
| `phrases.py` | Wählt zu einem Ereignis einen Spruch |
| `habits.py` | Tabellen zum Einstellen: `IDLE` (was sie von selbst tut, wie oft), `TIRED` (dasselbe im Finstern), `REACT` (Reaktion je Ereignis), Schlafzeiten, Helligkeit |
| `idle.py` | Führt `IDLE` bzw. `TIRED` aus: welche Bewegung sie als Nächstes von selbst macht |
| `tumble.py` | Gerät auf den Kopf gestellt: sie fällt auf den Kopf und rollt an ihren Platz |
| `stage.py` | Zeichnet sie ins Feld oder, solange sie kippt oder rollt, auf die Bühne |
| `pet.py` | Klasse `Pet`: hält alles zusammen und führt die Tabellen aus |

## Wie sie gezeichnet wird

Die Klammer ist keine Bilddatei, sondern wird aus Bögen, Balken und Ellipsen gezeichnet: `draw.draw(g, pose)`.
Eine **Haltung** (`pose`) ist ein Dictionary; `draw.REST` ist die Ruhehaltung.

| Schlüssel | Bedeutung | Ruhe |
|---|---|---|
| `look` | Blickrichtung als (x, y) in Pixeln, etwa −5 bis 5 | (0, 0) |
| `lid` | Augenlid: 0 = offen, 1 = ganz zu (nur ein dunkler Strich); die Pupillen bleiben gleich groß, das Lid schneidet sie ab | 0 |
| `brow` | Brauen: positiv = gehoben, negativ = gesenkt | 0 |
| `frown` | böser Blick: Brauen als schräge Striche, außen hoch, innen tief | False |
| `bob` | ganze Figur nach unten versetzt, in Pixeln; negativ = Sprung nach oben (bis etwa −20) | 0 |
| `stretch` | positiv = sie streckt sich nach oben, negativ = sie staucht sich, in Pixeln | 0 |
| `red` | Draht läuft rot an | False |
| `lean` | Neigung in Grad: positiv nach links um den linken Fuß (88 = liegt), negativ nach rechts um den rechten Fuß (−15 = lehnt am Bildschirmrand) | 0 |
| `roll` | Rolle in Grad um die Mitte der Figur, die dabei am Boden bleibt: 180 = steht am Kopf | 0 |
| `dx` | ganze Figur seitlich versetzt, in Pixeln; Platz ist etwa −10 bis +25 | 0 |
| `arm` | Unterarm (freies Drahtende, rechts) in Grad: 0 = gerade nach oben, 105 = hängt nach außen | 0 |
| `pogo` | freies Drahtende als Pogostick unter der Figur, Länge in Pixeln unter den Füßen; dazu `bob` = −`pogo`, damit der Stick am Boden steht | 0 |
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
| `dark` | Sensor unter dem Display 2 s lang zugehalten (`DARK_MS`) | wird müde, „I siag nix mehr.“: schwere Lider, entspannte Brauen; solange es finster bleibt, blinzelt sie langsam oder die Augen fallen ihr zu und gehen mühsam wieder auf (`TIRED` in `habits.py`) |
| `near` | Hand nähert sich dem Sensor | merkt auf |
| `tap` | Klammer kurz antippen: Finger beginnt und endet auf ihr, wandert kaum. Gilt 0,2 s nach dem Loslassen (`RELEASE_MS`) oder sobald der Finger an derselben Stelle wieder aufsetzt; setzt er binnen 0,2 s woanders auf, war es ein Aussetzer beim Wischen | duckt sich, schüttelt den Kopf |
| `pet` | Finger länger als 0,35 s auf der Klammer lassen, darüber streichen (ab 8 Pixel Weg, `MOVE_PX`) oder von außen hereinwischen; kurzes Berühren bis 1 s nach dem Streicheln zählt noch dazu (alles in `touch.py`) | schließt die Augen und wiegt sich, solange gestreichelt wird |
| `grumpy` | dreimal antippen innerhalb von 5 Sekunden | läuft rot an und droht mit dem Drahtende |
| `loud` | ein einzelnes lautes Geräusch | springt hoch, streckt sich, landet gestaucht |
| `beat` | fünf Schläge binnen 2,5 s (Klopfen aufs Gehäuse oder den Tisch; `BEATS`, `BEAT_MS`), dann jeder weitere | spielt Schlagzeug, ein Schlag je Klopfer, bis 1,5 s Ruhe ist |
| `plugged` | Ladekabel angesteckt | zittert, Blitze; nur einmal beim Anstecken |
| `low_battery` | Akku unter 15 %, alle 5 Minuten | gähnt, hat Hunger |
| `agent_working` | ein Coding-Agent am PC arbeitet ([agent-hooks.md](agent-hooks.md)) | merkt auf, höchstens alle 30 s; solange ein Agent arbeitet, schaut sie gespannt zur Seite |
| `agent_waiting` | ein Agent wartet auf dich; alle 30 s wieder, bis ein neuer Zustand kommt oder du sie antippst | hüpft, winkt, ruft |
| `agent_done` | ein Agent ist fertig | springt vor Freude, reckt das Drahtende |
| `flip` | Gerät auf den Kopf gestellt oder wieder zurück | Desktop dreht sich, sie fällt auf den Kopf und rollt an ihren Platz, siehe „Auf dem Kopf“ |

Dazu ohne Ereignis: Seitliches Kippen lässt die Augen mitrollen. Nachts (23 bis 6 Uhr) hängen die Lider.
Passiert länger nichts, will sie nach 1 Minute beachtet werden (hüpft, winkt), dann ist ihr fad und sie beschäftigt sich alle 15 bis 30 s (`QUIET` und `IDLE` in `habits.py`).
Aus Langeweile schläft sie nicht ein, sondern beschäftigt sich: Augen verdrehen, strecken, Schlagzeug-Solo, Hanteln, auf den Kopf rollen
und zurück, auf dem Drahtende Pogo hüpfen (`boredom.py`, je Mal eines davon zufällig).

**Müde wird sie nur im Finstern und nachts** (`sleep.py`, Zeiten in `habits.py`). Ohne Ereignis schläft sie ein nach 40 s mit zugehaltenem
Sensor (`SLEEP_AFTER_COVERED`), nachts (23 bis 6 Uhr) nach 3 Minuten, in einem dunklen Raum nach 5 Minuten. Nach der halben Zeit nickt sie
einmal ein (Sekundenschlaf: sackt ab, schreckt hoch). Im Schlaf sind die Lider zu, Zs steigen auf und treiben davon. Bei jedem zehnten
Einschlafen bläst sie dabei eine Rotzblase auf (`SNOT_CHANCE`). Jedes Ereignis weckt sie, ebenso wenn es wieder hell wird.

**Helligkeit:** wach `BRIGHT`, solange der Sensor zugehalten ist `DUSK`, im Schlaf `DIM` (alle in `habits.py`).

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
Neben den Ereignissen von oben gibt es `start`, `sleep`, `curl`, `drum`, `attention`, `bored`, `nod` und `fall`.
In den Sprüchen zu `agent_*` steht `{agent}` für den Namen des Agents („Claude“, „Codex“, „Copilot“).

## Sprechblase

`clippy.say("Text", seconds=6)` zeigt eine gelbe Sprechblase links neben dem Kopf, bricht den Text selbst um und
räumt sie nach der Zeit wieder weg. `clippy.hush()` entfernt sie sofort. Platz ist für etwa sechs Zeilen zu je
rund 18 Zeichen.

## Feld

Die Klammer lebt in einem Feld von 122×176 Pixeln rechts unten (`FIELD_X`, `FIELD_Y` in `draw.py`).
Beim Umfallen nach links (`lean` größer 0) und beim Rollen (`roll`) zeichnet sie auf der Bühne: ein Streifen in
Feldhöhe über die ganze Breite (`STAGE_W`, `stage.py`). Als Hintergrund dient der ganze Desktop samt Symbolen,
den `desktop.draw` einmal in eine eigene Leinwand malt; die Sprechblase wird dafür weggeräumt. Nur Feld bzw. Bühne
werden je Bild neu gezeichnet. Wer dort etwas anderes zeichnet, wird beim nächsten Bild überschrieben.

## Auf dem Kopf

Steht das Gerät 0,6 s lang auf dem Kopf (`FLIP_G`, `FLIP_MS` in `senses.py`), meldet `senses.py` das Ereignis
`flip`, ebenso beim Zurückdrehen. Die Klammer dreht dann das Display um 180° (`setRotation`), lässt den Desktop
neu zeichnen und spielt `tumble.py`: Sie hängt dort, wo sie vor dem Drehen war (jetzt links oben, verkehrt herum),
fällt auf den Kopf, rollt nach rechts an ihren Platz, läuft dabei rot an und beschwert sich danach (`flip` in
`apps/phrases.json`). Die Augen rollen beim Kippen auch umgedreht in die richtige Richtung.
