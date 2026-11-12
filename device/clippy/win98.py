# Windows-98-Bausteine: Farben und Zeichenfunktionen.
# g ist immer das Ziel: M5.Display oder ein Canvas.
import os

TEAL = 0x008080
FACE = 0xC0C0C0
LIGHT = 0xFFFFFF
SHADOW = 0x808080
DARK = 0x000000
NAVY = 0x000080

W, H = 320, 240
TASKBAR_H = 28
TASKBAR_Y = H - TASKBAR_H
BG_PATH = "/flash/bg.jpg"
FONT = "/flash/res/font12.vlw"
FONT_BOLD = "/flash/res/font12b.vlw"
FONT_H = 15

_fonts = {}  # Schriftdateien im Speicher: Laden aus Bytes kostet 0,2 ms, aus der Datei 9 ms


def _use_font(g, bold):
    path = FONT_BOLD if bold else FONT
    if path not in _fonts:
        with open(path, "rb") as f:
            _fonts[path] = f.read()
    g.loadFont(_fonts[path])


def text_width(g, s, bold=False):
    _use_font(g, bold)
    return g.textWidth(s)


def text(g, s, x, y, color, back, bold=False, align="left"):
    # back = Farbe hinter dem Text. Die Schrift ist geglättet und mischt ihre Kanten damit.
    # back gleich color = kein Hintergrund; das geht nur auf einem Canvas sauber (siehe label).
    _use_font(g, bold)
    g.setTextColor(color, back)
    {"left": g.drawString, "center": g.drawCenterString, "right": g.drawRightString}[align](s, x, y)


def backdrop(c, x, y):
    # Füllt c mit dem Desktop-Ausschnitt ab (x, y): Untergrund für alles, was über dem Foto liegt
    try:
        os.stat(BG_PATH)
        c.drawJpg(BG_PATH, 0, 0, c.width(), c.height(), x, y)
    except OSError:
        c.fillScreen(TEAL)


def label(g, s, cx, y):
    # Weißer Text mit Schatten direkt auf dem Desktop, mittig um cx
    w = text_width(g, s) + 1
    x = max(0, cx - w // 2)
    c = g.newCanvas(w, FONT_H + 1, 16, True)
    backdrop(c, x, y)
    text(c, s, 1, 1, DARK, DARK)
    text(c, s, 0, 0, LIGHT, LIGHT)
    c.push(x, y)
    c.delete()


def bevel(g, x, y, w, h, raised=True):
    # 3D-Kante: erhaben (Knopf) oder versenkt (Anzeigefeld)
    g.fillRect(x, y, w, h, FACE)
    top, bottom = (LIGHT, DARK) if raised else (SHADOW, LIGHT)
    g.drawLine(x, y, x + w - 2, y, top)
    g.drawLine(x, y, x, y + h - 2, top)
    g.drawLine(x, y + h - 1, x + w - 1, y + h - 1, bottom)
    g.drawLine(x + w - 1, y, x + w - 1, y + h - 1, bottom)
    if raised:
        g.drawLine(x + 1, y + h - 2, x + w - 2, y + h - 2, SHADOW)
        g.drawLine(x + w - 2, y + 1, x + w - 2, y + h - 2, SHADOW)


def tray(g, hhmm, battery, charging):
    # Versenktes Feld rechts: Akku-Symbol, Prozent, Uhr
    w = 104
    x, y = W - 3 - w, TASKBAR_Y + 4
    bevel(g, x, y, w, 21, raised=False)
    bx, by = x + 5, y + 5
    g.drawRect(bx, by, 17, 10, DARK)
    g.fillRect(bx + 17, by + 3, 2, 4, DARK)
    g.fillRect(bx + 2, by + 2, max(1, battery * 13 // 100), 6, 0xC00000 if battery < 20 else 0x008000)
    if charging:  # kleiner Blitz
        g.drawLine(bx + 10, by + 1, bx + 6, by + 5, 0xFFE000)
        g.drawLine(bx + 6, by + 5, bx + 10, by + 5, 0xFFE000)
        g.drawLine(bx + 10, by + 5, bx + 6, by + 9, 0xFFE000)
    text(g, "%d%%" % battery, x + 26, y + 3, DARK, FACE)
    text(g, hhmm, x + w - 5, y + 3, DARK, FACE, align="right")


def taskbar(g, hhmm, battery, charging):
    g.fillRect(0, TASKBAR_Y, W, TASKBAR_H, FACE)
    g.drawLine(0, TASKBAR_Y + 1, W, TASKBAR_Y + 1, LIGHT)
    bevel(g, 2, TASKBAR_Y + 4, 22 + text_width(g, "Start", bold=True) + 6, 22)  # Breite folgt der Schrift
    # Fähnchen aus vier Farbfeldern
    for dx, dy, c in ((0, 0, 0xE02020), (7, 0, 0x20A020), (0, 7, 0x2040E0), (7, 7, 0xE0C000)):
        g.fillRect(7 + dx, TASKBAR_Y + 9 + dy, 6, 6, c)
    text(g, "Start", 24, TASKBAR_Y + 8, DARK, FACE, bold=True)
    tray(g, hhmm, battery, charging)


def icon(g, x, y, name, color, letters):
    # Zelle 64 breit: Symbol 32×32 mittig, darunter der Name
    ix = x + 16
    g.fillRect(ix, y, 32, 32, color)
    g.drawRect(ix, y, 32, 32, DARK)
    g.drawLine(ix + 1, y + 1, ix + 30, y + 1, LIGHT)
    g.drawLine(ix + 1, y + 1, ix + 1, y + 30, LIGHT)
    text(g, letters, x + 32, y + 9, LIGHT, color, bold=True, align="center")
    label(g, name, x + 32, y + 36)
