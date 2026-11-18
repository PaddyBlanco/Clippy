"""Selbsttest am PC: python tests/test_weather.py
Die App Wetter: Abfrage je Ort, Auswerten der Antwort, Tippflächen und Platz im Fenster neben der Klammer;
der Schirm der Klammer bei Regen."""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "device"))
sys.path.insert(0, os.path.join(ROOT, "apps", "weather"))
import app as weather
import forecast

W, H = 190, 188  # Zeichenfläche im Fenster neben der Klammer (app_context.BESIDE ohne Rahmen)

with open(os.path.join(ROOT, "apps", "manifest.json"), encoding="utf-8") as f:
    assert next(a for a in json.load(f) if a["id"] == "weather").get("beside") is True

# Je Ort eine Abfrage mit seinen Koordinaten, alles in einer Zeile ohne Leerzeichen
assert [p[0] for p in forecast.PLACES] == ["Eferding", "Linz"]
for name, lat, lon in forecast.PLACES:
    u = forecast.url((name, lat, lon))
    assert u.startswith("http") and " " not in u and "latitude=%.2f" % lat in u and "longitude=%.2f" % lon in u

# Jeder WMO-Code ergibt eine Art mit einem Wort; ein paar Stichproben
assert all(forecast.kind(c) in forecast.WORDS for c in list(range(100)) + [None])
assert [forecast.kind(c) for c in (0, 2, 3, 45, 53, 63, 81, 75, 95)] == \
    ["sun", "partly", "cloud", "fog", "drizzle", "rain", "rain", "snow", "storm"]

# Die echte Antwort in tests/weather_sample.json: jetzt und drei Tage
with open(os.path.join(ROOT, "tests", "weather_sample.json"), encoding="utf-8") as f:
    got = forecast.parse(json.load(f))
t, kind, day = got["now"]
assert isinstance(t, (int, float)) and kind in forecast.WORDS and day in (True, False)
assert [d[0] for d in got["days"]] == list(forecast.DAYS) and len(got["time"]) >= 16
assert all(d[2] <= d[3] for d in got["days"])

# Kaputte oder halbe Antworten führen nicht zum Absturz
assert forecast.parse(None) is None and forecast.parse({}) is None and forecast.parse([1]) is None
half = forecast.parse({"current": {}, "daily": {"time": ["2026-11-18"]}})
assert half["now"] == (None, "cloud", True) and half["days"] == [("Heit", "cloud", None, None, None)]
assert forecast.degrees(None) == "?°" and forecast.degrees(14.6) == "15°" and forecast.degrees(-2.4) == "-2°"

# Ortsknöpfe treffen sich selbst und sind groß genug, darunter lädt jeder Tipper neu
assert weather.BTN_W >= 40 and weather.BTN_H >= 40 and 2 * weather.BTN_W + weather.GAP <= W
assert weather.hit(5, 5) == ("place", 0) and weather.hit(weather.BTN_W - 1, weather.BTN_H - 1) == ("place", 0)
assert weather.hit(weather.BTN_W + weather.GAP, 5) == ("place", 1) and weather.hit(W - 1, 20) == ("place", 1)
assert weather.hit(weather.BTN_W, 5) is None  # die Fuge zwischen den Knöpfen
assert weather.hit(10, weather.NOTE_Y) == ("reload",) and weather.hit(100, H - 1) == ("reload",)

# Alles bleibt im Fenster, die Teile überlappen sich nicht
assert weather.BTN_H <= weather.NOTE_Y and weather.NOTE_Y + weather.NOTE_H <= weather.NOW_Y
assert weather.NOW_Y + weather.NOW_H <= weather.DAY_Y
assert weather.DAY_Y + len(forecast.DAYS) * weather.DAY_H <= H

# Schirm: nass jetzt oder heute -> nasse Art, sonst die von jetzt
day = ("Heit", "sun", 1, 9, 0)
assert weather.wet({"now": (5, "sun", True), "days": [day]}) == "sun"
assert weather.wet({"now": (5, "cloud", True), "days": [("Heit", "rain", 1, 9, 80)]}) == "rain"
assert weather.wet({"now": (5, "snow", True), "days": []}) == "snow"
assert weather.wet(got) in forecast.WET  # in der Vorlage regnet es

# Die Klammer hält den Schirm nur im eigenen Feld: nie kippen nach links oder rollen (wie beim Tanz)
from clippy.pet import umbrella
from clippy.pet.draw import FIELD_W, draw
umbrella.rain(True)
poses = list(umbrella.hold())
assert len(poses) >= 40 and all(p["umbrella"] and p["lean"] <= 0 and p["roll"] == 0 for p in poses)
moving = umbrella.hold()
next(moving)
umbrella.rain(False)  # trocken geworden: die Bewegung endet sofort, nicht erst nach ihrer Runde
assert list(moving) == [] and list(umbrella.hold()) == []


class Bounds:
    """Merkt sich, wohin gezeichnet wird (nur die Punkte, ohne Radien und Breiten)."""
    def __init__(self):
        self.xs, self.ys = [], []

    def _points(self, *a):
        for x, y in zip(a[0::2], a[1::2]):
            self.xs.append(x)
            self.ys.append(y)

    def fillTriangle(self, *a):
        self._points(*a[:6])

    def drawLine(self, *a):
        self._points(*a[:4])

    def fillCircle(self, x, y, r, c):
        self._points(x - r, y - r, x + r, y + r)

    def __getattr__(self, name):  # alles andere an der Figur interessiert hier nicht
        return lambda *a, **k: None


for pose in poses:
    b = Bounds()
    draw(b, pose)
    assert 0 <= min(b.xs) and max(b.xs) < FIELD_W and 0 <= min(b.ys), (min(b.xs), max(b.xs), min(b.ys))

# ctx.weather schaltet den Schirm, Schließen klappt ihn zu (ohne Gerät: nur die Methoden, kein Fenster)
import types
sys.modules.setdefault("M5", types.ModuleType("M5"))  # am PC gibt es das Modul der Firmware nicht
from clippy import app_context
ctx = app_context.Ctx.__new__(app_context.Ctx)
for kind, want in (("rain", True), ("sun", False), ("storm", True), (None, False), ("drizzle", True)):
    ctx.weather(kind)
    assert umbrella.raining() is want, kind
ctx._played, ctx.screen = False, types.SimpleNamespace(delete=lambda: None)
ctx.close()
assert umbrella.raining() is False
print("ok")
