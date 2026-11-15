# Der Desktop: lädt die App-Liste, zeichnet alles und verteilt Tipper in der Hauptschleife.
import gc
import json
import time

import M5

from clippy import config, launcher, shell, wifi, win98
from clippy.pet import phrases
from clippy.pet.habits import BRIGHT
from clippy.pet.pet import Pet
from clippy.pet.senses import Senses

MENU = ("WLAN einrichten", "Handbuch", "Beenden")
MAX_ICONS = 4  # mehr passen nicht in die Spalte am linken Rand


def load_apps():
    try:
        with open(config.APPS_DIR + "/manifest.json") as f:
            return json.load(f)[:MAX_ICONS]
    except (OSError, ValueError):
        return []  # ohne Liste gibt es eben keine Symbole


def status(senses):
    t = time.localtime()
    return ("%02d:%02d" % (t[3], t[4]), M5.Power.getBatteryLevel(), M5.Power.isCharging(),
            senses.agents.summary())


def draw(g, apps, senses):
    win98.backdrop(g, 0, 0)
    for i, app in enumerate(apps):
        shell.icon(g, i, app["name"], int(app["color"][1:], 16), app["icon"])
    shell.taskbar(g, *status(senses))


def start_menu(d):
    """Zeigt das Startmenü und führt aus, was gewählt wurde."""
    shell.menu(d, MENU)
    launcher.wait_tap()
    choice = shell.menu_hit(M5.Touch.getX(), M5.Touch.getY(), MENU)
    if choice == 0:
        launcher.show_note(d, MENU[0], "Kummt nu. Bis dahin steht in docs/device.md, wia ma's WLAN eistöht.")
    elif choice == 1:
        launcher.show_manual(d)
    elif choice == 2:
        launcher.show_goodbye(d, BRIGHT)


def run():
    M5.begin()
    try:
        # Mitteleuropa mit Sommerzeit. Die Firmware erwartet das Vorzeichen andersherum als üblich.
        time.timezone("CET+1CEST,M3.5.0,M10.5.0/3")
    except Exception:
        pass  # am PC (Vorschau) gibt es diese Funktion nicht
    wifi.connect()  # wartet nicht; die Agents horchen, sobald die Verbindung steht
    d = M5.Display
    apps = load_apps()
    senses = Senses()
    draw(d, apps, senses)
    clippy = Pet(d, senses, lambda g: draw(g, apps, senses))
    clippy.say(phrases.pick("start"))
    shown = status(senses)
    turn, down = 0, True
    while True:
        M5.update()
        turn += 1
        if turn % 16 == 0 and status(senses) != shown:  # etwa einmal je Sekunde nachsehen
            shown = status(senses)
            shell.tray(d, *shown)
        if turn % 400 == 0:  # etwa alle halbe Minute ein Lebenszeichen auf die USB-Konsole
            print("clippy läuft seit", time.ticks_ms() // 1000, "s, frei", gc.mem_free())

        was_down, down = down, M5.Touch.getCount() > 0
        target = shell.hit(M5.Touch.getX(), M5.Touch.getY(), len(apps)) if down and not was_down else None
        if target is not None:
            if target == "start":
                start_menu(d)
            else:
                launcher.run_app(d, apps[target]["id"], apps[target]["name"], senses)
            draw(d, apps, senses)  # zurück am Desktop: alles neu zeichnen
            clippy.refresh()
            shown = status(senses)

        clippy.step()
        time.sleep_ms(60)
