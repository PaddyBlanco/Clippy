"""Selbsttest am PC: python tests/test_slideshow_menu.py
Menü der Diashow (Tipper in die Mitte): Knöpfe, Rückfrage vor dem Löschen, Löschen nur nach „Ja“, Fotos vom Handy.
Die Probebilder entstehen hier mit Pillow in einem temporären Ordner."""
import os
import shutil
import sys
import tempfile

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "device"))
sys.path.insert(0, os.path.join(ROOT, "apps", "slideshow"))
import app as slideshow
import pictures

W, H = 320, 218  # Zeichenfläche einer bildschirmfüllenden App


class Screen:
    """Zeichenfläche, die sich merkt, welche Bilder gezeichnet wurden."""
    def __init__(self):
        self.drawn = []

    def drawJpg(self, data, *a):
        self.drawn.append(data)

    def __getattr__(self, name):
        return lambda *a, **k: None


class Card:
    """Wie ctx.card(): zählt, dass jeder Kartenzugriff in einem with-Block steht."""
    open = 0

    def __enter__(self):
        Card.open += 1

    def __exit__(self, *exc):
        Card.open -= 1


class Ctx:
    W, H = W, H

    def __init__(self):
        self.screen = Screen()

    def card(self):
        return Card()

    def show(self):
        pass


# Menü und Rückfrage: Knöpfe groß genug, ganz in der Zeichenfläche, jeder trifft sich selbst
import menu
from clippy import win98
win98.text = lambda *a, **k: None  # die Geräte-Schrift gibt es am PC nicht
for kind in (menu.MENU, menu.CONFIRM):
    for key, _, x, y, w, h in menu.buttons(kind):
        assert w >= 40 and h >= 40 and x >= 0 and y >= 0 and x + w <= W and y + h <= H, (key, x, y, w, h)
        assert menu.hit(kind, (x + w // 2, y + h // 2)) == key
    assert menu.hit(kind, (2, 2)) is None


class Tapping(Ctx):
    """Ctx mit Tippern der Reihe nach, je Durchlauf von update() einer."""
    def __init__(self, taps):
        super().__init__()
        self.taps, self.tap = list(taps), None

    def update(self):
        self.tap = self.taps.pop(0) if self.taps else None
        return True


def middle(kind, key):
    return next((x + w // 2, y + h // 2) for k, _, x, y, w, h in menu.buttons(kind) if k == key)


# Löschen: erst nach „Ja“, dann ist genau das gezeigte Bild weg und das nächste kommt
album = tempfile.mkdtemp()
for name, color in (("a.jpg", "red"), ("b.jpg", "green"), ("c.jpg", "blue")):
    Image.new("RGB", (64, 48), color).save(os.path.join(album, name))
pics = pictures.find(album)
no = Tapping([middle(menu.MENU, "delete"), middle(menu.CONFIRM, "no")])
assert slideshow.choose(no, album, pics, 1, set()) == (1, pics) and len(os.listdir(album)) == 3
assert no.screen.drawn == [open(pics[1], "rb").read()]  # „Na“: dasselbe Bild wieder
back = Tapping([(5, 5)])  # daneben getippt: zurück zum Bild
assert slideshow.choose(back, album, pics, 1, set()) == (1, pics) and len(os.listdir(album)) == 3
c_data = open(pics[2], "rb").read()
yes = Tapping([middle(menu.MENU, "delete"), middle(menu.CONFIRM, "yes")])
i, left = slideshow.choose(yes, album, pics, 1, set())
assert sorted(os.listdir(album)) == ["a.jpg", "c.jpg"] and left[i].endswith("c.jpg") and yes.screen.drawn == [c_data]
i, left = slideshow.choose(Tapping([middle(menu.MENU, "delete"), middle(menu.CONFIRM, "yes")]), album, left, 1, set())
assert os.listdir(album) == ["a.jpg"] and left[i].endswith("a.jpg")  # das letzte gelöscht: vorn weiter
i, left = slideshow.choose(Tapping([middle(menu.MENU, "delete"), middle(menu.CONFIRM, "yes")]), album, left, 0, set())
assert os.listdir(album) == [] and left == []  # nichts mehr da: „Auf da Kartn san no ka Büdl.“
phone = Tapping([middle(menu.MENU, "phone")])
phone.photos_from_phone = lambda folder: phone.taps.append(folder)
assert slideshow.choose(phone, album, [os.path.join(album, "x.jpg")], 0, set()) == (-1, None)
assert phone.taps == [album + "/" + slideshow.FOLDER]  # Fotos vom Handy, danach neu suchen
assert Card.open == 0
shutil.rmtree(album)
print("ok")
