# Beiwerk zur Zeichnung der Klammer: Hantel, Trommel, Schlägel, Blitze, Rotzblase, Schlaf-Zs.
import math
import random

YELLOW = 0xFFE000
WHITE = 0xFFFFFF


def stick(g, x0, y0, x1, y1, t, c):
    # Dicke Linie mit runden Enden
    dx, dy = x1 - x0, y1 - y0
    n = math.sqrt(dx * dx + dy * dy) or 1
    px, py = -dy * t / 2 / n, dx * t / 2 / n
    g.fillTriangle(int(x0 + px), int(y0 + py), int(x0 - px), int(y0 - py), int(x1 + px), int(y1 + py), c)
    g.fillTriangle(int(x0 - px), int(y0 - py), int(x1 + px), int(y1 + py), int(x1 - px), int(y1 - py), c)
    g.fillCircle(int(x0), int(y0), t // 2, c)
    g.fillCircle(int(x1), int(y1), t // 2, c)


def in_hand(g, pose, at, hand):
    """Was sie in der Hand hält, und die Trommel. at: Punkt der Figur -> Punkt im Bild."""
    hx, hy = at(hand[0], hand[1])
    a = math.radians(pose["arm"])
    if pose["weight"]:  # Hantel quer zum Unterarm
        ux, uy = math.cos(a) * 9, math.sin(a) * 9
        stick(g, hx - ux, hy - uy, hx + ux, hy + uy, 3, 0x707070)
        for s in (-1, 1):
            g.fillCircle(int(hx + s * ux), int(hy + s * uy), 6, 0x202020)
            g.fillCircle(int(hx + s * ux) - 2, int(hy + s * uy) - 2, 1, 0x909090)
    if pose["drum"]:  # kleine Trommel rechts unten
        x, y = at(109, 110)
        g.fillRect(x - 12, y, 25, 14, 0xB03030)
        g.fillEllipse(x, y + 14, 12, 4, 0xB03030)
        g.fillEllipse(x, y, 12, 4, 0x303030)
        g.fillEllipse(x, y, 11, 3, 0xF0F0E0)
    if pose["stick"]:  # Schlägel, im Handgelenk nach unten abgewinkelt
        w = a + math.radians(70)
        stick(g, hx, hy, hx + 16 * math.sin(w), hy - 16 * math.cos(w), 2, 0x8B5A2B)
    if pose["umbrella"]:
        umbrella(g, at, hand)


UMBRELLA_RX, UMBRELLA_RY, UMBRELLA_Y = 40, 22, 1  # Schirmdach: halbe Breite, Höhe, Unterkante (Figur-Punkte)
UMBRELLA_IN = 18   # so weit liegt die Mitte des Dachs links von der Hand: über dem Kopf, nicht über dem Arm
RED, DARK_RED, HANDLE = 0xD03030, 0x801818, 0x404040


def umbrella(g, at, hand):
    """Aufgespannter Schirm: Stock schräg von der Hand hinauf, rotes Dach über dem Kopf."""
    x = hand[0] - UMBRELLA_IN
    stick(g, *at(hand[0], hand[1] + 4), *at(x, UMBRELLA_Y), 2, HANDLE)  # über dem Draht, aber unter Augen und Brauen
    rim = [at(x + UMBRELLA_RX * math.cos(math.radians(d)), UMBRELLA_Y + UMBRELLA_RY * math.sin(math.radians(d)))
           for d in range(180, 361, 15)]                             # Bogen von links über oben nach rechts
    cx, cy = at(x, UMBRELLA_Y)
    for p, q in zip(rim, rim[1:]):
        g.fillTriangle(cx, cy, p[0], p[1], q[0], q[1], RED)
    for p in rim[::3]:                                               # Speichen
        g.drawLine(cx, cy, p[0], p[1], DARK_RED)
    tx, ty = at(x, UMBRELLA_Y - UMBRELLA_RY - 3)
    g.fillCircle(tx, ty, 2, HANDLE)                                  # Spitze


CONSOLE_H = 58                       # Höhe der Konsole oben im Feld; darunter beginnt der Kopf
STAR = (1, 2, 3, 4, 5, 5, 4, 3, 2)  # Größe des Sterns je Bild, wie das Funkeln in Claude Code
GREY, BLACK = 0xC0C0C0, 0x000000


def _star(g, cx, cy, frame, color):
    # achtstrahliger Stern: wächst und schrumpft, abwechselnd sind die geraden oder die schrägen Strahlen länger
    r, twinkle = STAR[frame // 2 % len(STAR)], frame // 9 % 2
    for (dx, dy), long in (((1, 0), 1), ((0, 1), 1), ((1, 1), 0), ((1, -1), 0)):
        k = r if long != twinkle else max(1, r * 2 // 3)
        for o in (0, 1):
            g.drawLine(cx - dx * k + o, cy - dy * k, cx + dx * k + o, cy + dy * k, color)


def _fit(g, options, room):
    """Die erste Fassung, die in room Pixel passt, sonst die letzte."""
    from clippy import win98
    for s in options:
        if win98.text_width(g, s) <= room:
            return s
    return options[-1]


def console(g, c, frame, width):
    """Konsole über dem Kopf wie Claude Code im alten cmd-Fenster. c: siehe pet.agents.Agents.console()."""
    from clippy import win98
    color, h = c["color"], CONSOLE_H
    win98.bevel(g, 0, 0, width, h)                                      # Fensterrahmen
    g.fillRect(2, 2, width - 4, 15, color)                              # Titelleiste in der Farbe des Agents
    title = c["agent"].lower() + (": " + c["project"] if c["project"] else "")
    win98.text(g, _fit(g, (title, c["agent"].lower()), width - 24), 5, 2, 0xFFFFFF, color, bold=True)
    win98.bevel(g, width - 16, 4, 12, 11)                               # Schließen-Knopf
    g.drawLine(width - 13, 7, width - 8, 12, BLACK)
    g.drawLine(width - 8, 7, width - 13, 12, BLACK)
    g.fillRect(2, 18, width - 4, h - 20, BLACK)                         # schwarze Konsole
    _star(g, 10, 28, frame, color)
    word = c["verb"].replace("é", "e")                                  # die Geräte-Schrift hat kein é
    win98.text(g, _fit(g, (word + "…", word), width - 24), 19, 20, color, BLACK)
    s = c["seconds"]
    took = "%ds" % s if s < 60 else "%dm %02ds" % (s // 60, s % 60)
    win98.text(g, _fit(g, (took + " · esc to interrupt", took + " · esc", took), width - 12), 6, 38, GREY, BLACK)


def around(g, pose, at, ox, w, h, top):
    """Was um sie herum ist: Blitze, Rotzblase, Zs. w, h: Feldgröße; top: Luft über dem Kopf."""
    if pose["spark"]:  # unter Strom: Blitze an zufälligen Stellen
        for _ in range(4):
            x, y = ox + random.randint(4, w - 12), random.randint(top - 18, h - 22)  # rund um sie, nicht ganz oben
            for dx in (0, 1):
                g.drawLine(x + 6 + dx, y, x + dx, y + 7, YELLOW)
                g.drawLine(x + dx, y + 7, x + 6 + dx, y + 7, YELLOW)
                g.drawLine(x + 6 + dx, y + 7, x + dx, y + 14, YELLOW)
    if pose["snot"]:  # Rotzblase unter den Augen; snot ist ihr Radius
        r = int(pose["snot"])
        x, y = at(50 + r, 68 + r)
        g.fillCircle(x, y, r, 0xC8ECF4)
        g.drawCircle(x, y, r, 0x5090A8)
        g.fillCircle(x - r // 3, y - r // 3, 1, WHITE)
    for k in range(3 if pose["zzz"] else 0):  # Schlaf: drei Zs steigen auf, wachsen und treiben davon; zzz zählt hoch
        t = (pose["zzz"] + k * 8) % 24
        x, y, n = ox + 56 + t + (t // 3 % 2) * 2, top + 6 - t - t // 4, 3 + t // 4
        for dy in (0, 1):
            g.drawLine(x, y + dy, x + n, y + dy, 0x101060)
            g.drawLine(x + n, y + dy, x, y + n + dy, 0x101060)
            g.drawLine(x, y + n + dy, x + n, y + n + dy, 0x101060)
