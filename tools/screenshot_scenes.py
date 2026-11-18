"""Szenen fürs Handbuch: je Bild ein Stück Python, das tools/screenshots.py hinter HEAD hängt und mit
tools/preview.py zeichnet. Welche Nummer was zeigt, steht in docs/manual.md. Was nur das Gerät weiß (WLAN in der
Nähe, Nutzungszahlen, Adresse im WLAN), ist hier erfunden, sieht aber genauso aus wie am Gerät.
"""

# WLANs in der Nähe, erfunden (S19, S22): Name, Empfang, mit Passwort
NETS = [("Zuhause", -48, True), ("FRITZ!Box 7530 KL", -60, True), ("Nachbarn", -71, True), ("Gast", -77, False),
        ("Cafe am Stadtplatz", -84, True)]

# Vorspann jeder Szene: Desktop zeichnen wie am Gerät; danach zeigt stage.show(pose) die Klammer.
HEAD = """
import json
import M5
from clippy import desktop, launcher, shell, win98
from clippy.app_context import Ctx
from clippy.pet import boredom, moves, sleep, umbrella
from clippy.pet.bubble import Bubble
from clippy.pet.draw import REST
from clippy.pet.senses import Senses
from clippy.pet.stage import Stage

d = M5.Display
apps = desktop.load_apps()
senses = Senses()
desktop.draw(d, apps, senses)
stage = Stage(d, lambda g: desktop.draw(g, apps, senses), senses.agents)


def first(gen, test):
    return next(p for p in gen if test(p))


def nth(gen, n):
    for i, p in enumerate(gen):
        if i == n:
            return p


def app(name, title, beside, taps=(), **patch):
    # App starten wie der Launcher; taps: Tipper der Reihe nach, je Durchlauf einer. Die Vorschau beendet die App
    # nach ein paar Durchläufen.
    import sys
    sys.path.insert(0, ROOT + "/apps/" + name)  # wie launcher.run_app: Hilfsdateien der App finden
    scope = {"__name__": "app"}
    exec(open(ROOT + "/apps/" + name + "/app.py", encoding="utf-8").read(), scope)
    ctx = Ctx(d, title, beside)
    ctx._down = False
    for key, value in patch.items():
        setattr(ctx, key, value)
    queue, update = list(taps), ctx.update

    def tapping():
        going = update()
        ctx.tap = queue.pop(0) if queue else None
        return going
    ctx.update = tapping
    scope["run"](ctx)
""" + "NETS = %r\n" % (NETS,)

# Claude arbeitet am Projekt Clippy; Zahlen wie in tests/test_agent_hooks.py
AGENT = """import time
from clippy.agent_hooks import AGENTS
from clippy.monitor import Monitor
now, ms = time.time(), time.ticks_ms()
status = {"model": {"display_name": "Opus 5.5"}, "cost": {"total_cost_usd": 1.234, "total_lines_added": 120,
          "total_lines_removed": 30}, "rate_limits": {"five_hour": {"used_percentage": 42, "resets_at": now + 7200},
          "seven_day": {"used_percentage": 18, "resets_at": now + 86400 * 3}}}
senses.agents.usage["Claude"] = (AGENTS["claude"]().usage(status), ms)
senses.agents.known["Claude"] = {"short": "Cl", "state": "working", "heard": ms, "called": ms, "calls": 1,
                                 "seen": False, "project": "Clippy", "since": ms}
shell.taskbar(d, "14:24", 80, False, True, senses.agents.summary())
monitor = Monitor(d, senses.agents)
monitor.open = True
monitor.draw()
stage.narrow = True
stage.show(dict(REST, look=(-4, 2)))
"""

SCENES = {
    "s1": None,  # der Desktop mit Begrüßung: device/main.py selbst
    "s3": "stage.show(nth(moves.curl(), 10))",
    "s4": "stage.show(nth(boredom.drum_solo(), 8))",
    "s5": "stage.show(first(boredom.headstand(), lambda p: p['roll'] >= 180))",
    "s6": "stage.show(first(boredom.pogo(), lambda p: p['pogo'] == 20 and p['bob'] <= -27))",
    "s7": "stage.show(nth(moves.threaten(), 2))",
    "s8": "stage.show(nth(moves.enjoy(), 2))",
    "s9": "stage.show(sleep.pose(14, True))",
    "s10": "stage.show(first(moves.fall(), lambda p: p['lean'] == 88 and p['lid'] == 1.0))",
    "s11": "from clippy.pet import tumble\nstage.show(nth(tumble.tumble(), 1))",  # hängt nach dem Umdrehen verkehrt
    "s12": "stage.show(dict(REST, look=(4, 3), brow=2))\n"
           "shell.taskbar(d, '14:24', 80, False, True, (('Cl', 'working'), ('Co', 'done'), ('Cx', 'waiting')))",
    "s13": "stage.show(nth(moves.cheer(), 3))\n"
           "Bubble(d).say('Claude braucht di!')\n"
           "shell.taskbar(d, '14:24', 80, False, True, (('Cl', 'waiting'),))",
    "s14": "stage.show(REST)\nshell.menu(d, desktop.MENU)",
    "s15": "launcher.show_manual(d)",
    "s16": "from clippy.pet import dance\nstage.narrow = True\nstage.show(nth(dance.sway(), 4))\n"
           "app('radio', 'Radio', True, taps=[(140, 40)], online=lambda: True, play=lambda url: True,\n"
           "    playing=lambda: True)",  # Ö3 angetippt, der Sender spielt, die Klammer tanzt
    "s18": "launcher.show_goodbye(d, 100)",
    "s19": "from clippy import wifi, wifi_setup\nwifi.scan = lambda: NETS\nwifi.info = lambda: None\n"
           "wifi_setup._pick(Ctx(d, 'WLAN einrichten'))",
    "s20": "from clippy.keyboard import Keyboard\nctx = Ctx(d, 'WLAN einrichten')\n"
           "Keyboard('Passwort für Zuhause:', 'Sonnenbl').draw(ctx.screen)\nctx.show()",
    "s21": "from clippy import wifi_portal\nwifi_portal._screen(Ctx(d, 'WLAN einrichten'),\n"
           "    'WIFI:T:WPA;S:Clippy-Setup;P:48151623;;',\n"
           "    ['1. QR scannen', 'mit der Handy-', 'Kamera. Oder WLAN', 'Clippy-Setup', 'Passwort 48151623'])",
    "s23": AGENT,
    "s24": "umbrella.rain(True)\nstage.narrow = True\nstage.show(nth(umbrella.hold(), 20))\n"
           "sample = json.load(open(ROOT + '/tests/weather_sample.json', encoding='utf-8'))\n"
           "app('weather', 'Wetter', True, online=lambda: True, get_json=lambda url: sample)",
    "s25": None,  # die Diashow mit einem Probefoto: apps/slideshow/app.py mit --sd
    "s26": "from clippy import photo_drop\n"
           "photo_drop._screen(Ctx(d, 'Diashow'), 'http://192.168.1.23:8080/?k=424242', 3)",
}
