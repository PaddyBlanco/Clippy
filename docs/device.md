# Gerät: Fakten, Verbinden, Retten

Alles hier wurde am echten Gerät geprüft, außer wo „ungetestet“ steht.

## Hardware (M5Stack CoreS3)

| Teil | Zugriff in MicroPython | Stand |
|---|---|---|
| Display 320×240 | `M5.Display` (Formen, Bögen, Text, PNG/JPG, QR-Code). Drehung `setRotation`: 0 = normal, 2 = auf dem Kopf | geprüft (`checks/orientation.py`) |
| Touch | `M5.Touch` (`getCount`, `getX`, `getY`, `getDetail`); die Koordinaten folgen der Display-Drehung | geprüft |
| Bewegung, Kompass | `M5.Imu` (`getAccel`, `getGyro`, `getMag`). Schwerkraft in `getAccel()`: normal hingestellt y ≈ +1, auf dem Kopf y ≈ −1, flach liegend z ≈ ±1 | geprüft (`checks/orientation.py`) |
| Lautsprecher | `M5.Speaker` (`tone`, `playWav`, `playWavFile`) | geprüft |
| Mikrofon | `M5.Mic` (`record`, `recordWavFile`); vorher `M5.Speaker.end()`, beide teilen sich die Leitung | geprüft |
| Annäherung | `M5.Als.getProximitySensorData()`, in der Schleife `M5.update()` aufrufen. Sitzt im Streifen unter dem Display | geprüft: frei 0–6, Finger drauf ca. 300 |
| Licht | `M5.Als.getLightSensorData()` | liefert bei Abendlicht nur 0–5; bei Tageslicht ungetestet |
| Akku, Strom | `M5.Power` (`getBatteryLevel`, `getBatteryVoltage`, `isCharging`, `lightSleep`, ...) | geprüft; direkt nach dem Flashen kamen falsche Werte (0 %), nach Ab- und Anstecken des Kabels stimmten sie |
| Kamera | Modul `camera` | ungetestet |
| WLAN | Modul `network`, nur 2,4 GHz | Scan geprüft |
| Uhr | `machine.RTC()` oder `time.localtime()`; nicht als `M5.Rtc` vorhanden | läuft, steht nach dem Einschalten auf 1.1.1970 (Unix-Zeit ab 1970), bis sie gestellt wird; Clippy stellt sie per NTP, sobald das WLAN steht |

Firmware: UIFlow2 v2.5.4, MicroPython 1.27. Frei: ca. 8 MB Arbeitsspeicher, ca. 4,6 MB Dateisystem (`/flash`).
Schriften: `M5.Display.FONTS` enthält u. a. `DejaVu9` bis `DejaVu72` und `Montserrat12` bis `Montserrat48`.

**Nicht `import hardware` verwenden:** Der Aufruf blieb auf diesem Gerät hängen.

Pins, Adressen und Quellen: [hardware.md](hardware.md).

## Zeichengeschwindigkeit (gemessen mit `checks/bench.py`)

| Was | Zeit je Bild | Bilder pro Sekunde |
|---|---|---|
| Figur (ca. 110×150) über ein kleines Canvas (`newCanvas` + `push`) | 11 ms | ca. 90 |
| Figur direkt aufs Display (flackert) | 13 ms | ca. 78 |
| Ganzen Bildschirm neu schieben (320×240) | 31 ms | ca. 32 |

Folgerung: Bewegtes in einem kleinen Feld über ein Canvas zeichnen. Den ganzen Bildschirm nur neu zeichnen,
wenn sich wirklich alles ändert.

## Verbinden (Windows)

Einmalig: Python installieren, dann `python -m pip install esptool mpremote`.

```
python -m mpremote connect list
python -m mpremote connect COM6 resume run checks/hello.py
```

- Der Port heißt im Normalbetrieb anders als im Flash-Modus (hier: COM6 bzw. COM5). `connect list` zeigt ihn.
- **Immer `resume` angeben.** Ohne startet die UIFlow-Oberfläche neu und die Verbindung scheitert.
- **Keinen Python-Code direkt in der PowerShell-Befehlszeile übergeben**; Windows PowerShell entfernt die
  Anführungszeichen. Code in eine Datei schreiben und mit `run` starten.
- `run` lädt die Datei nur in den Arbeitsspeicher. Nach einem Neustart ist das Gerät wie vorher.

Prüfskripte: `checks/hello.py` (Text am Display), `checks/inventory.py` (listet Module und fragt Sensoren ab).

## Netz (gemessen mit `checks/nettest.py`)

- Clippy verbindet sich beim Start selbst (`device/clippy/wifi.py`) mit den Daten aus `/flash/wifi.json`
  (`{"ssid": ..., "password": ...}`). Die Datei entsteht über Startmenü → „WLAN einrichten“ am Gerät oder kommt
  aus `local/wifi.json`, die `tools/install.ps1` mitkopiert (überschreibt dann die am Gerät eingerichtete); sie
  liegt nie im Repo.
- Verbinden mit `network.WLAN(network.STA_IF)`; vorher `network.hostname("clippy")` setzen. Das Gerät ist dann
  vom PC aus unter **`clippy.local`** erreichbar, im Test sogar aus einem anderen Netzabschnitt des Routers.
