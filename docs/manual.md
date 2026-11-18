# Handbuch (Webseite)

Wer Clippy geschenkt bekommt, soll nachlesen können, was das Gerät alles kann. Dafür gibt es eine kleine statische
Webseite im Stil von 1998, gehostet auf GitHub Pages: **https://paddyblanco.github.io/Clippy/**. Das Startmenü am
Gerät zeigt die Adresse als QR-Code (`config.MANUAL_URL`).

**Regel: Das Handbuch ist immer aktuell.** Jede Änderung, die man am Gerät sieht oder spürt (neue Reaktion, neue
App, neuer Menüeintrag, geänderte Bedienung), kommt im selben Commit ins Handbuch, samt Datum „Zuletzt aktualisiert“
und Eintrag unter „Was ist neu“ auf der Startseite.

## Dateien

| Datei | Inhalt |
|---|---|
| `manual/index.html` | Startseite: Was ist Clippy, Was ist neu, Technische Daten |
| `manual/klammer.html` | Die Büroklammer: was sie von selbst tut, worauf sie reagiert |
| `manual/agents.html` | Claude Code, Codex, Copilot: was die Klammer anzeigt, kurz wie man es einrichtet |
| `manual/hilfe.html` | Bedienung: Tasten, Desktop, Startmenü, Apps; wenn etwas hängt |
| `manual/ideen.html` | App-Ideen für später: Photovoltaik und Wallbox, Units zum Anstecken (nur solche, für die die Firmware Treiber hat), Ideen ohne Zusatzteile |
| `manual/verbinden.html` | Coding-Agents verbinden, für Menschen: der eine Satz, was dabei passiert, wieder entfernen |
| `manual/verbinden.txt` | Anleitung **für den Coding-Agent**, die er auf den Satz hin liest (siehe [agent-hooks.md](agent-hooks.md)) |
| `manual/style.css` | Gemeinsames Aussehen |
| `.github/workflows/manual.yml` | Veröffentlicht `manual/` bei jedem Push auf `main` auf GitHub Pages |

Jede Seite hat dieselbe Navigationsleiste oben; wer eine Seite dazunimmt, trägt sie in allen Seiten ein.

## Stil

- Wie eine private Homepage von 1998: Tabellen-Layout, Serifenschrift, Lauftext (`marquee`), blinkende Hinweise,
  „Optimiert für Netscape Navigator 4.0 bei 800×600“, Trennlinien, Knöpfe im Windows-98-Grau.
- Muss trotzdem am Handy lesbar sein (der QR-Code führt dorthin): Breite höchstens 760 Pixel, darunter fließend.
- Nur eigene Dateien, keine fremden Skripte, Schriften oder Bilder aus dem Netz. Kein JavaScript nötig.
- Sprache: Deutsch, verständlich für Leute ohne Technikwissen. Sprüche der Klammer dürfen oberösterreichisch sein.
- Was eingerichtet werden muss (WLAN, Agents), nur kurz beschreiben und auf die Doku im Repo verlinken.

## Veröffentlichen

Einmalig im Repo auf GitHub: Settings → Pages → Source: „GitHub Actions“. Danach veröffentlicht jeder Push auf `main`
die Seite neu. Ansehen ohne Veröffentlichen: `manual/index.html` im Browser öffnen.

## Screenshots (offen, ganz zum Schluss mit der fertigen Version)

Auf den Seiten stehen bis dahin Platzhalter mit der Nummer aus dieser Liste (`[Bild S1]`).

**Vorher klären:** Bilder sind Binärdateien, und die sind im Repo verboten (AGENTS.md, Regel 4). Entweder eine
Ausnahme für `manual/img/` beschließen, oder die Bilder erst beim Veröffentlichen in GitHub Actions mit
`tools/preview.py` erzeugen (dann ohne das Hintergrundfoto aus `local/bg/`). Echte Fotos vom Gerät gehen nur mit
der Ausnahme.

| Nr. | Seite | Was zu sehen sein soll | Woher |
|---|---|---|---|
| S1 | index | Desktop mit Klammer und Begrüßungs-Sprechblase | Gerät oder Vorschau |
| S2 | index | Foto des Geräts auf dem Schreibtisch | Foto |
| S3 | klammer | Bizepscurls mit Hantel | Vorschau |
| S4 | klammer | Schlagzeug | Vorschau |
| S5 | klammer | Kopfrolle (steht am Kopf) | Vorschau |
| S6 | klammer | Pogo auf dem Drahtende | Vorschau |
| S7 | klammer | rot und grantig (dreimal angetippt) | Vorschau |
| S8 | klammer | gestreichelt, Augen zu | Vorschau |
| S9 | klammer | schlafend mit Zs und Rotzblase, Display gedimmt | Vorschau |
| S10 | klammer | umgefallen, liegt | Vorschau |
| S11 | klammer | Gerät auf dem Kopf: Klammer rollt an ihren Platz | Gerät (Foto/Video-Standbild) |
| S12 | agents | Taskleiste mit drei Agent-Kästchen (gelb, rot, grün) | Vorschau |
| S13 | agents | Klammer ruft „… braucht di!“ mit Sprechblase | Vorschau |
| S14 | hilfe | Startmenü offen | Vorschau |
| S15 | hilfe | Handbuch-Fenster mit QR-Code | Vorschau |
| S16 | hilfe | App „Radio“ im Fenster, ein Sender spielt | Vorschau |
| S18 | hilfe | „Sie können Clippy jetzt ignorieren.“ | Vorschau |
| S19 | hilfe | WLAN einrichten: Liste der Netze | Gerät (echte Netze) |
| S20 | hilfe | WLAN einrichten: Tastatur mit halb eingetipptem Passwort | Vorschau |
| S21 | hilfe | WLAN mit Handy: Clippy zeigt den QR-Code | Gerät (echter QR-Code) |
| S22 | hilfe | WLAN mit Handy: Einrichtungsseite am Handy | Handy-Screenshot |
| S23 | agents | Fenster „Agent-Nutzung“ links, Klammer rechts daneben | Gerät (echte Werte) |
| S24 | hilfe | App „Wetter“ links, Klammer rechts daneben | Gerät (echte Werte) oder Vorschau mit `--online` |
