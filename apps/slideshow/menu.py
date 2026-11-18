# Menü der Diashow (Tipper in die Mitte) und die Rückfrage vor dem Löschen: zeichnen, auf einen Tipper warten,
# sagen, welcher Knopf es war. Was dann passiert, entscheidet app.py.
from clippy import win98
from clippy.win98 import DARK, FACE, LIGHT, NAVY

BOX = (40, 19, 240, 180)  # Kasten über dem Bild: x, y, Breite, Höhe in der Zeichenfläche 320 × 218
MENU = ("Diashow", (), (("phone", "Fotos vom Handy"), ("delete", "Des Büdl löschn"), ("back", "Zruck")))
CONFIRM = ("Löschn?", ("Des Büdl wirklich löschn?", "Is dann ganz weg."), (("yes", "Ja, weg damit"), ("no", "Na")))


def buttons(kind):
    """Knöpfe als [(Aktion, Beschriftung, x, y, Breite, Höhe)]: im Menü untereinander, bei Fragen nebeneinander."""
    x, y, w, h = BOX
    _, lines, choices = kind
    if lines:
        bw = (w - 28) // len(choices)
        return [(key, caption, x + 10 + n * (bw + 8), y + h - 56, bw, 44) for n, (key, caption) in enumerate(choices)]
    return [(key, caption, x + 12, y + 30 + n * 50, w - 24, 42) for n, (key, caption) in enumerate(choices)]


def show(ctx, kind):
    """Zeichnet MENU oder CONFIRM über das Bild und bringt es aufs Display."""
    g = ctx.screen
    x, y, w, h = BOX
    title, lines, _ = kind
    win98.bevel(g, x, y, w, h)
    g.fillRect(x + 2, y + 2, w - 4, win98.PANEL_TITLE_H - 2, NAVY)
    win98.text(g, title, x + 7, y + 4, LIGHT, NAVY, bold=True)
    for n, line in enumerate(lines):
        win98.text(g, line, x + w // 2, y + 40 + n * 22, DARK, FACE, align="center")
    for _, caption, bx, by, bw, bh in buttons(kind):
        win98.button(g, bx, by, bw, bh, caption, bold=True)
    ctx.show()


def hit(kind, tap):
    """Aktion des getippten Knopfs, oder None (daneben)."""
    for key, _, x, y, w, h in buttons(kind):
        if tap and x <= tap[0] < x + w and y <= tap[1] < y + h:
            return key
    return None


def ask(ctx, kind):
    """Zeigt kind und wartet auf einen Tipper. Liefert dessen Aktion; None: daneben getippt oder Fenster zu."""
    show(ctx, kind)
    while ctx.update():
        if ctx.tap:
            return hit(kind, ctx.tap)
    return None