- PC → Gerät: Nachrichten direkt an `clippy.local` oder an die Adresse kommen an. Rundrufe (Broadcast) kommen
  nicht an, wenn PC und Gerät in verschiedenen Netzabschnitten hängen. `ping` blieb unbeantwortet; das ist kein
  Zeichen, dass das Gerät weg ist.
- Abruf von GitHub per HTTPS mit `requests`: der erste Abruf nach dem Verbinden dauerte 7,5 s, danach 0,4 s.
  Während eines Abrufs steht alles andere still.
- Änderungserkennung: GitHub liefert einen `ETag`. Schickt man ihn als `If-None-Match` mit, kommt `304` ohne
  Inhalt zurück, solange die Datei gleich ist.
- Uhr: `ntptime.settime()` stellt sie. `time.gmtime()` ist dann richtig (UTC). `time.localtime()` rechnet mit der
  voreingestellten Zeitzone der Firmware (UTC+8). Umstellen mit `time.timezone(...)`; **das Vorzeichen ist
  andersherum als bei der üblichen POSIX-Schreibweise**: `"GMT+1"` ist UTC+1. Mitteleuropa mit automatischer
  Sommerzeit: `time.timezone("CET+1CEST,M3.5.0,M10.5.0/3")` (am Gerät geprüft: Januar +1, Juli +2).

## Installieren und aktualisieren

```
.\tools\install.ps1
```

Das kopiert `device/` nach `/flash/` und `apps/` nach `/flash/apps/` (unveränderte Dateien werden übersprungen)
und startet das Gerät neu. Danach läuft Clippy von selbst, auch ohne PC.

- `device/boot.py` ersetzt die Start-Datei der Firmware und ist absichtlich leer. **Nicht mit `resume run` über
  die laufende Firmware-Oberfläche starten:** Die Firmware fährt sonst beim Start ihre eigene Oberfläche samt
  Netzwerk-Diensten hoch, beide Programme greifen dann gleichzeitig auf Display und Sensoren zu, und das Gerät
  stürzt nach einigen Minuten ab oder friert ein.
- Lebenszeichen: Etwa alle halbe Minute schreibt das Gerät eine Zeile auf die USB-Konsole
  (`clippy läuft seit ... s, frei ...`). Mitlesen geht mit jedem seriellen Monitor (115200 Baud); solange man
  nichts sendet, läuft das Programm ungestört weiter.
- Fehler im Desktop selbst landen als Bluescreen am Display und als Fehlermeldung auf der Konsole.
- Die Originale der Firmware (`boot.py`, `main.py`) lassen sich jederzeit durch Neu-Flashen zurückholen.

## Wenn das Gerät nicht mehr antwortet

Meldet `mpremote` „could not enter raw repl“ (passiert z. B., wenn ein Lauf mit `mount` hart abgebrochen wurde):
Reset-Taste unten kurz drücken, ein paar Sekunden warten, nochmal versuchen. Es geht dabei nichts verloren.

## Hintergrundbild

Der Desktop zeigt ein Bild mit 320×240 Pixeln. Es liegt nur am Gerät, nicht im Repo; fehlt es, ist der Desktop
türkis. So macht man eines aus einem beliebigen Bild (schneidet auf 4:3 zu, nimmt etwas Farbe heraus):

```
.\tools\make_background.ps1 -Source mein-bild.jpg -Out local\bg\bg.jpg
```

Mit `-Saturation 1` bleiben die Farben wie im Original, kleinere Werte machen es blasser. Ein JPG dieser Größe
zeichnet das Gerät in etwa 60 ms. `tools/install.ps1` kopiert `local/bg/bg.jpg` mit aufs Gerät, wenn die Datei da ist.

## Retten

Der Start-Lader sitzt fest im Chip und wird beim Flashen nicht überschrieben. Die Firmware lässt sich deshalb
jederzeit neu aufspielen, egal was auf dem Gerät liegt. Findet `esptool` das Gerät nicht: Reset-Taste (unten)
gedrückt halten, bis innen die grüne LED leuchtet, dann loslassen.

```
python -m esptool --port COM5 --baud 921600 write-flash 0x0 local/firmware/uiflow-cores3-v2.5.4.bin
```

Firmware-Datei (nicht im Repo):
<https://github.com/m5stack/uiflow-micropython/releases/download/2.5.4/uiflow-e437118-esp32s3-spiram-16mb-cores3-v2.5.4-20261030.bin>

Das löscht alle Dateien am Gerät. Danach mit `tools/install.ps1` neu installieren.

## Tabu

Diese drei Dinge können das Gerät dauerhaft beschädigen und werden nie gemacht:

- **eFuses brennen** (`espefuse`): einmalige, nicht umkehrbare Chip-Einstellungen.
- **Lade-Einstellungen ändern** (`M5.Power.setChargeCurrent`, `setChargeVoltage`, `setBatteryCharge`):
  falsche Werte schaden dem Akku.
- **Stromausgänge umschalten** (`M5.Power.setExtOutput`, `setUsbOutput`): kann angeschlossene Geräte beschädigen.
