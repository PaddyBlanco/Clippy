"""Zeichnet ein Geräte-Skript am PC in ein PNG, ohne Gerät.

    python tools/preview.py device/main.py local/preview.png [durchlaeufe]
    python tools/preview.py apps/radio/app.py local/preview.png      (eine App in ihrem Fenster)
    python tools/preview.py apps/weather/app.py local/preview.png --online tests/weather_sample.json
        (die App ist im WLAN, und ctx.get_json() liefert immer diese Datei)

Ersetzt das Modul M5 durch eine Nachbildung mit Pillow. Text in den Projekt-Schriften (device/res/*.vlw) wird
aus denselben Dateien gezeichnet wie am Gerät; nur die eingebauten Firmware-Schriften sind eine Näherung.
Das Skript endet, sobald es M5.update() so oft aufgerufen hat wie angegeben (Standard 3).
"""
import builtins
import io
import json
import os
import runpy
import struct
import sys
import time
import types

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_ONLY = {"/flash/bg.jpg": os.path.join(ROOT, "local", "bg", "bg.jpg")}  # liegt nicht im Repo
BUILTIN_TTF = "C:/Windows/Fonts/verdana.ttf"  # Ersatz für die eingebauten Firmware-Schriften


def pc_path(p):
    """Pfad am Gerät -> Datei am PC: /flash/... entspricht dem Ordner device/."""
    if isinstance(p, str) and p.startswith("/flash/apps/"):  # Apps und Sprüche
        return os.path.join(ROOT, "apps", p[12:])
    if isinstance(p, str) and p.startswith("/flash/"):
        return LOCAL_ONLY.get(p, os.path.join(ROOT, "device", p[7:]))
    return p


def rgb(c):
    return (c >> 16) & 255, (c >> 8) & 255, c & 255


class Vlw:
    def __init__(self, data):
        count, _, size, _, self.ascent, self.descent = struct.unpack(">6I", data[:24])
        self.height = max(size, self.ascent + self.descent)
        self.space = self.height * 2 // 7
        self.glyphs, pos = {}, 24 + count * 28
        for i in range(count):
            code, h, w, adv, dy, dx, _ = struct.unpack(">7i", data[24 + i * 28:52 + i * 28])
            self.glyphs[chr(code)] = (w, h, adv, dy, dx, data[pos:pos + w * h])
            pos += w * h

    def width(self, s):
        return sum(self.glyphs[ch][2] if ch in self.glyphs else self.space for ch in s)

    def draw(self, img, s, x, y, color):
        for ch in s:
            if ch in self.glyphs:
                w, h, adv, dy, dx, bits = self.glyphs[ch]
                if w and h:
                    img.paste(color, (x + dx, y + self.ascent - dy), Image.frombytes("L", (w, h), bits))
                x += adv
            else:
                x += self.space


class Fonts:
    def __getattr__(self, name):  # z. B. DejaVu12 -> Größe 12
        return int("".join(ch for ch in name if ch.isdigit()) or 8)


