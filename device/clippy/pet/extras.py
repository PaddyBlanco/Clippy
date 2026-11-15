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


def around(g, pose, at, ox, w, h, top):
    """Was um sie herum ist: Blitze, Rotzblase, Zs. w, h: Feldgröße; top: Luft über dem Kopf."""
    if pose["spark"]:  # unter Strom: Blitze an zufälligen Stellen
        for _ in range(4):
            x, y = ox + random.randint(4, w - 12), random.randint(6, h - 22)
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
