"""Selbsttest am PC: python tests/test_slideshow.py
Die App Diashow: Bilder auf der Karte finden, Dateikopf lesen (progressive JPEGs fallen heraus), einpassen,
nicht zeichenbare Bilder überspringen. Die Probebilder entstehen hier mit Pillow in einem temporären Ordner."""
import json
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

with open(os.path.join(ROOT, "apps", "manifest.json"), encoding="utf-8") as f:
    apps = json.load(f)
assert next(a for a in apps if a["id"] == "slideshow").get("beside") is None  # bildschirmfüllend
assert len(apps) <= 3  # mehr zeigt der Desktop nicht (das vierte Symbol ist „Agent“)

card = tempfile.mkdtemp()
os.makedirs(os.path.join(card, "DCIM", "Camera"))
os.makedirs(os.path.join(card, ".thumbnails"))
os.makedirs(os.path.join(card, "System Volume Information"))
Image.new("RGB", (2000, 1500), "blue").save(os.path.join(card, "DCIM", "Camera", "IMG_0001.jpg"), quality=70)
exif = Image.Exif()
exif[0x0110] = "Kamera"  # ein APP1-Abschnitt vor dem Bildkopf, wie bei echten Fotos
Image.new("RGB", (640, 480), "green").save(os.path.join(card, "mit_exif.JPG"), exif=exif)
Image.new("RGB", (1200, 1600), "red").save(os.path.join(card, "whatsapp.jpg"), progressive=True)
Image.new("RGB", (600, 900), "purple").save(os.path.join(card, "hoch.png"))
for name in ("video.mp4", "IMG_2041.MOV", "notiz.txt"):
    open(os.path.join(card, name), "wb").write(b"\x00" * 64)
open(os.path.join(card, "kaputt.jpg"), "wb").write(b"kein Bild")
Image.new("RGB", (10, 10)).save(os.path.join(card, ".thumbnails", "klein.jpg"))
Image.new("RGB", (10, 10)).save(os.path.join(card, "System Volume Information", "x.jpg"))

# Finden: nur JPG/JPEG/PNG, auch in Unterordnern, sortiert; Versteckte, Windows-Ordner und Videos nicht
found = pictures.find(card)
names = [p[len(card) + 1:].replace("\\", "/") for p in found]
assert names == ["DCIM/Camera/IMG_0001.jpg", "hoch.png", "kaputt.jpg", "mit_exif.JPG", "whatsapp.jpg"], names

# Dateikopf: Größe, oder None, wenn das Gerät es nicht zeichnen kann
sizes = {n: pictures.size(open(p, "rb").read(), p) for n, p in zip(names, found)}
assert sizes == {"DCIM/Camera/IMG_0001.jpg": (2000, 1500), "hoch.png": (600, 900), "kaputt.jpg": None,
                 "mit_exif.JPG": (640, 480), "whatsapp.jpg": None}, sizes

# Einpassen: ganz sichtbar, mittig, Seitenverhältnis bleibt
W, H = 320, 218  # Zeichenfläche einer bildschirmfüllenden App
for w, h in ((2000, 1500), (600, 900), (320, 218), (100, 50), (6387, 4258)):
    x, y, k = pictures.fit(w, h, W, H)
    assert x >= 0 and y >= 0 and w * k <= W + 0.01 and h * k <= H + 0.01
    assert abs(w * k - W) < 1 or abs(h * k - H) < 1  # füllt eine Richtung ganz aus
    assert abs(x - (W - int(w * k)) // 2) <= 1 and abs(y - (H - int(h * k)) // 2) <= 1


class Screen:
    """Zeichenfläche, die sich merkt, welche Bilder gezeichnet wurden (als Daten, nie als Pfad auf der Karte)."""
    def __init__(self):
        self.drawn = []

    def drawJpg(self, data, *a):
        assert isinstance(data, bytes)  # Karte und Display teilen Leitungen: nur aus dem Speicher zeichnen
        self.drawn.append(data)

    drawPng = drawJpg

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


# Weiterschalten überspringt, was nicht geht, in beide Richtungen und rundherum; merkt sich die Nieten
ctx, cant = Ctx(), set()
order = []
i = -1
for _ in range(4):
    i = slideshow.advance(ctx, found, i, 1, cant)
    order.append(names[i])
assert order == ["DCIM/Camera/IMG_0001.jpg", "hoch.png", "mit_exif.JPG", "DCIM/Camera/IMG_0001.jpg"], order
assert {names[found.index(p)] for p in cant} == {"kaputt.jpg", "whatsapp.jpg"}
assert names[slideshow.advance(ctx, found, 0, -1, cant)] == "mit_exif.JPG"
nothing = [os.path.join(card, "whatsapp.jpg"), os.path.join(card, "kaputt.jpg")]
assert slideshow.advance(Ctx(), nothing, -1, 1, set()) is None
# Geht nur ein Bild, bleibt es stehen: einmal zeichnen, danach nicht mehr (große Fotos brauchen Sekunden)
one, alone = Ctx(), nothing + [found[0]]
i = slideshow.advance(one, alone, -1, 1, set())
assert alone[i] == found[0] and slideshow.advance(one, alone, i, 1, set()) == i and one.screen.drawn == [open(found[0], "rb").read()]
assert Card.open == 0
shutil.rmtree(card)
print("ok")
