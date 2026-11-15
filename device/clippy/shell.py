# Die Desktop-Oberfläche: Taskleiste mit Start-Knopf und Uhr, Symbole, Startmenü.
from clippy import win98
from clippy.win98 import DARK, FACE, H, LIGHT, NAVY, W

TASKBAR_H = 28
TASKBAR_Y = H - TASKBAR_H
ICON_W, ICON_H = 68, 50      # Zelle eines Symbols; die Symbole stehen in einer Spalte am linken Rand
MENU_W, ENTRY_H = 150, 38    # Startmenü: Breite und Höhe eines Eintrags


AGENT_COLORS = {"working": (0xFFE000, DARK), "waiting": (0xE02020, 0xFFFFFF), "done": (0x20A020, 0xFFFFFF)}


def agents(g, x_end, states):
    # Kästchen je Coding-Agent, rechtsbündig bis x_end: Kürzel auf der Farbe des Zustands (docs/agent-hooks.md)
    y = TASKBAR_Y + 4
    g.fillRect(x_end - 4 * 24, y, 4 * 24, 21, FACE)  # Platz für höchstens vier, vorher leeren
    for i, (short, state) in enumerate(states[:4]):
        bg, fg = AGENT_COLORS.get(state, (FACE, DARK))
        x = x_end - (i + 1) * 24
        win98.bevel(g, x, y, 22, 21, raised=False)
        g.fillRect(x + 2, y + 2, 18, 17, bg)
        win98.text(g, short, x + 11, y + 3, fg, bg, align="center")


def wifi_sign(g, cx, by):
    # WLAN-Zeichen: drei Bögen über einem Punkt; (cx, by) ist der Punkt unten in der Mitte
    for r in (4, 7, 10):
        g.fillArc(cx, by, r - 1, r, 225, 315, DARK)
    g.fillCircle(cx, by - 1, 1, DARK)


def tray(g, hhmm, battery, charging, online=False, agent_states=()):
    # Versenktes Feld rechts: Akku-Symbol, Prozent, WLAN-Zeichen (nur verbunden), Uhr; links davon die Agents
    w = 128
    x, y = W - 3 - w, TASKBAR_Y + 4
    agents(g, x - 3, agent_states)
    win98.bevel(g, x, y, w, 21, raised=False)
    bx, by = x + 5, y + 5
    g.drawRect(bx, by, 17, 10, DARK)
    g.fillRect(bx + 17, by + 3, 2, 4, DARK)
    g.fillRect(bx + 2, by + 2, max(1, battery * 13 // 100), 6, 0xC00000 if battery < 20 else 0x008000)
    if charging:  # kleiner Blitz
        g.drawLine(bx + 10, by + 1, bx + 6, by + 5, 0xFFE000)
        g.drawLine(bx + 6, by + 5, bx + 10, by + 5, 0xFFE000)
        g.drawLine(bx + 10, by + 5, bx + 6, by + 9, 0xFFE000)
    win98.text(g, "%d%%" % battery, x + 26, y + 3, DARK, FACE)
    if online:
        wifi_sign(g, x + 73, y + 16)
    win98.text(g, hhmm, x + w - 5, y + 3, DARK, FACE, align="right")


def taskbar(g, hhmm, battery, charging, online=False, agent_states=()):
    g.fillRect(0, TASKBAR_Y, W, TASKBAR_H, FACE)
    g.drawLine(0, TASKBAR_Y + 1, W, TASKBAR_Y + 1, LIGHT)
    win98.bevel(g, 2, TASKBAR_Y + 4, 22 + win98.text_width(g, "Start", bold=True) + 6, 22)  # Breite folgt der Schrift
    # Fähnchen aus vier Farbfeldern
    for dx, dy, c in ((0, 0, 0xE02020), (7, 0, 0x20A020), (0, 7, 0x2040E0), (7, 7, 0xE0C000)):
        g.fillRect(7 + dx, TASKBAR_Y + 9 + dy, 6, 6, c)
    win98.text(g, "Start", 24, TASKBAR_Y + 8, DARK, FACE, bold=True)
    tray(g, hhmm, battery, charging, online, agent_states)


def icon(g, index, name, color, letters):
    # Symbol 32×32 mit zwei Buchstaben, darunter der Name
    x, y = 4, 8 + index * ICON_H
    ix = x + 16
    g.fillRect(ix, y, 32, 32, color)
    g.drawRect(ix, y, 32, 32, DARK)
    g.drawLine(ix + 1, y + 1, ix + 30, y + 1, LIGHT)
    g.drawLine(ix + 1, y + 1, ix + 1, y + 30, LIGHT)
    win98.text(g, letters, x + 32, y + 9, LIGHT, color, bold=True, align="center")
    win98.label(g, name, x + 32, y + 34)


def hit(x, y, icons):
    """Was liegt am Desktop unter dem Finger? "start", die Nummer eines Symbols oder None."""
    if y >= H - 40 and x < 70:  # der Start-Knopf reagiert großzügiger, als er gezeichnet ist
        return "start"
    if x < ICON_W and y < TASKBAR_Y and (y - 8) // ICON_H < icons:
        return max(0, (y - 8) // ICON_H)
    return None


def menu(g, entries):
    # Startmenü über dem Start-Knopf, links der blaue Streifen
    h = len(entries) * ENTRY_H + 6
    y = TASKBAR_Y - h
    win98.bevel(g, 2, y, MENU_W, h)
    g.fillRect(5, y + 3, 20, h - 6, NAVY)
    for i, entry in enumerate(entries):
        win98.text(g, entry, 34, y + 3 + i * ENTRY_H + (ENTRY_H - win98.FONT_H) // 2, DARK, FACE)
        if i:
            g.drawLine(28, y + 3 + i * ENTRY_H, MENU_W - 3, y + 3 + i * ENTRY_H, win98.SHADOW)


def menu_hit(x, y, entries):
    """Nummer des getroffenen Menüeintrags oder None."""
    top = TASKBAR_Y - len(entries) * ENTRY_H - 3
    if 2 <= x < 2 + MENU_W and top <= y < TASKBAR_Y:
        return min(len(entries) - 1, (y - top) // ENTRY_H)
    return None