class Surface:
    FONTS = Fonts()

    def __init__(self, w, h, parent=None):
        self.img = Image.new("RGB", (w, h))
        self.dr = ImageDraw.Draw(self.img)
        self.parent = parent
        self.size, self.scale, self.fg, self.bg, self.vlw = 8, 1, 0xFFFFFF, 0x000000, None

    def width(self):
        return self.img.width

    def height(self):
        return self.img.height

    def fillScreen(self, c=0):
        self.dr.rectangle([0, 0, self.img.width, self.img.height], fill=rgb(c))

    def fillRect(self, x, y, w, h, c):
        self.dr.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb(c))

    def drawRect(self, x, y, w, h, c):
        self.dr.rectangle([x, y, x + w - 1, y + h - 1], outline=rgb(c))

    def fillRoundRect(self, x, y, w, h, r, c):
        self.dr.rounded_rectangle([x, y, x + w - 1, y + h - 1], r, fill=rgb(c))

    def drawRoundRect(self, x, y, w, h, r, c):
        self.dr.rounded_rectangle([x, y, x + w - 1, y + h - 1], r, outline=rgb(c))

    def drawLine(self, x0, y0, x1, y1, c):
        self.dr.line([x0, y0, x1, y1], fill=rgb(c))

    def drawPixel(self, x, y, c):
        self.dr.point([x, y], fill=rgb(c))

    def fillCircle(self, x, y, r, c):
        self.dr.ellipse([x - r, y - r, x + r, y + r], fill=rgb(c))

    def drawCircle(self, x, y, r, c):
        self.dr.ellipse([x - r, y - r, x + r, y + r], outline=rgb(c))

    def fillEllipse(self, x, y, rx, ry, c):
        self.dr.ellipse([x - rx, y - ry, x + rx, y + ry], fill=rgb(c))

    def drawEllipse(self, x, y, rx, ry, c):
        self.dr.ellipse([x - rx, y - ry, x + rx, y + ry], outline=rgb(c))

    def fillTriangle(self, x0, y0, x1, y1, x2, y2, c):
        self.dr.polygon([x0, y0, x1, y1, x2, y2], fill=rgb(c))

    def fillArc(self, x, y, r0, r1, a0, a1, c):
        r = max(r0, r1)
        self.dr.arc([x - r, y - r, x + r, y + r], a0, a1, fill=rgb(c), width=abs(r0 - r1) + 1)

    def setFont(self, size):
        self.size, self.vlw = size, None

    def loadFont(self, src):
        self.vlw = Vlw(open(pc_path(src), "rb").read() if isinstance(src, str) else src)
        return True

    def setTextSize(self, scale):
        self.scale = scale

    def setTextColor(self, fg, bg=None):
        self.fg, self.bg = fg, fg if bg is None else bg

    def _ttf(self):
        return ImageFont.truetype(BUILTIN_TTF, max(6, round(self.size * self.scale * 1.17)))

    def textWidth(self, s):
        return self.vlw.width(s) if self.vlw else int(self.dr.textlength(s, font=self._ttf()))

    def fontHeight(self):
        return self.vlw.height if self.vlw else int(self.size * self.scale * 1.33)

    def drawString(self, s, x, y):
        if self.bg != self.fg and s:
            self.fillRect(x, y, self.textWidth(s), self.fontHeight(), self.bg)
        if self.vlw:
            self.vlw.draw(self.img, s, x, y, rgb(self.fg))
        else:
            self.dr.text((x, y), s, font=self._ttf(), fill=rgb(self.fg))

    def drawCenterString(self, s, x, y):
        self.drawString(s, x - self.textWidth(s) // 2, y)

    def drawRightString(self, s, x, y):
        self.drawString(s, x - self.textWidth(s), y)

    def drawJpg(self, src, x=0, y=0, maxW=0, maxH=0, offX=0, offY=0):
        if isinstance(src, str):
            src = open(pc_path(src), "rb").read()
        pic = Image.open(io.BytesIO(src)).convert("RGB")
        pic = pic.crop((offX, offY, offX + maxW if maxW else pic.width, offY + maxH if maxH else pic.height))
        self.img.paste(pic, (x, y))

    def newCanvas(self, w, h, bpp=16, psram=True):
        return Surface(w, h, parent=self)

    def push(self, x, y):
        self.parent.img.paste(self.img, (x, y))

    def delete(self):
        pass

    def setBrightness(self, value):
        pass

    def drawQR(self, text, x, y, size, version=1):  # nur ein Platzhalter in passender Größe
        self.dr.rectangle([x, y, x + size - 1, y + size - 1], fill=(0, 0, 0))
        self.dr.text((x + 6, y + size // 2 - 6), "QR-Code", font=self._ttf(), fill=(255, 255, 255))

    def __getattr__(self, name):
        raise AttributeError("Die Vorschau kennt '%s' nicht. In tools/preview.py ergänzen." % name)


class Quiet:
    """Sensoren und Ton: liefern Ruhewerte, tun nichts."""

    def __init__(self, **values):
        self._values = values

    def __getattr__(self, name):
        return lambda *a, **k: self._values.get(name)


def main():
    args = sys.argv[1:]
    answer = None  # --online <datei>: Antwort für ctx.get_json()
    if "--online" in args:
        i = args.index("--online")
        if i + 1 >= len(args):
            raise SystemExit("--online braucht eine JSON-Datei")
        answer = args[i + 1]
        del args[i:i + 2]
    script, out = args[0], args[1]
    runs = [int(args[2]) if len(args) > 2 else 3]
    display = Surface(320, 240)

    def update():
        runs[0] -= 1
        if runs[0] < 0:
            raise SystemExit

    m5 = types.ModuleType("M5")
    m5.begin = lambda: None
    m5.update = update
    m5.Display = m5.Lcd = display
    m5.Touch = Quiet(getCount=0, getX=0, getY=0)
    m5.Imu = Quiet(getAccel=(0.0, 0.0, 1.0), getGyro=(0.0, 0.0, 0.0))
    m5.Als = Quiet(getProximitySensorData=0, getLightSensorData=100)
    m5.Power = Quiet(getBatteryLevel=80, isCharging=False)
    m5.Speaker = m5.Mic = Quiet()
    sys.modules["M5"] = m5

    # MicroPython-Zeitfunktionen. Die Uhr ist gespielt: sleep_ms stellt sie vor, so vergeht in der Vorschau
    # genau so viel Zeit, wie das Skript am Gerät warten würde.
    clock = [0]
    time.sleep_ms = lambda ms: clock.__setitem__(0, clock[0] + ms)
    time.ticks_ms = lambda: clock[0]
    time.ticks_diff = lambda a, b: a - b
    time.ticks_add = lambda a, b: a + b

    # Dateien am Gerät (/flash/...) auf den Projektordner umlenken
    real_open, real_stat = builtins.open, os.stat
    builtins.open = lambda p, *a, **k: real_open(pc_path(p), *a, **k)
    os.stat = lambda p, *a, **k: real_stat(pc_path(p), *a, **k)

    sys.path.insert(0, os.path.join(ROOT, "device"))
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    try:
        scope = runpy.run_path(script, run_name="__main__")
        if "run" in scope:  # eine App: im Fenster starten, wie es der Launcher am Gerät tut
            from clippy import launcher
            app_id = os.path.basename(os.path.dirname(os.path.abspath(script)))
            with real_open(os.path.join(ROOT, "apps", "manifest.json"), encoding="utf-8") as f:
                app = next((a for a in json.load(f) if a["id"] == app_id), {})
            if app.get("beside"):  # Fenster neben der Klammer: dahinter der Desktop
                display.fillScreen(0x008080)
            ctx = launcher.Ctx(display, app.get("name", app_id), app.get("beside", False))
            ctx._down = False
            if answer:
                ctx.online = lambda: True
                with real_open(answer, encoding="utf-8") as f:
                    canned = json.load(f)
                ctx.get_json = lambda url: canned
            scope["run"](ctx)
    except SystemExit:
        pass
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    display.img.resize((640, 480), Image.NEAREST).save(out)
    print("gespeichert:", out)


main()
