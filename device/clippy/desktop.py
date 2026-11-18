# Der Desktop: lädt die App-Liste, zeichnet alles und verteilt Tipper in der Hauptschleife.
import gc
import json
import time

import M5

from clippy import config, launcher, shell, wifi, wifi_setup, win98
from clippy.monitor import Monitor
from clippy.pet import phrases
from clippy.pet.habits import BRIGHT
from clippy.pet.pet import Pet
from clippy.pet.senses import Senses

MENU = ("WLAN einrichten", "Mit PC verbinden", "Handbuch", "Beenden")
MAX_ICONS = 4  # mehr passen nicht in die Spalte am linken Rand
# eingebaut, öffnet monitor.py; statt Buchstaben zeigt das Symbol das Zeichen des Agents, der gerade dran ist
MONITOR = {"id": None, "name": "Agent", "icon": None, "color": "#208080"}


def load_apps():
    """Symbole am Desktop: die Apps aus manifest.json, zuletzt das eingebaute „Agent“."""
    try:
        with open(config.APPS_DIR + "/manifest.json") as f:
            apps = json.load(f)[:MAX_ICONS - 1]
    except (OSError, ValueError):
        apps = []  # ohne Liste gibt es eben keine App-Symbole
    return apps + [MONITOR]


def status(senses):
    t = time.localtime()
    return ("%02d:%02d" % (t[3], t[4]), M5.Power.getBatteryLevel(), M5.Power.isCharging(), wifi.connected(),
            senses.agents.summary())


def draw(g, apps, senses):
    win98.backdrop(g, 0, 0)
    for i, app in enumerate(apps):
        shell.icon(g, i, app["name"], int(app["color"][1:], 16), app["icon"], senses.agents.current())
    shell.taskbar(g, *status(senses))


def start_menu(d):
    """Zeigt das Startmenü und führt aus, was gewählt wurde."""
    shell.menu(d, MENU)
    launcher.wait_tap()
    choice = shell.menu_hit(M5.Touch.getX(), M5.Touch.getY(), MENU)
    if choice == 0:
        launcher.run_builtin(d, MENU[0], wifi_setup.run)
    elif choice == 1:
        launcher.show_connect(d)
    elif choice == 2:
        launcher.show_manual(d)
    elif choice == 3:
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
    monitor = Monitor(d, senses.agents)
    clippy.say(phrases.pick("start"))
    shown, agent = status(senses), senses.agents.current()
    turn, down, clock_set = 0, True, False
    while True:
        M5.update()
        turn += 1
        if turn % 16 == 0:  # etwa einmal je Sekunde
            if not clock_set and turn % 160 == 0:  # Uhr stellen, sobald das WLAN steht; sonst in 10 s nochmal
                clock_set = wifi.sync_clock()
            if status(senses) != shown:
                shown = status(senses)
                shell.tray(d, *shown)
            if senses.agents.current() != agent:  # ein anderer Agent ist dran: sein Zeichen aufs Symbol
                agent = senses.agents.current()
                shell.icon(d, len(apps) - 1, MONITOR["name"], 0, None, agent)
                clippy.stage.repaint()
            if not clippy.bubble.box:  # die Klammer spricht: Blase bleibt vorn, das Fenster wartet
                monitor.draw()  # auch, was Sprechblase oder Sturz darübergemalt haben, ist danach wieder weg
        if turn % 400 == 0:  # etwa alle halbe Minute ein Lebenszeichen auf die USB-Konsole
            print("clippy läuft seit", time.ticks_ms() // 1000, "s, frei", getattr(gc, "mem_free", int)())

        was_down, down = down, M5.Touch.getCount() > 0
        tap = (M5.Touch.getX(), M5.Touch.getY()) if down and not was_down else None
        inside = monitor.hit(*tap) if tap else None
        target = shell.hit(tap[0], tap[1], len(apps)) if tap and not inside else None
        if inside == "close" or target is not None:
            if inside == "close":
                monitor.open = False
            elif target == "start":
                start_menu(d)
            elif apps[target] is MONITOR:
                monitor.open = True
            else:
                launcher.run_app(d, apps[target]["id"], apps[target]["name"], senses)
            draw(d, apps, senses)  # alles neu zeichnen: nach App oder Menü, oder das Fenster ist auf oder zu
            clippy.refresh()
            monitor.draw()
            shown = status(senses)

        clippy.step()
        time.sleep_ms(60)
