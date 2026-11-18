# Aufbau

Stand: Desktop, Klammer, Startmenü, Apps im Fenster und Agent-Anbindung laufen. Apps und Sprüche kommen mit
`tools/install.ps1` fest aufs Gerät; einen Abruf oder Updates aus dem Netz gibt es bewusst nicht.

## Dateien

Der Ordner `device/` ist ein Abbild dessen, was am Gerät unter `/flash/` liegt.

| Datei | Aufgabe |
|---|---|
| `device/main.py` | Start am Gerät, ruft nur `desktop.run()` |
| `device/clippy/desktop.py` | Hauptschleife: lädt die App-Liste, verteilt Tipper an Symbole, Startmenü und Klammer |
| `device/clippy/shell.py` | Taskleiste, Symbole und Startmenü zeichnen; sagt, was unter dem Finger liegt |
| `device/clippy/logos.py` | Zeichen von Claude (Stern) und Codex (Knoten) für das Desktop-Symbol „Agent“ |
| `device/clippy/launcher.py` | Startet eine App im Fenster, fängt Fehler ab (Bluescreen); Verbinden-, Handbuch- und Abschiedsbild |
| `device/clippy/app_context.py` | `Ctx`: was eine App bekommt (Zeichenfläche, Tipper, Ton, WLAN-Stand, Radio, JSON aus dem Netz, Wetter für den Schirm der Klammer), Vertrag in [build-an-app.md](build-an-app.md) |
| `device/clippy/photo_drop.py` | Fotos vom Handy empfangen (`ctx.photos_from_phone`): QR-Code, kleiner Webserver auf `config.PHOTO_PORT`, schreibt auf die Karte; nur mit der Geheimzahl aus dem QR-Code |
| `device/clippy/request.py` | Teile einer Web-Anfrage lesen: Adresse mit `?a=1`, sicherer Dateiname fürs Foto |
| `device/clippy/photo_page.py` | Die Seite fürs Handy (HTML mit JavaScript): Fotos auswählen, im Handy verkleinern, einzeln schicken |
| `device/clippy/sdcard.py` | microSD-Karte einbinden, wenn eine App sie braucht (`ctx.sd()`), siehe [device.md](device.md) |
| `device/clippy/player.py` | Internetradio über den Player der Firmware; nur http-MP3, siehe [device.md](device.md) |
| `device/clippy/win98.py` | Farben, Schrift und Grundformen: Text, Knopf, 3D-Kante, Fenster, Bluescreen, Empfangsbalken, Schloss |
| `device/clippy/config.py` | Einstellungen an einer Stelle: Adresse des Handbuchs, Ablageort der Apps, WLAN-Datei, Port für Agents |
| `device/clippy/wifi.py` | WLAN: beim Start verbinden, ohne zu warten; Netze suchen, verbinden, Zugang speichern |
| `device/clippy/wifi_setup.py` | „WLAN einrichten“ aus dem Startmenü: Netz wählen, Passwort eingeben, verbinden |
| `device/clippy/keyboard.py` | Bildschirm-Tastatur für Texteingaben |
| `device/clippy/monitor.py` | Fenster „Agent-Nutzung“: was der Agent tut, bei Claude Code die Limits; die Klammer bleibt daneben sichtbar |
| `device/clippy/agent_hooks/` | Nimmt die Hook-Meldungen der Coding-Agents an (Webserver) und wertet sie je Agent aus, siehe [agent-hooks.md](agent-hooks.md) |
| `device/clippy/wifi_portal.py` | WLAN einrichten mit dem Handy: eigenes WLAN, QR-Codes, kleiner Web- und Namensserver |
| `device/clippy/portal_page.py` | Die Einrichtungsseite fürs Handy (HTML) und das Auslesen des Formulars |
| `device/clippy/pet/` | Die Klammer, siehe [pet.md](pet.md) |
| `device/res/` | Schriften |
| `tools/preview.py` | Zeichnet ein Geräte-Skript am PC in ein PNG, ohne Gerät |
| `tools/screenshots.py` | Bilder fürs Handbuch (`manual/img/`) mit der Vorschau; läuft beim Veröffentlichen, siehe [manual.md](manual.md) |
| `checks/` | Prüfskripte, die einzeln am Gerät laufen (Sensoren, Netz, Zeichentempo) |
| `tests/` | Selbsttests am PC: `python tests/test_<name>.py` |

