# Clippy: Hinweise für Coding-Agents

Ein M5Stack CoreS3 (320×240, nur Touch) mit MicroPython (UIFlow2-Firmware). Die Oberfläche sieht aus wie
Windows 98; am Desktop sitzt eine Büroklammer, die auf Sensoren und auf Coding-Agents am PC reagiert.

**Ziel: ein Geschenk.** Clippy wird verschenkt. Wer es bekommt, soll so wenig wie möglich einrichten müssen;
was doch nötig ist, muss ohne Technikwissen in wenigen Schritten gehen (am Gerät antippen, QR-Code scannen,
einen Satz kopieren). Nichts darf voraussetzen, dass am PC Python, dieses Repo oder Entwicklerwerkzeuge da sind. Am PC wird nur
Windows unterstützt.

**Stand: im Aufbau.** Einträge mit „folgt“ gibt es noch nicht. Erfinde keine Schnittstellen, die hier nicht
dokumentiert sind; lies die genannte Datei oder frag nach.

## Feste Regeln

1. **Doku zuerst.** Erst die passende Datei in `docs/` anpassen, dann den Code.
2. **So einfach wie möglich, kleine Dateien.** Eine Datei hat eine Aufgabe und bleibt unter etwa 150 Zeilen;
   wird sie größer oder bekommt eine zweite Aufgabe, wird sie geteilt. Keine Abstraktion auf Vorrat.
   Namen: Ordner und Dateien klein, Python mit Unterstrich (`make_font.py`), Doku mit Bindestrich, keine Abkürzungen.
3. **Tabu am Gerät:** keine eFuses, kein `M5.Power.setCharge*`, `setExtOutput`, `setUsbOutput`.
   Begründung in [docs/device.md](docs/device.md).
4. **Keine Secrets und keine Binärdateien im Repo.** Lokales (WLAN-Daten, Bilder, Firmware) liegt in `local/`
   oder ist per `.gitignore` ausgeschlossen. Einzige Ausnahme: die Geräte-Schriften in `device/res/`.
5. **Sprache:** Doku Deutsch, Code und Dateinamen Englisch, Texte am Gerät oberösterreichisch.
6. **Testen:** zuerst am PC mit `tools/preview.py` und `tests/`, dann am Gerät mit `tools/install.ps1`
   (kopiert alles und startet neu). Einzelne Prüfskripte aus `checks/` laufen mit `mpremote ... resume run`.
   Das Hauptprogramm nie so starten; Grund in [docs/device.md](docs/device.md).

7. **Saubere Git-Historie.** Ein Commit je abgeschlossenem, getestetem Schritt; Doku und Code dazu im selben
   Commit. Betreff auf Deutsch, höchstens 60 Zeichen, sagt was sich für den Nutzer ändert
   (z. B. „Klammer blinzelt und spricht“). Keine „fix“- oder „wip“-Commits; Korrekturen vor dem Hochladen
   in den passenden Commit einarbeiten. Nach dem Hochladen wird nichts mehr umgeschrieben.

8. **Handbuch immer aktuell.** Was man am Gerät sieht oder bedient, steht im Handbuch `manual/` (Webseite für
   Beschenkte). Neue oder geänderte Funktion → Handbuch im selben Commit nachziehen. Siehe [docs/manual.md](docs/manual.md).

## Aufgabe → lies diese Datei

| Aufgabe | Datei |
|---|---|
| Mit dem Gerät verbinden, flashen, retten, Hardware-Fakten | [docs/device.md](docs/device.md) |
| Pins, I2C-Adressen, Chips, Hersteller-Quellen | [docs/hardware.md](docs/hardware.md) |
| Neue App bauen | [docs/build-an-app.md](docs/build-an-app.md) |
| Klammer: Zeichnung, Bewegungen, Sinne und Reaktionen, Sprüche | [docs/pet.md](docs/pet.md) |
| Klammer am Gerät durchtesten | [docs/pet-checklist.md](docs/pet-checklist.md) |
| Claude Code / Codex / Copilot mit der Klammer verbinden | [docs/agent-hooks.md](docs/agent-hooks.md) |
| Überblick, Bildschirmaufteilung, Zeichnen, Schrift, Vorschau am PC | [docs/architecture.md](docs/architecture.md) |
| Handbuch (Webseite für Beschenkte) pflegen und veröffentlichen | [docs/manual.md](docs/manual.md) |
| Ideen für weitere Apps | [manual/ideen.html](manual/ideen.html) (Handbuch-Seite) |
| Code vereinfachen lassen (Subagent, ohne Verhalten zu ändern) | [.claude/agents/code-simplifier.md](.claude/agents/code-simplifier.md) |

## Ordner

| Ordner | Inhalt |
|---|---|
| `apps/` | `manifest.json` (App-Liste), `phrases.json` (Sprüche der Klammer) und je App ein Ordner mit `app.py`; kommt mit `tools/install.ps1` aufs Gerät, einen Abruf aus dem Netz gibt es bewusst nicht |
| `device/` | Abbild des Geräts: `main.py`, Paket `clippy/` (Desktop, Startmenü, App-Starter, Windows-98-Bausteine, Klammer), `res/` |
| `tools/` | Skripte für den PC: aufs Gerät installieren, Vorschau ohne Gerät, Hintergrundbild und Schrift erzeugen |
| `checks/` | Prüfskripte, die einzeln am Gerät laufen |
| `tests/` | Selbsttests am PC |
| `local/` | Nicht im Repo: WLAN-Daten, Bilder, Firmware-Abbild, heruntergeladene Unterlagen |
| `docs/` | Doku, je Aufgabe eine Datei |
| `manual/` | Handbuch als Webseite (GitHub Pages), siehe [docs/manual.md](docs/manual.md) |
