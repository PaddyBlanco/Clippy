# Karten-Probe: python -m mpremote connect COM4 resume run checks/sdcard.py  (direkt nach einem Neustart)
# Prüft ohne hinzuschauen, ob das Display nach dem Einbinden der microSD-Karte noch seine Leitungen hat: Karte und
# Display teilen sich G35, G36, G37 (docs/device.md). Erwartet überall "True". Liest ein Bild, schreibt nichts.
import os

import M5
from machine import mem32

M5.begin()
OUT_SEL, EN1 = 0x60004554, 0x6000402C


def wiring():
    return [(p, mem32[OUT_SEL + 4 * p] & 0x1FF, bool(mem32[EN1] & (1 << (p - 32)))) for p in (35, 36, 37)]


M5.Display.fillScreen(0x202020)
display = wiring()
from clippy import sdcard  # noqa: E402  (erst nach M5.begin)

root = sdcard.mount()
print("karte:", root, "| danach Leitungen beim Display:", wiring() == display)
if root:
    with sdcard.access():
        inside = wiring()
        names = [n for n in os.listdir(root) if n.lower().endswith((".jpg", ".jpeg"))]
        for folder in ("Clippy-Bilder",):
            if folder in os.listdir(root):
                names += [folder + "/" + n for n in os.listdir(root + "/" + folder)]
        data = open(root + "/" + names[0], "rb").read() if names else b""
    print("im Block bei der Karte:", inside != display, "| gelesen:", len(data), "Bytes", data[:2])
    print("danach beim Display:", wiring() == display)
    if data[:2] == b"\xff\xd8":
        M5.Display.fillScreen(0)
        M5.Display.drawJpg(data, 0, 0)
        print("Foto gezeichnet; Leitungen beim Display:", wiring() == display, "(am Display sollte es zu sehen sein)")
