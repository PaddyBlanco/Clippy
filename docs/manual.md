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
| `manual/bilder.html` | Werkzeug für den Weg über den Kartenleser (der einfache Weg ist Fotos vom Handy in der Diashow): Fotos im Browser auf Clippy-Größe bringen (320 × 218, normales JPEG) und auf die Karte speichern oder als ZIP herunterladen; für die App Diashow |
| `manual/verbinden.html` | Coding-Agents verbinden, für Menschen: der eine Satz, was dabei passiert, wieder entfernen |
| `manual/verbinden.txt` | Anleitung **für den Coding-Agent**, die er auf den Satz hin liest (siehe [agent-hooks.md](agent-hooks.md)) |
| `manual/style.css` | Gemeinsames Aussehen |
| `.github/workflows/manual.yml` | Veröffentlicht `manual/` bei jedem Push auf `main` auf GitHub Pages |

Jede Seite hat dieselbe Navigationsleiste oben; wer eine Seite dazunimmt, trägt sie in allen Seiten ein.

## Stil

- Wie eine private Homepage von 1998: Tabellen-Layout, Serifenschrift, Lauftext (`marquee`), blinkende Hinweise,
  „Optimiert für Netscape Navigator 4.0 bei 800×600“, Trennlinien, Knöpfe im Windows-98-Grau.
- Muss trotzdem am Handy lesbar sein (der QR-Code führt dorthin): Breite höchstens 760 Pixel, darunter fließend.
- Nur eigene Dateien, keine fremden Skripte, Schriften oder Bilder aus dem Netz. Kein JavaScript nötig, außer auf
  `bilder.html`: Das Verkleinern läuft im Browser, die Fotos verlassen dabei den Rechner nicht.
- Sprache: Deutsch, verständlich für Leute ohne Technikwissen. Sprüche der Klammer dürfen oberösterreichisch sein.
- Was eingerichtet werden muss (WLAN, Agents), nur kurz beschreiben und auf die Doku im Repo verlinken.

## Veröffentlichen

Einmalig im Repo auf GitHub: Settings → Pages → Source: „GitHub Actions“. Danach veröffentlicht jeder Push auf `main`
die Seite neu. Ansehen ohne Veröffentlichen: `manual/index.html` im Browser öffnen.

## Bilder vom Gerät

Die Bilder entstehen erst beim Veröffentlichen: `.github/workflows/manual.yml` ruft `tools/screenshots.py` auf und
legt sie als `manual/img/s<Nr>.png` ab. Im Repo liegen sie nie (AGENTS.md, Regel 4; `manual/img/` steht in
`.gitignore`), ohne Hintergrundfoto aus `local/bg/`. Ansehen am PC: `python tools/screenshots.py`, dann
`manual/index.html` öffnen. Auf der Seite: `<img class="pic" src="img/s<Nr>.png" ...>`, mehrere nebeneinander in
`<div class="gallery">` mit `<figure>`.

Drei Wege, je nach Bild:

- **Vorschau** (`tools/preview.py`): Desktop, Klammer, Menüs, Apps. Eine Szene ist ein Eintrag in `SCENES` in
  `tools/screenshot_scenes.py`. QR-Codes sind echt, wenn das Paket `qrcode` da ist (in Actions immer). Was nur das
  Gerät weiß (WLAN-Liste, Nutzungszahlen, Adresse im WLAN), ist in der Szene erfunden, sieht aber genauso aus.
- **Handy-Seiten**: Headless Chrome fotografiert die Seiten aus `portal_page.py` und `photo_page.py` in Handy-Größe
  (`tools/screenshot_extras.py`). In Actions ist Chrome dabei; fehlt er am PC, fehlen nur diese Bilder.
- **Gerät** (S2): Pillow zeichnet ein CoreS3-Gehäuse und setzt S1 als Bildschirm hinein. Ein echtes Foto bräuchte
  eine Ausnahme von Regel 4.

| Nr. | Seite | Was zu sehen ist | Woher |
|---|---|---|---|
| S1 | (Grundlage für S2) | Desktop mit Klammer und Begrüßungs-Sprechblase | Vorschau: `device/main.py` |
| S2 | index | Das Gerät mit dem Desktop | gezeichnet |
| S3 | klammer | Bizepscurls mit Hantel | Vorschau |
| S4 | klammer | Schlagzeug | Vorschau |
| S5 | klammer | Kopfrolle (steht am Kopf) | Vorschau |
| S6 | klammer | Pogo auf dem Drahtende | Vorschau |
| S7 | klammer | rot und grantig (dreimal angetippt) | Vorschau |
| S8 | klammer | gestreichelt, Augen zu | Vorschau |
| S9 | klammer | schlafend mit Zs und Rotzblase, Display gedimmt | Vorschau |
| S10 | klammer | umgefallen, liegt | Vorschau |
| S11 | klammer | Gerät auf dem Kopf: Klammer hängt verkehrt, gleich fällt sie | Vorschau |
| S12 | agents | Taskleiste mit drei Agent-Kästchen (gelb, rot, grün) | Vorschau |
| S13 | agents | Klammer ruft „… braucht di!“ mit Sprechblase | Vorschau |
| S14 | hilfe | Startmenü offen | Vorschau |
| S15 | hilfe | Handbuch-Fenster mit QR-Code | Vorschau |
| S16 | hilfe | App „Radio“ im Fenster, ein Sender spielt | Vorschau |
| S18 | hilfe | „Sie können Clippy jetzt ignorieren.“ | Vorschau |
| S19 | hilfe | WLAN einrichten: Liste der Netze | Vorschau, Netze erfunden |
| S20 | hilfe | WLAN einrichten: Tastatur mit halb eingetipptem Passwort | Vorschau |
| S21 | hilfe | WLAN mit Handy: Clippy zeigt den QR-Code | Vorschau |
| S22 | hilfe | WLAN mit Handy: Einrichtungsseite am Handy | Chrome |
| S23 | agents | Fenster „Agent-Nutzung“ links, Klammer rechts daneben | Vorschau, Zahlen erfunden |
| S24 | hilfe | App „Wetter“ links, Klammer mit Schirm rechts daneben | Vorschau mit `tests/weather_sample.json` |
| S25 | hilfe | App „Diashow“ mit einem Foto | Vorschau mit `--sd` |
| S26 | hilfe | Diashow: QR-Code „Fotos vom Handy“, Scho do: 3 | Vorschau |
| S27 | hilfe | Handy: Seite „Fotos an Clippy“ mit drei geschickten Fotos | Chrome |
