# Internetradio: Sender antippen, mit - und + leiser und lauter. Das X schließt das Fenster und schaltet das Radio aus.
import time

from clippy import win98
from clippy.win98 import DARK, FACE
from stations import STATIONS

COLS, BTN_W, BTN_H, GAP = 2, 154, 40, 4  # Senderknöpfe in zwei Spalten, dazu „Aus“
GRID_Y, VOL_Y = 36, 172                   # erste Reihe der Knöpfe; Reihe für die Lautstärke
STEP, WAIT_MS = 10, 12000                 # Schritt der Lautstärke; so lange darf das Verbinden dauern
GREEN = 0x40E040                          # Schrift der Anzeige oben, wie bei einem Radio
NO_WIFI = "Ka WLAN. Startmenü > WLAN einrichten"


def _cell(i):
    return 4 + (i % COLS) * (BTN_W + GAP), GRID_Y + (i // COLS) * (BTN_H + GAP)


def hit(x, y):
    """Was liegt unter dem Finger: ("station", Nummer), ("off",), ("down",), ("up",) oder None."""
    for i in range(len(STATIONS) + 1):
        cx, cy = _cell(i)
        if cx <= x < cx + BTN_W and cy <= y < cy + BTN_H:
            return ("off",) if i == len(STATIONS) else ("station", i)
    if VOL_Y <= y < VOL_Y + 40:
        if x < 64:
            return ("down",)
        if x >= 320 - 64:
            return ("up",)
    return None


def draw(g, w, current, note, volume):
    g.fillScreen(FACE)
    win98.bevel(g, 4, 4, w - 8, 26, raised=False)  # die Anzeige oben
    g.fillRect(6, 6, w - 12, 22, DARK)
    win98.text(g, note, w // 2, 9, GREEN, DARK, bold=True, align="center")
    for i, (name, _) in enumerate(STATIONS):
        x, y = _cell(i)
        win98.bevel(g, x, y, BTN_W, BTN_H, raised=i != current)  # der laufende Sender ist eingedrückt
        win98.text(g, name, x + BTN_W // 2, y + (BTN_H - win98.FONT_H) // 2, DARK, FACE, bold=i == current,
                   align="center")
    x, y = _cell(len(STATIONS))
    win98.button(g, x, y, BTN_W, BTN_H, "Aus")
    win98.button(g, 4, VOL_Y, 60, 40, "-", bold=True)
    win98.button(g, w - 64, VOL_Y, 60, 40, "+", bold=True)
    win98.text(g, "Lautstärke", w // 2, VOL_Y + 1, DARK, FACE, align="center")
    win98.bevel(g, 70, VOL_Y + 20, w - 140, 16, raised=False)
    for i in range(volume * (w - 146) // 100 // 7):  # Blöcke wie bei Windows 98
        g.fillRect(73 + i * 7, VOL_Y + 23, 5, 10, win98.NAVY)


def run(ctx):
    current, started = None, None  # laufender Sender; wann er gestartet wurde, solange er noch verbindet
    note = "Such da an Sender aus" if ctx.online() else NO_WIFI
    dirty = True
    while ctx.update():
        what = hit(*ctx.tap) if ctx.tap else None
        if what:
            dirty = True
            if what[0] == "station":
                name, url = STATIONS[what[1]]
                if not ctx.online():
                    note = NO_WIFI
                else:  # play() wartet bis zu 3,5 s, bis der Sender läuft; solange soll man sehen, dass etwas passiert
                    note = "Verbind mi mit %s ..." % name
                    draw(ctx.screen, ctx.W, what[1], note, ctx.volume())
                    ctx.show()
                    if ctx.play(url):
                        current, started = what[1], time.ticks_ms()
                    else:
                        current, started, note = None, None, "%s geht grod net" % name
            elif what[0] == "off":
                ctx.stop()
                current, started, note = None, None, "Aus is."
            else:
                ctx.volume(ctx.volume() + (STEP if what[0] == "up" else -STEP))
        if started is not None:
            if ctx.playing():
                started, note, dirty = None, "Spült grod: " + STATIONS[current][0], True
            elif time.ticks_diff(time.ticks_ms(), started) > WAIT_MS:
                started, note, dirty = None, "%s meldt si net" % STATIONS[current][0], True
        if dirty:
            draw(ctx.screen, ctx.W, current, note, ctx.volume())
            ctx.show()
            dirty = False
