# Gerät: Fakten, Verbinden, Retten

Alles hier wurde am echten Gerät geprüft, außer wo „ungetestet“ steht.

## Hardware (M5Stack CoreS3)

| Teil | Zugriff in MicroPython | Stand |
|---|---|---|
| Display 320×240 | `M5.Display` (Formen, Bögen, Text, PNG/JPG, QR-Code) | geprüft |
| Touch | `M5.Touch` (`getCount`, `getX`, `getY`, `getDetail`) | geprüft |
| Bewegung, Kompass | `M5.Imu` (`getAccel`, `getGyro`, `getMag`) | geprüft |
| Lautsprecher | `M5.Speaker` (`tone`, `playWav`, `playWavFile`) | geprüft |
| Mikrofon | `M5.Mic` (`record`, `recordWavFile`); vorher `M5.Speaker.end()`, beide teilen sich die Leitung | geprüft |
| Annäherung | `M5.Als.getProximitySensorData()`, in der Schleife `M5.update()` aufrufen. Sitzt im Streifen unter dem Display | geprüft: frei 0–6, Finger drauf ca. 300 |
| Licht | `M5.Als.getLightSensorData()` | liefert bei Abendlicht nur 0–5; bei Tageslicht ungetestet |
| Akku, Strom | `M5.Power` (`getBatteryLevel`, `getBatteryVoltage`, `isCharging`, `lightSleep`, ...) | geprüft; direkt nach dem Flashen kamen falsche Werte (0 %), nach Ab- und Anstecken des Kabels stimmten sie |
| Kamera | Modul `camera` | ungetestet |
| WLAN | Modul `network`, nur 2,4 GHz | Scan geprüft |
| Uhr | `machine.RTC()` oder `time.localtime()`; nicht als `M5.Rtc` vorhanden | läuft, steht aber auf 1999, bis sie gestellt wird |

Firmware: UIFlow2 v2.5.4, MicroPython 1.27. Frei: ca. 8 MB Arbeitsspeicher, ca. 4,6 MB Dateisystem (`/flash`).
Schriften: `M5.Display.FONTS` enthält u. a. `DejaVu9` bis `DejaVu72` und `Montserrat12` bis `Montserrat48`.

**Nicht `import hardware` verwenden:** Der Aufruf blieb auf diesem Gerät hängen.

Pins, Adressen und Quellen: [hardware.md](hardware.md).

## Zeichengeschwindigkeit (gemessen mit `firmware/bench.py`)

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
python -m mpremote connect COM6 resume run firmware/hello.py
```

- Der Port heißt im Normalbetrieb anders als im Flash-Modus (hier: COM6 bzw. COM5). `connect list` zeigt ihn.
- **Immer `resume` angeben.** Ohne startet die UIFlow-Oberfläche neu und die Verbindung scheitert.
- **Keinen Python-Code direkt in der PowerShell-Befehlszeile übergeben**; Windows PowerShell entfernt die
  Anführungszeichen. Code in eine Datei schreiben und mit `run` starten.
- `run` lädt die Datei nur in den Arbeitsspeicher. Nach einem Neustart ist das Gerät wie vorher.

Prüfskripte: `firmware/hello.py` (Text am Display), `firmware/inventory.py` (listet Module und fragt Sensoren ab).

## Hintergrundbild

Der Desktop zeigt ein Bild mit 320×240 Pixeln. Es liegt nur am Gerät, nicht im Repo; fehlt es, ist der Desktop
türkis. So macht man eines aus einem beliebigen Bild (schneidet auf 4:3 zu, nimmt etwas Farbe heraus):

```
.\tools\make-background.ps1 -Source mein-bild.jpg -Out local\bg\bg.jpg
```

Mit `-Saturation 1` bleiben die Farben wie im Original, kleinere Werte machen es blasser. Ein JPG dieser Größe
zeichnet das Gerät in etwa 60 ms. Wie es aufs Gerät kommt, steht bei der Installation (folgt).

## Retten

Der Start-Lader sitzt fest im Chip und wird beim Flashen nicht überschrieben. Die Firmware lässt sich deshalb
jederzeit neu aufspielen, egal was auf dem Gerät liegt. Findet `esptool` das Gerät nicht: Reset-Taste (unten)
gedrückt halten, bis innen die grüne LED leuchtet, dann loslassen.

```
python -m esptool --port COM5 --baud 921600 write-flash 0x0 firmware/uiflow-cores3-v2.5.4.bin
```

Firmware-Datei (nicht im Repo):
<https://github.com/m5stack/uiflow-micropython/releases/download/2.5.4/uiflow-e437118-esp32s3-spiram-16mb-cores3-v2.5.4-20261030.bin>

Das löscht alle Dateien am Gerät. Danach den Kern neu installieren (Anleitung folgt mit `tools/install.ps1`).

## Tabu

Diese drei Dinge können das Gerät dauerhaft beschädigen und werden nie gemacht:

- **eFuses brennen** (`espefuse`): einmalige, nicht umkehrbare Chip-Einstellungen.
- **Lade-Einstellungen ändern** (`M5.Power.setChargeCurrent`, `setChargeVoltage`, `setBatteryCharge`):
  falsche Werte schaden dem Akku.
- **Stromausgänge umschalten** (`M5.Power.setExtOutput`, `setUsbOutput`): kann angeschlossene Geräte beschädigen.
