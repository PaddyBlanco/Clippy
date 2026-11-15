# Windows-98-Bausteine: Farben, Schrift und die Grundformen, aus denen alles andere gebaut ist.
# g ist immer das Ziel: M5.Display oder ein Canvas.
import os

TEAL = 0x008080
FACE = 0xC0C0C0
LIGHT = 0xFFFFFF
SHADOW = 0x808080
DARK = 0x000000
NAVY = 0x000080
BLUE = 0x0000AA  # Bluescreen

W, H = 320, 240
TITLE_H = 22     # Titelleiste eines Fensters
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


def wrap(s, width, measure):
    """Bricht s in Zeilen um, die laut measure(zeile) höchstens width breit sind. Zeilenwechsel in s bleiben."""
    lines = []
    for part in s.split("\n"):
        line = ""
        for word in part.split():
            trial = (line + " " + word).strip()
            if line and measure(trial) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


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


def signal(g, x, y, level):
    # Empfang: vier Balken, level davon schwarz
    for i in range(4):
        g.fillRect(x + i * 6, y + 12 - i * 4, 4, 4 + i * 4, DARK if i < level else SHADOW)


def lock(g, x, y):
    # kleines Schloss: Bügel und Körper
    g.drawRoundRect(x + 2, y, 8, 9, 3, DARK)
    g.fillRect(x, y + 6, 12, 9, DARK)


def button(g, x, y, w, h, caption, bold=False):
    bevel(g, x, y, w, h)
    text(g, caption, x + w // 2, y + (h - FONT_H) // 2, DARK, FACE, bold=bold, align="center")


def window(g, title):
    # Bildschirmfüllendes Fenster: blaue Titelleiste mit X, darunter graue Fläche
    g.fillRect(0, 0, W, TITLE_H, NAVY)
    text(g, title, 6, 3, LIGHT, NAVY, bold=True)
    bevel(g, W - 21, 3, 17, 16)
    g.drawLine(W - 16, 7, W - 10, 13, DARK)
    g.drawLine(W - 15, 7, W - 9, 13, DARK)
    g.drawLine(W - 10, 7, W - 16, 13, DARK)
    g.drawLine(W - 9, 7, W - 15, 13, DARK)
    g.fillRect(0, TITLE_H, W, H - TITLE_H, FACE)


def bluescreen(g, app_name, error_text):
    g.fillScreen(BLUE)
    g.fillRect(126, 14, 68, FONT_H + 4, FACE)
    text(g, "Clippy", 160, 16, BLUE, FACE, bold=True, align="center")
    lines = ["Ein schwerer Ausnahmefehler ist in der App", "„%s“ aufgetreten. Die App wurde beendet." % app_name, ""]
    lines += wrap(error_text, W - 20, lambda t: text_width(g, t))[-7:]  # die letzten Zeilen nennen den Fehler
    for i, line in enumerate(lines):
        text(g, line, 10, 44 + i * (FONT_H + 1), LIGHT, BLUE)
    text(g, "Tippen, um zum Desktop zurückzukehren", 160, H - 22, LIGHT, BLUE, align="center")
