# Startet am Gerät: zeichnet den Desktop und hält die Uhr aktuell.
import time
import M5
from lib import win98

# Bis die Apps aus dem Manifest kommen, stehen hier zwei Platzhalter.
APPS = (
    {"name": "Timer", "color": 0xB03030, "icon": "Ti"},
    {"name": "PR-Knopf", "color": 0x3050B0, "icon": "PR"},
)


def hhmm():
    t = time.localtime()
    return "%02d:%02d" % (t[3], t[4])


def status():
    return hhmm(), M5.Power.getBatteryLevel(), M5.Power.isCharging()


def draw_desktop(g):
    win98.backdrop(g, 0, 0)
    for i, app in enumerate(APPS):
        win98.icon(g, 4, 8 + i * 60, app["name"], app["color"], app["icon"])
    win98.taskbar(g, *status())


def main():
    M5.begin()
    try:
        # Mitteleuropa mit Sommerzeit. Die Firmware erwartet das Vorzeichen andersherum als üblich.
        time.timezone("CET+1CEST,M3.5.0,M10.5.0/3")
    except Exception:
        pass  # am PC (Vorschau) gibt es diese Funktion nicht
    d = M5.Display
    draw_desktop(d)
    shown = status()
    while True:
        M5.update()
        if status() != shown:
            shown = status()
            win98.tray(d, *shown)
        time.sleep_ms(200)


main()