Importiert wird immer vom Paket aus, z. B. `from clippy import win98` oder `from clippy.pet import moves`.

## Bildschirm (320×240)

```
 0 ┌───────────────────────┬──────────────┐
   │ [Symbol] ┌──────────┐ │ [Konsole]    │   Symbole: Spalte links, je 68×50, höchstens vier
   │ [Symbol] │ Agent-   │ │──────────────│   Feld der Klammer: 122×212 bei x=198, y=0; oben 60 Luft
   │          │ Nutzung  │ │   Klammer    │   (Sprünge, Konsole, wenn ein Agent arbeitet)
   │          └──────────┘ │              │   Fenster „Agent-Nutzung“: 194×206 bei x=2, y=2
212├───────────────────────┴──────────────┤
   │ [Start]    [Cl][Co] [Akku % WLAN 20:36]│  Taskleiste: 28 hoch; Kästchen je Coding-Agent; WLAN-Zeichen nur, wenn verbunden
240└──────────────────────────────────────┘
```

Tippflächen sind mindestens 40 Pixel hoch: Der Start-Knopf reagiert schon ab y=200, auch wenn er kleiner
gezeichnet ist. Das X eines Fensters reagiert in der ganzen Ecke rechts oben (48×40).

## Wer bekommt den Tipper?

Am Desktop: Symbol-Spalte und Start-Knopf gehören `desktop.py`, das Feld der Klammer gehört ihren Sinnen
(`pet/senses.py`). In einer bildschirmfüllenden App liest nur `ctx.update()` die Berührung; in einer App neben der Klammer
(`beside`, Fenster 196×212 ab x=0, y=0) bekommt die App nur Tipper ins Fenster, die Klammer ihr Feld. Startmenü und Meldungsfenster
warten mit `launcher.wait_tap()` auf den nächsten Tipper; solange ruht die Klammer.

## Symbol „Agent“ und Fenster „Agent-Nutzung“

Eingebautes Symbol „Agent“ am Desktop (nach den Apps aus `manifest.json`, zählt zu den höchstens vier). Es zeigt
das Zeichen des Agents, der gerade dran ist (`agents.current()`: wer sich zuletzt gemeldet hat, sonst wer
Nutzungszahlen geschickt hat): der Stern von Claude, der Knoten von Codex (`logos.py`, aus Grundformen gezeichnet);
Copilot und „noch keiner“ bekommen das Prozentzeichen. Wechselt der Agent, zeichnet `desktop.py` das Symbol neu.
Antippen öffnet ein Fenster links (`monitor.py`, 194×206 ab x=2, y=2), das die Klammer rechts frei lässt: Sie lebt
weiter, redet und reagiert. Inhalt: oben der Agent, rechts daneben wie alt seine Zahlen sind, darunter was er tut
(„arbeitet grad an Clippy“, „wartet auf di“, „is fertig“). Für Claude Code folgen die Limits wie in der
Windows-98-Ressourcenanzeige: Balken für 5 Stunden und Woche (mit Uhrzeit, wann es zurückgesetzt wird); nur im
Terminal (Statuszeile) dazu Modell, Kosten der Sitzung und Zeilen +/−. Ab 80 % ist ein Balken rot. Codex und Copilot
geben keine Limits heraus, das steht dann dort. Ohne Agent steht dort, wie man einen verbindet (Startmenü →
„Mit PC verbinden“). Spricht die Klammer, liegt ihre Sprechblase über dem Fenster; sonst zeichnet sich das Fenster
jede Sekunde neu, damit ist danach auch wieder weg, was Sprechblase oder Sturz-Bühne darübergemalt haben. X schließt es. Daten: [agent-hooks.md](agent-hooks.md) „Nutzung und Limits“.

## Uhr

