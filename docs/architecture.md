# Aufbau

Stand: Desktop, Klammer, Startmenü, Apps im Fenster und Agent-Anbindung laufen. Der Abruf von Apps folgt.

## Dateien

Der Ordner `device/` ist ein Abbild dessen, was am Gerät unter `/flash/` liegt.

| Datei | Aufgabe |
|---|---|
| `device/main.py` | Start am Gerät, ruft nur `desktop.run()` |
| `device/clippy/desktop.py` | Hauptschleife: lädt die App-Liste, verteilt Tipper an Symbole, Startmenü und Klammer |
| `device/clippy/shell.py` | Taskleiste, Symbole und Startmenü zeichnen; sagt, was unter dem Finger liegt |
| `device/clippy/launcher.py` | Startet eine App im Fenster, fängt Fehler ab (Bluescreen); Handbuch- und Abschiedsbild |
| `device/clippy/win98.py` | Farben, Schrift und Grundformen: Text, Knopf, 3D-Kante, Fenster, Bluescreen |
| `device/clippy/config.py` | Einstellungen an einer Stelle: Adresse des Handbuchs, Ablageort der Apps, WLAN-Datei, Port für Agents |
| `device/clippy/wifi.py` | Verbindet beim Start mit dem WLAN aus `/flash/wifi.json`, ohne zu warten |
| `device/clippy/pet/` | Die Klammer, siehe [pet.md](pet.md) |
| `device/res/` | Schriften |
| `tools/preview.py` | Zeichnet ein Geräte-Skript am PC in ein PNG, ohne Gerät |
| `tools/agent_hook.py`, `tools/agents/` | Hooks der Coding-Agents am PC: Meldung → Zustand → UDP ans Gerät, siehe [agent-hooks.md](agent-hooks.md) |
| `checks/` | Prüfskripte, die einzeln am Gerät laufen (Sensoren, Netz, Zeichentempo) |
| `tests/` | Selbsttests am PC: `python tests/test_<name>.py` |

Importiert wird immer vom Paket aus, z. B. `from clippy import win98` oder `from clippy.pet import moves`.

## Bildschirm (320×240)

```
 0 ┌──────────────────────────────────────┐
   │ [Symbol]                             │   Symbole: Spalte links, je 68×50, höchstens vier
   │ [Symbol]                 ┌─────────┐ │
   │                          │ Klammer │ │   Feld der Klammer: 110×150 bei x=205, y=58
   │                          │         │ │
212├──────────────────────────┴─────────┴─┤
   │ [Start]      [Cl][Co]   [Akku % 20:36]│   Taskleiste: 28 hoch; Kästchen je Coding-Agent links neben der Uhr
240└──────────────────────────────────────┘
```

Tippflächen sind mindestens 40 Pixel hoch: Der Start-Knopf reagiert schon ab y=200, auch wenn er kleiner
gezeichnet ist. Das X eines Fensters reagiert in der ganzen Ecke rechts oben (48×40).

## Wer bekommt den Tipper?

Am Desktop: Symbol-Spalte und Start-Knopf gehören `desktop.py`, das Feld der Klammer gehört ihren Sinnen
(`pet/senses.py`). In einer App liest nur `ctx.update()` die Berührung. Startmenü und Meldungsfenster
warten mit `launcher.wait_tap()` auf den nächsten Tipper; solange ruht die Klammer.

## Startmenü

Einträge stehen in `desktop.MENU`, ausgeführt werden sie in `desktop.start_menu`. „Handbuch“ zeigt die Adresse
aus `config.MANUAL_URL` als QR-Code. „Beenden“ schaltet nur das Display aus, bis man es antippt.

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
