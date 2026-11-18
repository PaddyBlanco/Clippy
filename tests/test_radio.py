"""Selbsttest am PC: python tests/test_radio.py
Die Sender der App Radio, ihre Tippflächen im Fenster neben der Klammer und der Tanz."""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "device"))
sys.path.insert(0, os.path.join(ROOT, "apps", "radio"))
import app as radio
from stations import STATIONS

W, H = 190, 188  # Zeichenfläche im Fenster neben der Klammer (app_context.BESIDE ohne Rahmen)

assert all(url.startswith("http://") for _, url in STATIONS)  # https kann der Player der Firmware nicht
assert 1 <= len(STATIONS) <= 5 and len({name for name, _ in STATIONS}) == len(STATIONS)
with open(os.path.join(ROOT, "apps", "manifest.json"), encoding="utf-8") as f:
    assert next(a for a in json.load(f) if a["id"] == "radio").get("beside") is True

# Jeder Knopf trifft sich selbst, „Aus“ kommt nach den Sendern, - und + am Rand der Lautstärke-Reihe
for i in range(len(STATIONS)):
    x, y = radio._cell(i)
    assert radio.hit(x + 10, y + 10) == ("station", i) and radio.hit(x + radio.BTN_W - 1, y + radio.BTN_H - 1) == ("station", i)
x, y = radio._cell(len(STATIONS))
assert radio.hit(x + 1, y + 1) == ("off",)
assert radio.hit(10, radio.VOL_Y + 5, W) == ("down",) and radio.hit(W - 1, radio.VOL_Y + 39, W) == ("up",)
assert radio.hit(W // 2, radio.VOL_Y + 5, W) is None and radio.hit(W // 2, 10, W) is None

# Alles bleibt im Fenster, Tippflächen mindestens 40 hoch, die Reihen überlappen sich nicht
assert radio.BTN_H >= 40 and radio.VOL_Y + radio.BTN_H <= H
assert radio.SHOW_H <= radio.GRID_Y and radio._cell(len(STATIONS))[1] + radio.BTN_H <= radio.VOL_Y
assert radio._cell(1)[0] + radio.BTN_W <= W

# Der Tanz bleibt im Feld: nie kippen nach links (lean > 0) oder rollen, sonst bräuchte er die Bühne übers Fenster
from clippy.pet import dance
for figure in (dance.sway, dance.hop, dance.groove):
    poses = list(figure())
    assert len(poses) >= 40 and all(p["lean"] <= 0 and p["roll"] == 0 for p in poses), figure
print("ok")