Sobald das WLAN steht, stellt Clippy einmal die Uhr (`wifi.sync_clock`, NTP, `pool.ntp.org`); die Zeitzone ist
seit dem Start Mitteleuropa. Ohne WLAN steht die Uhr nach jedem Einschalten auf 1. Jänner 1970 (die Nacht-Regeln
der Klammer greifen dann nicht, siehe `senses.py`).

## Startmenü

Einträge stehen in `desktop.MENU`, ausgeführt werden sie in `desktop.start_menu`. „Handbuch“ zeigt die Adresse
aus `config.MANUAL_URL` als QR-Code. „Beenden“ schaltet nur das Display aus, bis man es antippt.

Einträge: „WLAN einrichten“, „Mit PC verbinden“, „Handbuch“, „Beenden“. „Mit PC verbinden“
(`launcher.show_connect`) zeigt den Satz für den Coding-Agent (`config.CONNECT_SENTENCE`) und, ob Clippy im WLAN ist
(siehe [agent-hooks.md](agent-hooks.md)).

„WLAN einrichten“ (`wifi_setup.py`) läuft im selben Fensterrahmen wie eine App (`launcher.run_builtin`, X schließt):

1. Zeigt, womit Clippy gerade verbunden ist, sucht Netze und listet sie nach Empfang, fünf je Seite
   (Balken = Empfang, Schloss = mit Passwort). „Neu suchen“ sucht nochmal.
2. Netz antippen → Passwort über die Bildschirm-Tastatur (`keyboard.py`): Seite mit Buchstaben und Ziffern,
   `aA` schaltet Groß-/Kleinschreibung, `#+=` die Seite mit Sonderzeichen, `<-` löscht. Offene Netze ohne Passwort.
3. Verbindet bis zu 20 s. Klappt es, speichert es Netz und Passwort in `/flash/wifi.json` und zeigt Adresse und
   `clippy.local`. Klappt es nicht, bleibt die alte Datei, Clippy verbindet sich wieder mit dem alten Netz, und man
   kann das Passwort nochmal eingeben.

Nur ASCII-Zeichen sind auf der Tastatur; ein Passwort mit Umlauten geht über „Mit Handy“ oder `local/wifi.json`.

**„Mit Handy“** (Knopf in der Netzliste, `wifi_portal.py` und `portal_page.py`):

1. Clippy trennt sich vom bisherigen WLAN und öffnet ein eigenes: `Clippy-Setup`, WPA2, mit einem bei jedem Mal neu
   gewürfelten Passwort aus acht Ziffern. Am Display: QR-Code zum Verbinden (`WIFI:T:WPA;S:...;P:...;;`) und
   darunter Name und Passwort zum Abtippen.
2. Ist ein Handy verbunden, zeigt Clippy stattdessen einen QR-Code mit der Adresse der Einrichtungsseite
   (`http://192.168.4.1/`). Meist geht die Seite schon von selbst auf: Clippy beantwortet jede Namensanfrage
   (DNS, Port 53) mit der eigenen Adresse und liefert auf jede Adresse die Seite aus; Handys halten das für eine
   Anmeldeseite wie im Hotel-WLAN.
3. Die Seite listet die zuvor gefundenen WLANs, dazu ein Feld für ein verstecktes Netz und das Passwort. Nach
   „Verbinden“ schließt Clippy das eigene WLAN und verbindet sich wie oben in Schritt 3; das Ergebnis steht am
   Display, nicht am Handy (das Handy ist dann nicht mehr mit Clippy verbunden).

X am Fenster bricht ab, das eigene WLAN geht zu, Clippy verbindet sich wieder mit dem gespeicherten Netz.

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
python tools/preview.py apps/weather/app.py local/preview.png --online tests/weather_sample.json
```

Eine App, die etwas aus dem Netz holt, sieht am PC sonst nur „Ka WLAN“: Mit `--online <datei.json>` gilt sie als im
WLAN, und jedes `ctx.get_json()` liefert diese Datei.

Die Vorschau ist eine Näherung: Schrift und Kantenglättung weichen vom Gerät ab, Positionen und Farben stimmen.
Sie kennt nur die Zeichenfunktionen, die das Projekt benutzt; fehlt eine, bricht sie mit einer klaren Meldung ab.
