# Hardware-Referenz M5Stack CoreS3 (K128)

Auszug aus der Hersteller-Doku, Stand 12.11.2026. Für die tägliche Arbeit reicht [device.md](device.md);
diese Datei braucht nur, wer direkt an Chips oder Anschlüsse will.

## Eckdaten

| Teil | Wert |
|---|---|
| Prozessor | ESP32-S3, 2 Kerne, 240 MHz, WLAN 2,4 GHz |
| Speicher | 16 MB Flash, 8 MB PSRAM |
| Display | 2,0" IPS, 320×240, ILI9342C/E, kapazitiver Touch FT6336U |
| Kamera | GC0308, 0,3 MP, sitzt unter dem Display |
| Annäherung + Licht | LTR-553ALS-WA, auf demselben Flachbandkabel wie die Kamera, also auch unter dem Display |
| Bewegung | BMI270 (6 Achsen) + BMM150 (Magnetometer, am BMI270 angehängt) |
| Ton | Verstärker AW88298 mit 1-W-Lautsprecher, ES7210 mit 2 Mikrofonen |
| Uhr | BM8563 |
| Strom | AXP2101, Akku 500 mAh, sitzt im Bodenteil (DinBase) |
| microSD | bis 16 GB |
| Maße | 54 × 54 × 15,5 mm ohne, 69 × 54 × 31,5 mm mit Bodenteil |

## Tasten

- Power (links): kurz drücken = ein, lang drücken = aus.
- Reset (unten): kurz drücken = Neustart. **Gedrückt halten, bis die grüne LED innen leuchtet, dann loslassen
  = Download-Modus** zum Flashen, falls das automatische Umschalten nicht klappt.

Magnete in der Nähe stören den Kompass (BMM150).

## Interner I2C-Bus (SDA = G12, SCL = G11)

| Chip | Adresse | | Chip | Adresse |
|---|---|---|---|---|
| AXP2101 | 0x34 | | FT6336 | 0x38 |
| AW88298 | 0x36 | | ES7210 | 0x40 |
| AW9523 | 0x58 | | BM8563 | 0x51 |
| BMI270 | 0x69 | | GC0308 | 0x21 |
| BMM150 | 0x10 | | LTR553 | 0x23 |

## Belegte Pins

| Funktion | Pins |
|---|---|
| Display (SPI) | MOSI G37, SCK G36, CS G3, DC G35 |
| microSD (SPI, geteilt mit Display) | MISO G35, MOSI G37, SCK G36, CS G4 |
| Ton (I2S) | BCK G34, WCK G33, Daten raus G13, Daten rein G14, MCLK G0 |
| Kamera | PCLK G45, VSYNC G46, HREF G38, Daten G39–G42, G15, G16, G48, G47 |

## Freie Anschlüsse (Grove, 5 V)

| Anschluss | Gelb | Weiß |
|---|---|---|
| PORT.A (rot, I2C) | G2 | G1 |
| PORT.B (schwarz) | G9 | G8 |
| PORT.C (blau, UART) | G17 | G18 |

Die Stromrichtung an diesen Anschlüssen steuert der AXP2101 zusammen mit dem AW9523B. Finger weg davon, siehe
Tabu-Liste in [device.md](device.md).

## Quellen

- Hersteller-Seite: <https://docs.m5stack.com/en/core/CoreS3> (Spiegel: <https://docs.m5stack.switch-science.com/en/core/CoreS3>)
- Schaltplan: <https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/490/Sch_M5_CoreS3_v1.0.pdf>
- Schaltplan Bodenteil: <https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/559/SCH_DinBase_V1.1.pdf>
- ESP32-S3-Datenblatt: <https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf>
- MicroPython-Schnittstellen der Firmware: <https://uiflow-micropython.readthedocs.io/en/latest/>
  (für dieses Gerät: `controllers/cores3`, `hardware/*`, `system/power`, `system/time`)
- Datenblätter der einzelnen Chips sind auf der Hersteller-Seite unter „Datasheets“ verlinkt.

Heruntergeladene Kopien liegen lokal in `local/reference/` und gehören nicht ins Repo (fremdes Urheberrecht).
