# Der Desktop: Hintergrund, Symbole, Taskleiste, Klammer und die Hauptschleife.
import time

import M5

from clippy import win98
from clippy.pet import phrases
from clippy.pet.pet import Pet
from clippy.pet.senses import Senses

# Bis die Apps aus dem Manifest kommen, stehen hier zwei Platzhalter.
APPS = (
    {"name": "Timer", "color": 0xB03030, "icon": "Ti"},
    {"name": "PR-Knopf", "color": 0x3050B0, "icon": "PR"},
)


def status():
    t = time.localtime()
    return "%02d:%02d" % (t[3], t[4]), M5.Power.getBatteryLevel(), M5.Power.isCharging()


def draw(g):
    win98.backdrop(g, 0, 0)
    for i, app in enumerate(APPS):
        win98.icon(g, 4, 8 + i * 60, app["name"], app["color"], app["icon"])
    win98.taskbar(g, *status())


def run():
    M5.begin()
    try:
        # Mitteleuropa mit Sommerzeit. Die Firmware erwartet das Vorzeichen andersherum als üblich.
        time.timezone("CET+1CEST,M3.5.0,M10.5.0/3")
    except Exception:
        pass  # am PC (Vorschau) gibt es diese Funktion nicht
    d = M5.Display
    draw(d)
    clippy = Pet(d, Senses())
    clippy.say(phrases.pick("start"))
    shown = status()
    turn = 0
    while True:
        M5.update()
        turn += 1
        if turn % 16 == 0 and status() != shown:  # etwa einmal je Sekunde nachsehen
            shown = status()
            win98.tray(d, *shown)
        clippy.step()
        time.sleep_ms(60)
