"""Bilder fürs Handbuch: zeichnet Szenen mit tools/preview.py nach manual/img/s<Nr>.png.

    python tools/screenshots.py [zielordner]      (Standard: manual/img)

Läuft beim Veröffentlichen in GitHub Actions (.github/workflows/manual.yml); die Bilder liegen nie im Repo
(AGENTS.md, Regel 4). Welche Nummer was zeigt, steht in docs/manual.md. Bilder, die nur das echte Gerät oder ein
Handy liefern kann (Foto, echte WLAN-Liste, QR-Codes), bleiben auf den Seiten Platzhalter.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "tools", "preview.py")

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
    "s12": "stage.show(dict(REST, look=(4, 3), brow=2))\n"
           "shell.taskbar(d, '14:24', 80, False, True, (('Cl', 'working'), ('Co', 'done'), ('Cx', 'waiting')))",
    "s13": "stage.show(nth(moves.cheer(), 3))\n"
           "Bubble(d).say('Claude braucht di!')\n"
           "shell.taskbar(d, '14:24', 80, False, True, (('Cl', 'waiting'),))",
    "s14": "stage.show(REST)\nshell.menu(d, desktop.MENU)",
    "s16": "from clippy.pet import dance\nstage.narrow = True\nstage.show(nth(dance.sway(), 4))\n"
           "app('radio', 'Radio', True, taps=[(140, 40)], online=lambda: True, play=lambda url: True,\n"
           "    playing=lambda: True)",  # Ö3 angetippt, der Sender spielt, die Klammer tanzt
    "s18": "launcher.show_goodbye(d, 100)",
    "s24": "umbrella.rain(True)\nstage.narrow = True\nstage.show(nth(umbrella.hold(), 20))\n"
           "sample = json.load(open(ROOT + '/tests/weather_sample.json', encoding='utf-8'))\n"
           "app('weather', 'Wetter', True, online=lambda: True, get_json=lambda url: sample)",
    "s25": None,  # die Diashow mit einem Probefoto: apps/slideshow/app.py mit --sd
}


def probe_photo(folder):
    """Ein freundliches Probefoto (Sonne über Hügeln), damit die Diashow etwas zeigt; entsteht hier, nie im Repo."""
    im = Image.new("RGB", (291, 218), (110, 170, 235))
    g = ImageDraw.Draw(im)
    g.ellipse([190, 30, 250, 90], fill=(255, 215, 60))
    g.ellipse([-60, 130, 200, 330], fill=(70, 150, 70))
    g.ellipse([120, 150, 380, 340], fill=(50, 125, 55))
    g.rectangle([60, 120, 110, 175], fill=(200, 80, 60))
    g.polygon([(52, 122), (85, 90), (118, 122)], fill=(140, 50, 40))
    os.makedirs(os.path.join(folder, "Clippy-Bilder"))
    im.save(os.path.join(folder, "Clippy-Bilder", "Haus.jpg"), quality=90)


def render(name, out, tmp):
    target = os.path.join(out, name + ".png")
    if name == "s1":
        args = [os.path.join(ROOT, "device", "main.py"), target, "3"]
    elif name == "s25":
        card = os.path.join(tmp, "sd")
        probe_photo(card)
        args = [os.path.join(ROOT, "apps", "slideshow", "app.py"), target, "4", "--sd", card]
    else:
        scene = os.path.join(tmp, name + ".py")
        with open(scene, "w", encoding="utf-8") as f:
            f.write("ROOT = %r\n" % ROOT.replace("\\", "/") + HEAD + SCENES[name] + "\n")
        args = [scene, target, "4"]
    run = subprocess.run([sys.executable, PREVIEW] + args, capture_output=True, text=True)
    if run.returncode != 0 or not os.path.exists(target):
        raise SystemExit("%s ging nicht:\n%s%s" % (name, run.stdout, run.stderr))
    print(name, "->", target)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "manual", "img"))
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name in SCENES:
            render(name, out, tmp)


if __name__ == "__main__":
    main()
