# Aufbau

Stand: Desktop und Klammer laufen. Apps, Abruf und Agent-Anbindung folgen und werden hier ergänzt.

## Dateien

Der Ordner `device/` ist ein Abbild dessen, was am Gerät unter `/flash/` liegt.

| Datei | Aufgabe |
|---|---|
| `device/main.py` | Start am Gerät, ruft nur `desktop.run()` |
| `device/clippy/desktop.py` | Desktop zeichnen, Hauptschleife, Uhr und Akkustand aktuell halten |
| `device/clippy/win98.py` | Farben und Zeichenfunktionen im Windows-98-Stil; sonst zeichnet niemand Knöpfe oder Leisten selbst |
| `device/clippy/pet/` | Die Klammer, siehe [pet.md](pet.md) |
| `device/res/` | Schriften |
| `tools/preview.py` | Zeichnet ein Geräte-Skript am PC in ein PNG, ohne Gerät |
| `checks/` | Prüfskripte, die einzeln am Gerät laufen (Sensoren, Netz, Zeichentempo) |
| `tests/` | Selbsttests am PC: `python tests/test_<name>.py` |

Importiert wird immer vom Paket aus, z. B. `from clippy import win98` oder `from clippy.pet import moves`.

## Bildschirm (320×240)

```
 0 ┌──────────────────────────────────────┐
   │ [Symbol]                             │   Symbole: Spalte links, je 64×60, von oben nach unten
   │ [Symbol]                 ┌─────────┐ │
   │                          │ Klammer │ │   Feld der Klammer: 110×150 bei x=205, y=58
   │                          │         │ │
212├──────────────────────────┴─────────┴─┤
   │ [Start]                 [Akku % 20:36]│   Taskleiste: 28 hoch
240└──────────────────────────────────────┘
```

Tippflächen sind mindestens 40 Pixel hoch: Der Start-Knopf reagiert schon ab y=200, auch wenn er kleiner
gezeichnet ist.

## Zeichnen

- Alle Funktionen in `win98.py` bekommen als erstes Argument das Ziel `g`: das Display (`M5.Display`) oder ein
  Canvas. So lässt sich dasselbe am Gerät und in der Vorschau zeichnen.
- Bewegtes wird in einem kleinen Canvas gezeichnet und dann geschoben; der ganze Bildschirm nur, wenn sich alles
  ändert (Messwerte in [device.md](device.md)).
- Der Hintergrund ist `/flash/bg.jpg`. Fehlt die Datei, ist der Desktop türkis.

## Schrift

Die eingebauten Schriften der Firmware sind ungeglättet und wirken eckig. Das Projekt bringt deshalb zwei eigene
mit: `device/res/font12.vlw` (normal) und `font12b.vlw` (fett), beide DejaVu Sans, 12 Pixel, mit Umlauten.

- Text immer über `win98.text(g, text, x, y, farbe, hintergrund)` zeichnen, nie direkt mit `drawString`.
- **Der Hintergrund muss angegeben werden.** Die Schrift hat weiche Kanten und mischt sie mit dieser Farbe.
- Text direkt auf dem Foto, ohne Kasten: `win98.label(g, text, mitte_x, y)`. Das holt den Bildausschnitt in ein
  kleines Canvas, schreibt weiß mit Schatten darauf und schiebt es zurück; so bleiben die Kanten sauber.
- `win98.backdrop(canvas, x, y)` füllt ein Canvas mit dem Desktop-Ausschnitt an dieser Stelle. Alles, was über
  dem Foto liegt und sich bewegt, beginnt damit.
- Andere Schrift oder Größe: `python tools/make_font.py <schrift.ttf> <pixel> device/res/<name>.vlw`.
  Die Schrift muss frei weitergegeben werden dürfen. Diese beiden Dateien sind die einzigen Binärdateien im Repo.

## Vorschau am PC

```
python -m pip install pillow
python tools/preview.py device/main.py local/preview.png
```

Die Vorschau ist eine Näherung: Schrift und Kantenglättung weichen vom Gerät ab, Positionen und Farben stimmen.
Sie kennt nur die Zeichenfunktionen, die das Projekt benutzt; fehlt eine, bricht sie mit einer klaren Meldung ab.
