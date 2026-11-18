"""Bilder fürs Handbuch: zeichnet alle Bilder nach manual/img/s<Nr>.png.

    python tools/screenshots.py [zielordner]      (Standard: manual/img)

Läuft beim Veröffentlichen in GitHub Actions (.github/workflows/manual.yml); die Bilder liegen nie im Repo
(AGENTS.md, Regel 4). Welche Nummer was zeigt und woher sie kommt, steht in docs/manual.md.
Die meisten zeichnet tools/preview.py aus den Szenen in tools/screenshot_scenes.py; QR-Codes sind dabei echt, wenn das
Paket qrcode da ist. Gerät (S2) und Handy-Seiten (S22, S27) macht tools/screenshot_extras.py.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

import screenshot_extras
from screenshot_scenes import HEAD, SCENES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "tools", "preview.py")


def probe_photo(folder):
    """Ein freundliches Probefoto (Sonne über Hügeln), damit die Diashow etwas zeigt; entsteht hier, nie im Repo."""
    im = Image.new("RGB", (291, 218), (110, 170, 235))
    g = ImageDraw.Draw(im)
    g.ellipse([190, 30, 250, 90], fill=(255, 215, 60))
    g.ellipse([-60, 130, 200, 330], fill=(70, 150, 70))
    g.ellipse([120, 150, 380, 340], fill=(50, 125, 55))
    g.rectangle([60, 120, 110, 175], fill=(200, 80, 60))
    g.polygon([(52, 122), (85, 90), (118, 122)], fill=(140, 50, 40))
    os.makedirs(os.path.join(folder, "Clippy-Bilder"))
    im.save(os.path.join(folder, "Clippy-Bilder", "Haus.jpg"), quality=90)


def render(name, out, tmp):
    target = os.path.join(out, name + ".png")
    if name == "s1":
        args = [os.path.join(ROOT, "device", "main.py"), target, "3"]
    elif name == "s25":
        card = os.path.join(tmp, "sd")
        probe_photo(card)
        args = [os.path.join(ROOT, "apps", "slideshow", "app.py"), target, "4", "--sd", card]
    else:
        scene = os.path.join(tmp, name + ".py")
        with open(scene, "w", encoding="utf-8") as f:
            f.write("ROOT = %r\n" % ROOT.replace("\\", "/") + HEAD + SCENES[name] + "\n")
        args = [scene, target, "4"]
    run = subprocess.run([sys.executable, PREVIEW] + args, capture_output=True, text=True)
    if run.returncode != 0 or not os.path.exists(target):
        raise SystemExit("%s ging nicht:\n%s%s" % (name, run.stdout, run.stderr))
    print(name, "->", target)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "manual", "img"))
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name in SCENES:
            render(name, out, tmp)
        screenshot_extras.render(out, tmp)  # braucht S1 schon fertig


if __name__ == "__main__":
    main()
