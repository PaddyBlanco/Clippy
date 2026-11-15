# Lage zum Mitmachen: misst die Schwerkraft beim normal stehenden und beim umgedrehten Gerät,
# dreht dann das Display um und prüft, ob die Touch-Koordinaten mitgedreht werden.
# python -m mpremote connect COM6 resume run checks/orientation.py
import M5, time

M5.begin()
d = M5.Display
BLUE, WHITE, RED = 0x000080, 0xFFFFFF, 0xFF0000


def say(line1, line2=""):
    d.fillScreen(BLUE)
    d.setTextColor(WHITE, BLUE)
    d.setTextSize(2)
    d.drawCenterString(line1, 160, 90)
    d.drawCenterString(line2, 160, 130)


def wait_tap(max_s=60):
    for _ in range(max_s * 20):
        M5.update()
        if M5.Touch.getCount():
            x, y = M5.Touch.getX(), M5.Touch.getY()
            while M5.Touch.getCount():  # loslassen abwarten
                M5.update()
                time.sleep_ms(20)
            return x, y
        time.sleep_ms(50)
    return None


def accel(label, seconds=3):
    sx = sy = sz = 0
    n = seconds * 10
    for _ in range(n):
        M5.update()
        ax, ay, az = M5.Imu.getAccel()
        sx, sy, sz = sx + ax, sy + ay, sz + az
        time.sleep_ms(100)
    print("ACCEL", label, "x %.2f y %.2f z %.2f" % (sx / n, sy / n, sz / n))


try:
    start = d.getRotation()
except Exception:
    start = 1
print("ROTATION", start)
say("Geraet normal hinstellen,", "dann kurz tippen")
wait_tap()
say("Stillhalten ...")
accel("normal")
say("Jetzt auf den Kopf stellen", "und 5 Sekunden halten")
time.sleep_ms(4000)
accel("kopf")
d.setRotation((start + 2) % 4)
say("Display gedreht.", "Tipp auf das rote Kreuz")
d.drawLine(10, 10, 30, 30, RED)
d.drawLine(10, 30, 30, 10, RED)
print("TOUCH Kreuz bei 20 20, Tipper bei", wait_tap())
d.setRotation(start)
say("Fertig. Wieder", "normal hinstellen")
