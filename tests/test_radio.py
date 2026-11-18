"""Selbsttest am PC: python tests/test_radio.py
Die Sender der App Radio und ihre Tippflächen."""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "device"))
sys.path.insert(0, os.path.join(ROOT, "apps", "radio"))
import app as radio
from stations import STATIONS

assert all(url.startswith("http://") for _, url in STATIONS)  # https kann der Player der Firmware nicht
assert 1 <= len(STATIONS) <= 5 and len({name for name, _ in STATIONS}) == len(STATIONS)

# Jeder Knopf trifft sich selbst, „Aus“ kommt nach den Sendern, - und + am Rand der Lautstärke-Reihe
for i in range(len(STATIONS)):
    x, y = radio._cell(i)
    assert radio.hit(x + 10, y + 10) == ("station", i) and radio.hit(x + radio.BTN_W - 1, y + radio.BTN_H - 1) == ("station", i)
x, y = radio._cell(len(STATIONS))
assert radio.hit(x + 1, y + 1) == ("off",)
assert radio.hit(10, radio.VOL_Y + 5) == ("down",) and radio.hit(310, radio.VOL_Y + 39) == ("up",)
assert radio.hit(160, radio.VOL_Y + 5) is None and radio.hit(160, 10) is None

# Alles bleibt im Fenster (320 × 218) und die Reihen überlappen sich nicht
assert radio.VOL_Y + 40 <= 218 and radio._cell(len(STATIONS))[1] + radio.BTN_H <= radio.VOL_Y
assert radio._cell(1)[0] + radio.BTN_W <= 320
print("ok")
