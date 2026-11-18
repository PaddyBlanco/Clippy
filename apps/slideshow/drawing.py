# Was die Diashow auf den Bildschirm bringt: ein Foto von der Karte, ein paar Zeilen Text, eine Zeile unten.
# Fotos von der Karte zeigt sie, so gut die Firmware es kann (docs/device.md).
import os

import pictures
from clippy import win98
from clippy.win98 import LIGHT

BLACK = 0x000000
BIG = 400000            # ab so vielen Bytes dauert das Zeichnen spürbar: vorher „I lad grod ...“ zeigen
MAX_BYTES = 3000000     # größere Dateien liest sie gar nicht (das allein dauert schon 15 s)
HEAD = 131072           # so viel vom Anfang reicht, um den Bildkopf zu finden (auch hinter großen EXIF-Daten)


def say(ctx, lines):
    """Ein paar Zeilen weiß auf schwarz, mittig."""
    g = ctx.screen
    g.fillScreen(BLACK)
    top = (ctx.H - len(lines) * (win98.FONT_H + 4)) // 2
    for n, line in enumerate(lines):
        win98.text(g, line, ctx.W // 2, top + n * (win98.FONT_H + 4), LIGHT, BLACK, align="center")
    ctx.show()


def banner(ctx, text):
    """Eine Zeile unten über dem Bild."""
    g, w, h = ctx.screen, ctx.W, ctx.H
    g.fillRect(0, h - win98.FONT_H - 4, w, win98.FONT_H + 4, BLACK)
    win98.text(g, text, w // 2, h - win98.FONT_H - 2, LIGHT, BLACK, align="center")
    ctx.show()


def draw(ctx, path):
    """Zeichnet ein Bild. False, wenn das Gerät es nicht kann (zu groß, progressives JPEG, kaputt).
    Erst lesen (Leitungen bei der Karte), dann aus dem Speicher zeichnen (Leitungen beim Display)."""
    with ctx.card():
        n = os.stat(path)[6]
        with open(path, "rb") as f:
            head = f.read(HEAD)  # erst nur der Anfang: kann das Gerät das Bild überhaupt?
    if n > MAX_BYTES or pictures.size(head, path) is None:
        return False
    if n > BIG:  # großes Foto: Lesen und Zeichnen halten alles an, bis zu einigen Sekunden
        banner(ctx, "I lad grod a großes Büdl ...")
    try:
        with ctx.card():
            with open(path, "rb") as f:
                data = f.read()
    except MemoryError:  # passt nicht in den Speicher: auslassen
        return False
    got = pictures.size(data, path)
    if got is None:
        return False
    g, w, h = ctx.screen, ctx.W, ctx.H
    x, y, k = pictures.fit(got[0], got[1], w, h)
    g.fillScreen(BLACK)
    if path.lower().endswith(".png"):
        g.drawPng(data, x, y, w, h, 0, 0, k, k)
    else:
        g.drawJpg(data, x, y, w, h, 0, 0, k, k)
    ctx.show()
    return True
