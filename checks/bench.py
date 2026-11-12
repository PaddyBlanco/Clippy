# Misst Zeichengeschwindigkeit und fragt ungetestete Sensoren ab.
# python -m mpremote connect COM6 resume run checks/bench.py
import M5, time, struct

M5.begin()
d = M5.Display
TEAL, GREY, DARK, WHITE, BLACK = 0x008080, 0xC0C0C0, 0x404040, 0xFFFFFF, 0x000000
W, H = 110, 150  # Feld, in dem sich die Klammer bewegt


def figure(g, x, y):
    # Arbeitslast wie die spätere Klammer: Draht aus Bögen und Balken, Augen, Brauen
    g.fillRect(x, y, W, H, TEAL)
    for r0, r1, c in ((30, 40, DARK), (32, 38, GREY)):
        g.fillArc(x + 55, y + 50, r0, r1, 180, 360, c)
        g.fillArc(x + 55, y + 105, r0 - 8, r1 - 8, 0, 180, c)
    for dx in (15, 25, 77, 87):
        g.fillRect(x + dx, y + 50, 8, 55, GREY)
    for dx in (40, 70):
        g.fillEllipse(x + dx, y + 45, 11, 14, WHITE)
        g.fillCircle(x + dx + 2, y + 47, 5, BLACK)
        g.fillRect(x + dx - 12, y + 22, 24, 5, BLACK)


def ms(label, n, fn):
    t = time.ticks_ms()
    for _ in range(n):
        fn()
    per = time.ticks_diff(time.ticks_ms(), t) / n
    print("%-34s %6.1f ms  = %5.1f Bilder/s" % (label, per, 1000 / per))


def probe(label, fn):
    try:
        print(label, "->", fn())
    except Exception as e:
        print(label, "-> FEHLER", type(e).__name__, e)


d.fillScreen(TEAL)
ms("Bildschirm fuellen", 20, lambda: d.fillScreen(TEAL))
ms("Figur direkt aufs Display", 30, lambda: figure(d, 200, 60))

small = full = None
try:
    small = d.newCanvas(W, H, 16, True)
    full = d.newCanvas(320, 240, 16, True)
    print("canvas:", [n for n in dir(small) if not n.startswith("_")])
except Exception as e:
    print("newCanvas -> FEHLER", type(e).__name__, e)

if small:
    def via_small():
        figure(small, 0, 0)
        small.push(200, 60)
    ms("Figur ueber kleines Canvas", 30, via_small)
if full:
    full.fillScreen(TEAL)
    ms("ganzes Canvas nur schieben", 20, lambda: full.push(0, 0))

    def via_full():
        figure(full, 200, 60)
        full.push(0, 0)
    ms("Figur ueber ganzes Canvas", 20, via_full)

print("--- Sensoren")
for _ in range(3):
    probe("licht / naehe", lambda: (M5.Als.getLightSensorData(), M5.Als.getProximitySensorData()))
    time.sleep_ms(200)
probe("akku % / mV / mA", lambda: (M5.Power.getBatteryLevel(), M5.Power.getBatteryVoltage(), M5.Power.getBatteryCurrent()))
probe("laedt / usb mV", lambda: (M5.Power.isCharging(), M5.Power.getVBUSVoltage()))
probe("time.localtime", lambda: time.localtime())


def rtc():
    import machine
    return machine.RTC().datetime()


def mic():
    M5.Speaker.end()  # Mikrofon und Lautsprecher teilen sich die Leitung
    M5.Mic.begin()
    buf = bytearray(8000)  # 0,25 s bei 16 kHz, 16 Bit
    M5.Mic.record(buf, 16000, False)
    for _ in range(100):  # höchstens 1 s warten, nie hängen bleiben
        if not M5.Mic.isRecording():
            break
        time.sleep_ms(10)
    M5.Mic.end()
    M5.Speaker.begin()
    s = struct.unpack("<%dh" % (len(buf) // 2), buf)
    return "spitze", max(abs(v) for v in s), "mittel", sum(abs(v) for v in s) // len(s)


probe("machine.RTC", rtc)
print("mikrofon ...")
probe("mikrofon", mic)
d.setTextColor(WHITE, TEAL)
d.setTextSize(2)
d.drawCenterString("Messung fertig", 160, 110)
