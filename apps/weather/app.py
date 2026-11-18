# Wetter im Fenster links neben der Klammer: jetzt und drei Tage, für Eferding oder Linz (oben umschalten).
# Tippen unter den Knöpfen lädt neu, von selbst alle 30 Minuten. Bei Regen spannt die Klammer den Schirm auf.
# Zeichenfläche 190 × 188 (beside in manifest.json).
import time

import forecast
import icons
from clippy import win98
from clippy.win98 import DARK, FACE

BTN_W, BTN_H, GAP = 94, 40, 2   # Knöpfe für die Orte, ganz oben nebeneinander
NOTE_Y, NOTE_H = 42, 18         # Anzeige für Stand und Meldungen (Schrift 15 hoch plus Rahmen)
NOW_Y, NOW_H = 60, 46           # das Wetter jetzt
DAY_Y, DAY_H = 106, 27          # je Tag eine Zeile
REFRESH_MS, RETRY_MS = 30 * 60000, 30000  # neu laden; nochmal versuchen, solange nichts da ist
GREEN = 0x40E040                # Schrift der Anzeige, wie beim Radio
NO_WIFI = "Ka WLAN (Startmenü)"


def hit(x, y, w=190):
    """Was liegt unter dem Finger: ("place", Nummer), ("reload",) oder None."""
    if y < BTN_H:
        for i in range(len(forecast.PLACES)):
            if i * (BTN_W + GAP) <= x < i * (BTN_W + GAP) + BTN_W:
                return ("place", i)
        return None
    return ("reload",) if y >= NOTE_Y and 0 <= x < w else None


def wet(data):
    """Die Art, die die Klammer hören soll: nass jetzt oder heute, sonst wie es jetzt ist."""
    now = data["now"][1]
    today = data["days"][0][1] if data["days"] else None
    return next((k for k in (now, today) if k in forecast.WET), now)


def _now(g, data):
    t, kind, day = data["now"]
    icons.draw(g, kind, 26, NOW_Y + 22, 20, day, FACE)
    temp = forecast.degrees(t)
    win98.text(g, temp, 58, NOW_Y + 4, DARK, FACE, bold=True)
    win98.text(g, forecast.WORDS[kind], 66 + win98.text_width(g, temp, bold=True), NOW_Y + 4, DARK, FACE)
    if wet(data) in forecast.WET:  # die Klammer spannt daneben den Schirm auf; reden darf sie dort nicht
        win98.text(g, "Nimm an Schirm mit!", 58, NOW_Y + 24, win98.NAVY, FACE)


def _day(g, w, y, day):
    name, kind, low, high, rain = day
    g.drawLine(2, y, w - 3, y, win98.SHADOW)
    g.drawLine(2, y + 1, w - 3, y + 1, win98.LIGHT)
    mid = y + (DAY_H - win98.FONT_H) // 2 + 1
    win98.text(g, name, 4, mid, DARK, FACE, bold=name == forecast.DAYS[0])
    icons.draw(g, kind, 86, y + DAY_H // 2 + 1, 10, True, FACE)
    win98.text(g, "%s/%s" % (forecast.degrees(low), forecast.degrees(high)), 100, mid, DARK, FACE)
    if rain is not None:
        rain = "%d%%" % rain
        win98.text(g, rain, w - 3 - win98.text_width(g, rain), mid, win98.NAVY, FACE)


def show(ctx, place, data, note):
    """Zeichnet das Fenster neu und bringt es aufs Display."""
    g, w = ctx.screen, ctx.W
    g.fillScreen(FACE)
    for i, (name, _, _) in enumerate(forecast.PLACES):
        x = i * (BTN_W + GAP)
        win98.bevel(g, x, 0, BTN_W, BTN_H, raised=i != place)  # der gewählte Ort ist eingedrückt
        win98.text(g, name, x + BTN_W // 2, (BTN_H - win98.FONT_H) // 2, DARK, FACE, bold=i == place,
                   align="center")
    win98.bevel(g, 0, NOTE_Y, w, NOTE_H, raised=False)
    g.fillRect(2, NOTE_Y + 2, w - 4, NOTE_H - 3, DARK)
    win98.text(g, note, w // 2, NOTE_Y + 1, GREEN, DARK, align="center")
    if data:
        _now(g, data)
        for i, day in enumerate(data["days"]):
            _day(g, w, DAY_Y + i * DAY_H, day)
    ctx.show()


def load(ctx, place, data):
    """Holt das Wetter für PLACES[place]. Liefert (Daten, Meldung, geklappt); ohne Erfolg bleiben die alten Daten."""
    if not ctx.online():
        return data, NO_WIFI, False
    show(ctx, place, data, "Schau grod nach ...")  # der Abruf hält alles an; solange soll man das sehen
    got = forecast.parse(ctx.get_json(forecast.url(forecast.PLACES[place])))
    if got is None:
        return data, "Wetter grod net erreichbar", False
    ctx.weather(wet(got))
    return got, "Stand " + (got["time"] or "")[11:16], True


def run(ctx):
    place = 0
    data, note, fresh = load(ctx, place, None)
    loaded, dirty = time.ticks_ms(), True
    while ctx.update():
        what = hit(ctx.tap[0], ctx.tap[1], ctx.W) if ctx.tap else None
        wait = REFRESH_MS if fresh else RETRY_MS  # nach einem Fehler bald nochmal, auch wenn alte Werte da sind
        if what or time.ticks_diff(time.ticks_ms(), loaded) > wait:
            if what and what[0] == "place" and what[1] != place:
                place, data = what[1], None  # die alten Zahlen gehören zum anderen Ort
                ctx.weather(None)
            data, note, fresh = load(ctx, place, data)
            loaded, dirty = time.ticks_ms(), True
        if dirty:
            show(ctx, place, data, note)
            dirty = False
