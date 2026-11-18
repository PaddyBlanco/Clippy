# Internetradio im Fenster links neben der Klammer (die tanzt dazu): Sender antippen, mit - und + leiser und lauter.
# Das X schließt das Fenster und schaltet das Radio aus. Zeichenfläche 190 × 188 (beside in manifest.json).
import time

from clippy import win98
from clippy.win98 import DARK, FACE
from stations import STATIONS

COLS, BTN_W, BTN_H, GAP = 2, 94, 40, 2  # Senderknöpfe in zwei Spalten, dazu „Aus“
SHOW_H, GRID_Y, VOL_Y = 18, 20, 146     # Höhe der Anzeige oben; erste Reihe der Knöpfe; Reihe für die Lautstärke
VOL_BTN = 44                            # Breite von - und +
STEP, WAIT_MS = 10, 12000               # Schritt der Lautstärke; so lange darf das Verbinden dauern
GREEN = 0x40E040                        # Schrift der Anzeige oben, wie bei einem Radio
NO_WIFI = "Ka WLAN (Startmenü)"


def _cell(i):
    return (i % COLS) * (BTN_W + GAP), GRID_Y + (i // COLS) * (BTN_H + GAP)


def hit(x, y, w=190):
    """Was liegt unter dem Finger: ("station", Nummer), ("off",), ("down",), ("up",) oder None."""
    for i in range(len(STATIONS) + 1):
        cx, cy = _cell(i)
        if cx <= x < cx + BTN_W and cy <= y < cy + BTN_H:
            return ("off",) if i == len(STATIONS) else ("station", i)
    if VOL_Y <= y < VOL_Y + BTN_H:
        if x < VOL_BTN:
            return ("down",)
        if x >= w - VOL_BTN:
            return ("up",)
    return None


def show(ctx, current, note):
    """Zeichnet das Fenster neu und bringt es aufs Display."""
    g, w = ctx.screen, ctx.W
    g.fillScreen(FACE)
    win98.bevel(g, 0, 0, w, SHOW_H, raised=False)  # die Anzeige oben
    g.fillRect(2, 2, w - 4, SHOW_H - 3, DARK)
    win98.text(g, note, w // 2, 2, GREEN, DARK, align="center")
    for i, (name, _) in enumerate(STATIONS):
        x, y = _cell(i)
        win98.bevel(g, x, y, BTN_W, BTN_H, raised=i != current)  # der laufende Sender ist eingedrückt
        win98.text(g, name, x + BTN_W // 2, y + (BTN_H - win98.FONT_H) // 2, DARK, FACE, bold=i == current,
                   align="center")
    x, y = _cell(len(STATIONS))
    win98.button(g, x, y, BTN_W, BTN_H, "Aus")
    win98.button(g, 0, VOL_Y, VOL_BTN, BTN_H, "-", bold=True)
    win98.button(g, w - VOL_BTN, VOL_Y, VOL_BTN, BTN_H, "+", bold=True)
    bar_x, bar_w = VOL_BTN + 4, w - 2 * VOL_BTN - 8
    win98.bevel(g, bar_x, VOL_Y + 12, bar_w, 16, raised=False)
    for i in range(ctx.volume() * (bar_w - 6) // 100 // 7):  # Blöcke wie bei Windows 98
        g.fillRect(bar_x + 3 + i * 7, VOL_Y + 15, 5, 10, win98.NAVY)
    ctx.show()


def run(ctx):
    current, started = None, None  # laufender Sender; wann er gestartet wurde, solange er noch verbindet
    note = "Such da an Sender aus" if ctx.online() else NO_WIFI
    dirty = True
    while ctx.update():
        what = hit(ctx.tap[0], ctx.tap[1], ctx.W) if ctx.tap else None
        if what:
            dirty = True
            if what[0] == "station":
                name, url = STATIONS[what[1]]
                if not ctx.online():
                    note = NO_WIFI
                else:  # play() wartet bis zu 3,5 s, bis der Sender läuft; solange soll man sehen, dass etwas passiert
                    note = "Verbind mi mit %s ..." % name
                    show(ctx, what[1], note)
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
            show(ctx, current, note)
            dirty = False
