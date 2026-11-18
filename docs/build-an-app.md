# Eine App bauen

Eine App ist ein Ordner in `apps/` mit einer Datei `app.py` und einem Eintrag in `apps/manifest.json`.
Sie erscheint als Symbol am Desktop und läuft in einem Fenster mit Titelleiste und X.

## In drei Schritten

1. Ordner `apps/<id>/` anlegen, darin `app.py` nach dem Vertrag unten beginnen (`apps/radio/` ist eine fertige App).
2. In `apps/manifest.json` einen Eintrag ergänzen (siehe unten).
3. Am PC ansehen: `python tools/preview.py apps/<id>/app.py local/preview.png`. Dann aufs Gerät bringen mit
   `.\tools\install.ps1` (siehe [device.md](device.md)). Apps kommen nur so aufs Gerät, nie aus dem Netz.

## Der Vertrag

```python
from clippy import win98


def run(ctx):
    while ctx.update():      # False, sobald das Fenster über das X geschlossen wurde
        if ctx.tap:          # (x, y) des Tippers in diesem Durchlauf, sonst None
            ...
        g = ctx.screen       # Zeichenfläche der App
        g.fillScreen(win98.FACE)
        win98.text(g, "Hallo", 10, 10, win98.DARK, win98.FACE)
        ctx.show()           # Zeichenfläche aufs Display bringen
```

| `ctx` | Bedeutung |
|---|---|
| `ctx.update()` | **einmal je Durchlauf aufrufen.** Liest die Berührung, liefert `False` nach dem Schließen. Dann sofort aus `run` zurückkehren |
| `ctx.screen` | Zeichenfläche, `ctx.W` × `ctx.H` = 320 × 218 Pixel, im Fenster neben der Klammer (`beside`) 190 × 188; Nullpunkt links oben unter der Titelleiste |
| `ctx.show()` | bringt die Zeichenfläche aufs Display (kostet rund 30 ms) |
| `ctx.tap` | `(x, y)` in Koordinaten der Zeichenfläche oder `None` |
| `ctx.tone(hz, ms)` | Ton aus dem Lautsprecher; nicht mehr, sobald `play` benutzt wurde |
| `ctx.online()` | `True`, wenn das WLAN steht |
| `ctx.play(url)` | spielt einen MP3-Strom aus dem Netz (nur `http://`, kein https); wartet bis zu 3,5 s, bis er läuft, also vorher anzeigen, dass etwas passiert. `True`, wenn die Firmware ihn angenommen hat |
| `ctx.playing()` | `True`, sobald Daten fließen |
| `ctx.volume(pct=None)` | Lautstärke 0 bis 100 lesen, mit `pct` stellen (100 = voll, je Punkt darunter −0,5 dB, 0 = stumm; Start 40); bleibt bis zum Neustart des Geräts |
| `ctx.stop()` | Musik aus; beim Schließen des Fensters passiert das von selbst |

Mehr bietet `ctx` noch nicht. Was fehlt (Sensoren, Internet, Speichern), kommt dazu, sobald eine App es
braucht, und wird dann hier eingetragen. Nichts verwenden, was hier nicht steht.

## Regeln

- **`ctx.update()` in jeder Schleife.** Eine App, die es nicht aufruft, lässt sich nicht schließen; dann hilft
  nur die Reset-Taste.
- **Die Ecke rechts oben gehört dem X:** Tipper bei x ≥ 272 in den obersten 18 Pixeln der Zeichenfläche
  schließen das Fenster und kommen nicht bei der App an. Im Fenster neben der Klammer liegt das X in der
  Titelleiste, die Zeichenfläche gehört ganz der App.
- **Tippflächen mindestens 40 × 40 Pixel.** Es gibt nur Berührung, keine Tasten.
- **Zeichnen nur auf `ctx.screen`**, Knöpfe und Text mit den Bausteinen aus `clippy/win98.py`
  (`text`, `button`, `bevel`, Farben), damit alles einheitlich aussieht. Text braucht immer die Farbe dahinter.
- **Fehler sind erlaubt:** Wirft die App eine Ausnahme, zeigt das Gerät einen Bluescreen mit der Fehlermeldung
  und kehrt nach einem Tipper zum Desktop zurück.
- Weitere Dateien im App-Ordner darf `app.py` normal importieren (`import helper`).
- Wenig Animation: Ein voller Bildaufbau kostet 30 ms. Nur neu zeichnen, wenn sich etwas geändert hat.

## Manifest

`apps/manifest.json` ist eine Liste. Die Reihenfolge ist die Reihenfolge der Symbole; es passen vier.

```json
{"id": "radio", "name": "Radio", "icon": "FM", "color": "#A03020"}
```

| Feld | Bedeutung |
|---|---|
| `id` | Name des Ordners in `apps/`, klein, ohne Leerzeichen |
| `name` | Text unter dem Symbol und in der Titelleiste, höchstens etwa 9 Zeichen |
| `icon` | zwei Zeichen im Symbol |
| `color` | Farbe des Symbols als `#RRGGBB` |
| `beside` | `true`: Fenster links neben der Klammer (196 × 212 samt Rahmen) statt bildschirmfüllend; weglassen für bildschirmfüllend |

## Während eine App läuft

Das Mikrofon ist aus, damit der Lautsprecher frei ist (beide teilen sich am Gerät eine Leitung). Nach dem
Schließen ist das Radio aus.

- **Bildschirmfüllend:** Die Klammer ist nicht zu sehen und ruht.
- **Neben der Klammer (`beside`):** Sie bleibt rechts sichtbar und lebt weiter, `ctx.update()` lässt sie
  mitlaufen, samt Uhr und Kästchen in der Taskleiste. Tipper auf sie gehen an sie, nicht an die App. Solange
  `ctx.play` Musik liefert, tanzt sie. Damit nichts über das Fenster gemalt wird, redet sie nicht, fällt nicht
  um und rollt nicht; stellt man das Gerät auf den Kopf, dreht sich das Display erst nach dem Schließen. Weil das
  Mikrofon aus ist, reagiert sie nicht auf Klatschen und Klopfen.
