# Sensortest zum Mitmachen: wartet auf einen Tipp, dann Annäherung/Licht, dann Mikrofon.
# python -m mpremote connect COM6 resume run checks/sensortest.py
import M5, time, struct

M5.begin()
d = M5.Display
BLUE, WHITE = 0x000080, 0xFFFFFF


def say(line1, line2=""):
    d.fillScreen(BLUE)
    d.setTextColor(WHITE, BLUE)
    d.setTextSize(2)
    d.drawCenterString(line1, 160, 70)
    d.drawCenterString(line2, 160, 110)


def wait_tap(max_s):
    for _ in range(max_s * 20):
        M5.update()
        if M5.Touch.getCount():
            return True
        time.sleep_ms(50)
    return False


def proximity(seconds):
    lo, hi, light_lo, light_hi = 99999, 0, 99999, 0
    for i in range(seconds * 5):
        M5.update()  # ohne das liefert der Sensor nur Nullen
        p, l = M5.Als.getProximitySensorData(), M5.Als.getLightSensorData()
        lo, hi, light_lo, light_hi = min(lo, p), max(hi, p), min(light_lo, l), max(light_hi, l)
        d.drawCenterString("  Naehe %4d  Licht %5d  " % (p, l), 160, 170)
        print("naehe", p, "licht", l)
        time.sleep_ms(200)
    print("NAEHE min/max", lo, hi, "LICHT min/max", light_lo, light_hi)


def mic(label, chunks):
    buf = bytearray(8000)  # 0,25 s bei 16 kHz, 16 Bit
    peaks = []
    for _ in range(chunks):
        M5.Mic.record(buf, 16000, False)
        for _ in range(100):  # höchstens 1 s warten, nie hängen bleiben
            if not M5.Mic.isRecording():
                break
            time.sleep_ms(10)
        peak = max(abs(v) for v in struct.unpack("<4000h", buf))
        peaks.append(peak)
        d.drawCenterString("  Pegel %5d  " % peak, 160, 170)
    print(label, peaks)


def main():
    say("Sensortest", "Display antippen = Start")
    if not wait_tap(480):
        print("kein Tipp innerhalb von 8 Minuten, Abbruch")
        return
    say("Hand langsam vors Geraet", "und wieder weg (8 s)")
    proximity(8)
    say("Jetzt Sensor abdecken", "dann Licht drauf (8 s)")
    proximity(8)
    M5.Speaker.end()  # Mikrofon und Lautsprecher teilen sich die Leitung
    M5.Mic.begin()
    say("Jetzt ganz leise sein", "(2 s)")
    mic("MIKRO leise", 8)
    say("Jetzt 3x klatschen", "(5 s)")
    mic("MIKRO klatschen", 20)
    M5.Mic.end()
    M5.Speaker.begin()
    say("Fertig, danke!")


main()
