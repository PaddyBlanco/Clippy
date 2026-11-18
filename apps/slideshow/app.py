# Diashow: zeigt die Bilder von der microSD-Karte nacheinander, bildschirmfüllend, alle 6 Sekunden das nächste.
# Tippen rechts: nächstes Bild, links: voriges, Mitte: Fotos vom Handy schicken (landen in Clippy-Bilder).
# Videos übergeht sie. Fotos von der Karte zeigt sie, so gut die Firmware es kann (docs/device.md).
import os
import sys
import time

import pictures
from clippy import win98
from clippy.win98 import LIGHT

BLACK = 0x000000
SHOW_MS = 6000          # so lange bleibt ein Bild stehen
BIG = 400000            # ab so vielen Bytes dauert das Zeichnen spürbar: vorher „I lad grod ...“ zeigen
MAX_BYTES = 3000000     # größere Dateien liest sie gar nicht (das allein dauert schon 15 s)
HEAD = 131072           # so viel vom Anfang reicht, um den Bildkopf zu finden (auch hinter großen EXIF-Daten)
FOLDER = "Clippy-Bilder"  # hierher schickt das Handy die Fotos
NO_CARD = ["Ka Kartn drin, oder i kann's net lesen.", "Steck a microSD-Kartn eini (FAT32).",
           "Wia's geht, steht im Handbuch.", "Tipp, dann schau i nochmal."]
NO_PICS = ["Auf da Kartn san no ka Büdl.", "Tipp, dann schick ma Fotos", "vom Handy, übers WLAN."]
CANT = ["Die Büdl kann i so net zeign.", "Tipp, dann schick's ma vom Handy,", "dann mach i's passend."]
CARD_ERROR = ["Hoppla, die Kartn mog grod net.", "Steckt's no richtig drin?", "Tipp, dann schau i nochmal."]
HINT = "In d'Mittn tippn: Fotos vom Handy"


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


def scan(ctx):
    """Karte einbinden und Bilder suchen. Liefert (Ordner der Karte, Liste); bei leerer Liste steht schon da,
    warum. Ohne Karte ist der Ordner None."""
    say(ctx, ["Schau, wos auf da Kartn is ..."])
    root = ctx.sd()
    if root is None:
        say(ctx, NO_CARD)
        return None, []
    with ctx.card():
        found = pictures.find(root)
    if not found:
        say(ctx, NO_PICS)
    return root, found


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


def advance(ctx, pics, i, step, cant):
    """Geht von i aus in Richtung step zum nächsten Bild, das sich zeichnen lässt. Liefert dessen Nummer, oder
    None, wenn keines geht. cant: Pfade, die schon einmal nicht gingen, werden gleich übersprungen.
    Geht nur das Bild, das schon zu sehen ist, bleibt es stehen, statt neu gezeichnet zu werden."""
    shown = i
    for _ in range(len(pics)):
        i = (i + step) % len(pics)
        if i == shown:
            return i
        if pics[i] not in cant:
            if draw(ctx, pics[i]):
                return i
            cant.add(pics[i])
    return None


def run(ctx):
    root, pics, i, due, cant = None, None, -1, 0, set()
    while ctx.update():
        tap = ctx.tap
        try:
            if pics is None:  # zu Beginn und nach dem Empfangen: (neu) suchen
                (root, pics), i, due, cant = scan(ctx), -1, time.ticks_ms(), set()
                continue
            middle = tap and ctx.W // 3 <= tap[0] < 2 * ctx.W // 3
            if (not pics and tap) or (pics and middle):  # ohne Karte nochmal schauen, sonst Fotos vom Handy
                if root:
                    ctx.photos_from_phone(root + "/" + FOLDER)
                pics = None
                continue
            if not pics:
                continue
            step = 0
            if tap:
                step = -1 if tap[0] < ctx.W // 3 and i >= 0 else 1
            elif time.ticks_diff(time.ticks_ms(), due) >= 0:
                step = 1
            if step:
                first = i < 0
                i = advance(ctx, pics, i, step, cant)
                if i is None:
                    say(ctx, CANT)
                    pics = []
                elif first:
                    banner(ctx, HINT)
                due = time.ticks_add(time.ticks_ms(), SHOW_MS)
        except OSError as e:  # Karte herausgezogen, Lesefehler, Port belegt: sagen, nach einem Tipper neu suchen
            sys.print_exception(e)  # für die USB-Konsole
            say(ctx, CARD_ERROR)
            root, pics = None, []
