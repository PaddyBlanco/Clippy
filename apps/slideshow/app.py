# Diashow: zeigt die Bilder von der microSD-Karte nacheinander, bildschirmfüllend, alle 6 Sekunden das nächste.
# Tippen rechts: nächstes Bild, links: voriges, Mitte: Menü (Fotos vom Handy schicken, dieses Bild löschen).
# Videos übergeht sie. Zeichnen: drawing.py, Menü und Rückfrage: menu.py.
import os
import sys
import time

import menu
import pictures
from drawing import banner, draw, say

SHOW_MS = 6000          # so lange bleibt ein Bild stehen
FOLDER = "Clippy-Bilder"  # hierher schickt das Handy die Fotos
NO_CARD = ["Ka Kartn drin, oder i kann's net lesen.", "Steck a microSD-Kartn eini (FAT32).",
           "Wia's geht, steht im Handbuch.", "Tipp, dann schau i nochmal."]
NO_PICS = ["Auf da Kartn san no ka Büdl.", "Tipp, dann schick ma Fotos", "vom Handy, übers WLAN."]
CANT = ["Die Büdl kann i so net zeign.", "Tipp, dann schick's ma vom Handy,", "dann mach i's passend."]
CARD_ERROR = ["Hoppla, die Kartn mog grod net.", "Steckt's no richtig drin?", "Tipp, dann schau i nochmal."]
HINT = "In d'Mittn tippn: Menü (Fotos, löschn)"


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


def advance(ctx, pics, i, step, cant, again=False):
    """Geht von i aus in Richtung step zum nächsten Bild, das sich zeichnen lässt. Liefert dessen Nummer, oder
    None, wenn keines geht. cant: Pfade, die schon einmal nicht gingen, werden gleich übersprungen.
    Geht nur das Bild, das schon zu sehen ist, bleibt es stehen, statt neu gezeichnet zu werden.
    again: Bild i ist gerade nicht zu sehen (Menü darüber) und kommt als letztes auch dran."""
    shown = None if again else i
    for _ in range(len(pics)):
        i = (i + step) % len(pics)
        if i == shown:
            return i
        if pics[i] not in cant:
            if draw(ctx, pics[i]):
                return i
            cant.add(pics[i])
    return None


def choose(ctx, root, pics, i, cant):
    """Menü über Bild i. Liefert (i, pics) für danach: pics None heißt neu suchen, [] heißt es steht schon da,
    warum nichts mehr geht. Gelöscht wird erst nach „Ja“, und dann ganz (kein Papierkorb)."""
    got = menu.ask(ctx, menu.MENU)
    if got == "phone":
        ctx.photos_from_phone(root + "/" + FOLDER)
        return -1, None
    if got == "delete" and menu.ask(ctx, menu.CONFIRM) == "yes":
        with ctx.card():
            os.remove(pics[i])
        del pics[i]
        if not pics:
            say(ctx, NO_PICS)
            return -1, pics
        i = advance(ctx, pics, i - 1, 1, cant, again=True)  # das nächste; das bisher nächste rückt auf i
        if i is None:
            say(ctx, CANT)
            return -1, []
        return i, pics
    if not draw(ctx, pics[i]):  # Zruck, Na oder daneben: das Bild wieder zeigen
        cant.add(pics[i])
    return i, pics


def run(ctx):
    root, pics, i, due, cant = None, None, -1, 0, set()
    while ctx.update():
        tap = ctx.tap
        try:
            if pics is None:  # zu Beginn und nach dem Empfangen: (neu) suchen
                (root, pics), i, due, cant = scan(ctx), -1, time.ticks_ms(), set()
                continue
            if not pics:
                if tap:  # ohne Karte nochmal schauen, ohne Bilder gleich Fotos vom Handy
                    if root:
                        ctx.photos_from_phone(root + "/" + FOLDER)
                    pics = None
                continue
            step = 0
            if tap and i >= 0 and ctx.W // 3 <= tap[0] < 2 * ctx.W // 3:
                i, pics = choose(ctx, root, pics, i, cant)
                due = time.ticks_add(time.ticks_ms(), SHOW_MS)  # der Takt steht, solange das Menü offen war
                continue
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
