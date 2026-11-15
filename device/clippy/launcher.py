# Startet Apps in einem Fenster und fängt ihre Fehler ab. Der Vertrag für Apps steht in docs/build-an-app.md.
import io
import sys
import time

import M5

from clippy import config, win98
from clippy.win98 import H, TITLE_H, W

CLOSE_ZONE = (W - 48, 40)  # Tipper rechts oben (ab x, bis y) schließt das Fenster


class Ctx:
    """Was eine App vom Gerät bekommt."""

    W, H = W, H - TITLE_H

    def __init__(self, display, title):
        self._d = display
        win98.window(display, title)
        self.screen = display.newCanvas(self.W, self.H, 16, True)  # hierauf zeichnet die App
        self.screen.fillScreen(win98.FACE)
        self.tap = None      # (x, y) des Tippers in diesem Durchlauf, sonst None
        self._down = True    # der Tipper, der die App geöffnet hat, zählt nicht

    def update(self):
        """Einmal je Schleifendurchlauf aufrufen. Liefert False, sobald das Fenster geschlossen wurde."""
        time.sleep_ms(20)
        M5.update()
        down = M5.Touch.getCount() > 0
        self.tap = None
        if down and not self._down:
            x, y = M5.Touch.getX(), M5.Touch.getY()
            if x >= CLOSE_ZONE[0] and y < CLOSE_ZONE[1]:
                return False
            if y >= TITLE_H:
                self.tap = (x, y - TITLE_H)
        self._down = down
        return True

    def show(self):
        """Bringt screen aufs Display."""
        self.screen.push(0, TITLE_H)

    def tone(self, hz, ms):
        M5.Speaker.tone(hz, ms)

    def close(self):
        self.screen.delete()


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
        for name in set(sys.modules) - before:  # Hilfsdateien der App vergessen, damit ein Update sofort gilt
            del sys.modules[name]


def show_note(display, title, note):
    win98.window(display, title)
    for i, line in enumerate(win98.wrap(note, W - 40, lambda t: win98.text_width(display, t))):
        win98.text(display, line, 20, TITLE_H + 30 + i * (win98.FONT_H + 3), win98.DARK, win98.FACE)
    win98.button(display, W // 2 - 40, H - 50, 80, 28, "OK")
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
