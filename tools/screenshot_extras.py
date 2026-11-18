"""Bilder fürs Handbuch, die nicht aus der Vorschau kommen (tools/screenshots.py ruft das hier auf):

    S2   das Gerät: ein gezeichnetes CoreS3-Gehäuse, darin der Desktop aus S1
    S22  Handy: Seite „WLAN einrichten“ (device/clippy/portal_page.py)
    S27  Handy: Seite „Fotos an Clippy“ (device/clippy/photo_page.py), so als wären drei Fotos geschickt

Die Handy-Seiten fotografiert Headless Chrome (in GitHub Actions dabei). Fehlt Chrome am PC, fehlen nur diese zwei;
in Actions (Umgebungsvariable CI) bricht das Fehlen ab.
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

from screenshot_scenes import NETS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMES = ("google-chrome", "chromium", "chromium-browser", "C:/Program Files/Google/Chrome/Application/chrome.exe",
           "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
PHONE = (390, 640)  # Bildschirm eines Handys in CSS-Pixeln: Breite, Höhe
# S27: die Liste so füllen, wie sie nach drei geschickten Fotos aussieht (line und list sind aus der Seite)
SENT = ('<script>list.innerHTML = ""; ["IMG_2041.HEIC", "IMG_2042.HEIC", "Urlaub am See.jpg"].forEach(function (n) '
        '{ line("\\u2713 " + n); }); line("3 Fotos bei Clippy. Du kannst noch mehr schicken.");</script>')


def device(screen, target):
    """S2: Gehäuse auf hellem Tisch, mit Schatten; screen ist S1 (doppelt so groß wie das Display)."""
    w, h = 480, 430
    im = Image.new("RGB", (w, h), (232, 228, 220))
    shadow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shadow).rounded_rectangle([58, 60, 438, 418], 40, fill=150)
    im.paste((150, 145, 138), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)))
    g = ImageDraw.Draw(im)
    g.rounded_rectangle([40, 20, 440, 400], 36, fill=(52, 54, 58))       # Gehäuse
    g.rounded_rectangle([40, 20, 440, 400], 36, outline=(84, 86, 92), width=3)
    g.rounded_rectangle([62, 62, 418, 330], 8, fill=(12, 12, 14))        # Rand um das Display
    g.ellipse([234, 36, 246, 48], fill=(20, 20, 24), outline=(70, 72, 78))  # Kamera oben
    for x in range(200, 281, 10):                                           # Lautsprecher unten
        g.ellipse([x, 360, x + 4, 364], fill=(30, 30, 34))
    lcd = Image.open(screen).convert("RGB").resize((320, 240), Image.LANCZOS)
    im.paste(lcd, (80, 76))
    im.save(target)


def _chrome():
    return next((c for c in CHROMES if shutil.which(c) or os.path.exists(c)), None)


def phone(html, target, tmp):
    """Fotografiert eine Seite in Handy-Größe. False, wenn es am PC kein Chrome gibt."""
    chrome = _chrome()
    if chrome is None:
        if os.environ.get("CI"):
            raise SystemExit("Kein Chrome gefunden, %s geht nicht" % os.path.basename(target))
        print(os.path.basename(target), "übersprungen: kein Chrome")
        return False
    page = os.path.join(tmp, os.path.basename(target) + ".html")
    with open(page, "wb") as f:  # Seite so schmal wie ein Handy; das Fenster selbst darf breiter sein (Windows)
        f.write(html.replace(b"</head>", b"<style>html{width:%dpx;overflow:hidden}</style></head>" % PHONE[0], 1))
    raw = os.path.join(tmp, os.path.basename(target))
    run = subprocess.run([shutil.which(chrome) or chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                          "--hide-scrollbars", "--force-device-scale-factor=1",
                          "--window-size=%d,%d" % (PHONE[0] + 300, PHONE[1]),
                          "--screenshot=" + raw, "file:///" + page.replace("\\", "/")],
                         capture_output=True, text=True, timeout=120)
    if not os.path.exists(raw):
        raise SystemExit("%s ging nicht:\n%s%s" % (target, run.stdout, run.stderr))
    Image.open(raw).crop((0, 0) + PHONE).save(target)
    return True


def render(out, tmp):
    sys.path.insert(0, os.path.join(ROOT, "device"))
    from clippy import photo_page, portal_page
    device(os.path.join(out, "s1.png"), os.path.join(out, "s2.png"))
    print("s2 ->", os.path.join(out, "s2.png"))
    for name, html in (("s22", portal_page.page(NETS)),
                       ("s27", photo_page.page("424242").replace(b"</body>", SENT.encode() + b"</body>"))):
        if phone(html, os.path.join(out, name + ".png"), tmp):
            print(name, "->", os.path.join(out, name + ".png"))
