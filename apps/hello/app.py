# Beispiel und Vorlage für eine App: zählt, wie oft getippt wurde.
from clippy import win98


def run(ctx):
    count = 0
    while ctx.update():          # False, sobald das Fenster über das X geschlossen wurde
        if ctx.tap:              # (x, y) des Tippers oder None
            count += 1
            ctx.tone(880, 60)
        g = ctx.screen           # Zeichenfläche der App, ctx.W × ctx.H Pixel
        g.fillScreen(win98.FACE)
        win98.text(g, "Griaß di! Tipp irgendwo hin.", ctx.W // 2, 60, win98.DARK, win98.FACE, align="center")
        win98.text(g, "Getippt: %d" % count, ctx.W // 2, 100, win98.DARK, win98.FACE, bold=True, align="center")
        ctx.show()               # Zeichenfläche aufs Display bringen
