# Startet Apps in einem Fenster und fängt ihre Fehler ab. Was eine App dabei bekommt, steht in app_context.py,
# der Vertrag für Apps in docs/build-an-app.md.
import io
import sys
import time

import M5

from clippy import config, wifi, win98
from clippy.app_context import Ctx
from clippy.win98 import H, TITLE_H, W


def wait_tap():
    # wartet, bis der Finger weg ist und dann einmal neu tippt
    seen_up = False
    while True:
        time.sleep_ms(30)
        M5.update()
        down = M5.Touch.getCount() > 0
        if down and seen_up:
            return
        seen_up = seen_up or not down


def _crash(display, title, e):
    out = io.StringIO()
    sys.print_exception(e, out)
    win98.bluescreen(display, title, out.getvalue())
    wait_tap()


def run_builtin(display, title, run):
    """Eingebautes Programm im selben Fensterrahmen wie eine App, z. B. „WLAN einrichten“: run(ctx)."""
    ctx = Ctx(display, title)
    try:
        run(ctx)
    except Exception as e:
        _crash(display, title, e)
    finally:
        ctx.close()


def run_app(display, app_id, title, senses):
    """Lädt apps/<id>/app.py frisch und ruft run(ctx). Jeder Fehler endet im Bluescreen, nie im Stillstand."""
    folder = config.APPS_DIR + "/" + app_id
    before = set(sys.modules)
    sys.path.insert(0, folder)   # damit die App Dateien aus ihrem eigenen Ordner importieren kann
    senses.pause()               # Mikrofon aus, Lautsprecher an
    ctx = Ctx(display, title)
    try:
        scope = {"__name__": "app"}
        with open(folder + "/app.py") as f:
            exec(f.read(), scope)
        scope["run"](ctx)
    except Exception as e:
        _crash(display, title, e)
    finally:
        ctx.close()
        senses.resume()
        sys.path.remove(folder)
        for name in set(sys.modules) - before:  # Hilfsdateien der App vergessen, damit eine Änderung sofort gilt
            del sys.modules[name]


def show_connect(display):
    # Der Satz, mit dem sich der Coding-Agent am PC selbst einrichtet (docs/agent-hooks.md)
    win98.window(display, "Mit PC verbinden")
    win98.text(display, "Tipp diesen Satz in Claude Code,", 14, TITLE_H + 10, win98.DARK, win98.FACE)
    win98.text(display, "Codex oder Copilot:", 14, TITLE_H + 28, win98.DARK, win98.FACE)
    win98.bevel(display, 8, TITLE_H + 50, W - 16, 58, raised=False)
    display.fillRect(10, TITLE_H + 52, W - 20, 54, win98.LIGHT)
    lines = win98.wrap(config.CONNECT_SENTENCE, W - 36, lambda t: win98.text_width(display, t))
    for i, line in enumerate(lines[:3]):  # normale Schrift: die Adresse passt sonst nicht in eine Zeile
        win98.text(display, line, 16, TITLE_H + 58 + i * 18, win98.DARK, win98.LIGHT)
    now = wifi.info()
    note = ("Clippy ist im WLAN %s." % now[0]) if now else "Zuerst: Startmenü > WLAN einrichten."
    win98.text(display, note, W // 2, TITLE_H + 122, win98.DARK, win98.FACE, align="center")
    win98.text(display, "Der Agent richtet den Rest selbst ein.", W // 2, TITLE_H + 142, win98.DARK, win98.FACE,
               align="center")
    win98.button(display, W // 2 - 40, H - 34, 80, 26, "OK")
    wait_tap()


def show_manual(display):
    win98.window(display, "Handbuch")
    display.fillRect(92, TITLE_H + 8, 136, 136, win98.LIGHT)
    display.drawQR(config.MANUAL_URL, 98, TITLE_H + 14, 124, 5)
    win98.text(display, "Mit dem Handy scannen", W // 2, TITLE_H + 152, win98.DARK, win98.FACE, align="center")
    win98.button(display, W // 2 - 40, H - 34, 80, 26, "OK")
    wait_tap()


def show_goodbye(display, bright):
    # Wie früher beim Herunterfahren. Das Gerät läuft weiter, nur das Display geht aus, bis man es antippt.
    display.fillScreen(0x000000)
    win98.text(display, "Sie können Clippy jetzt ignorieren.", W // 2, H // 2 - 8, 0xFF8000, 0x000000, bold=True,
               align="center")
    time.sleep_ms(2500)
    display.setBrightness(0)
    wait_tap()
    display.setBrightness(bright)
