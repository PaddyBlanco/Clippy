# Was eine App vom Gerät bekommt: Zeichenfläche, Tipper, Ton, WLAN-Stand, Radio, Netz und Wetter für die Klammer.
# Der Vertrag steht in docs/build-an-app.md; der Starter (launcher.py) legt je App ein Ctx an und räumt es weg.
import time

import M5

from clippy import wifi, win98
from clippy.pet import umbrella
from clippy.player import Player
from clippy.win98 import H, PANEL_TITLE_H, TITLE_H, W

WET = ("rain", "drizzle", "snow", "storm")  # bei diesem Wetter spannt die Klammer den Schirm auf
TIMEOUT_S = 8              # so lange wartet get_json höchstens auf eine Antwort (erster https-Abruf: bis 7,5 s)
BESIDE = (0, 0, 196, 212)  # Fenster neben der Klammer: x, y, Breite, Höhe samt Rahmen; rechts davon ihr Feld
TICK_MS = 60               # so oft läuft daneben die Klammer mit, wie in der Hauptschleife des Desktops


class Ctx:
    def __init__(self, display, title, beside=False, tick=None):
        """beside: Fenster links neben der Klammer statt bildschirmfüllend; tick() läuft dann alle TICK_MS mit."""
        if beside:
            x, y, w, h = BESIDE
            win98.panel(display, x, y, w, h, title)
            self._origin = (x + 3, y + PANEL_TITLE_H + 1)
            self.W, self.H = w - 6, h - PANEL_TITLE_H - 4
            self._close = (x + w - 30, x + w, y + PANEL_TITLE_H + 6)  # X: von x, bis x, bis y
        else:
            win98.window(display, title)
            self._origin = (0, TITLE_H)
            self.W, self.H = W, H - TITLE_H
            self._close = (W - 48, W, 40)
        self.screen = display.newCanvas(self.W, self.H, 16, True)  # hierauf zeichnet die App
        self.screen.fillScreen(win98.FACE)
        self.tap = None          # (x, y) des Tippers in diesem Durchlauf, sonst None
        self._down = True        # der Tipper, der die App geöffnet hat, zählt nicht
        self._tick, self._ticked = tick, time.ticks_ms()
        self._player = Player()  # legt noch nichts an; erst play() startet den Player der Firmware
        self._played = False     # nach play() gehört der Ton-Ausgang dem Player, tone() schweigt

    def update(self):
        """Einmal je Schleifendurchlauf aufrufen. Liefert False, sobald das Fenster geschlossen wurde."""
        time.sleep_ms(20)
        M5.update()
        now = time.ticks_ms()
        if self._tick and time.ticks_diff(now, self._ticked) >= TICK_MS:
            self._ticked = now
            self._tick()
        down = M5.Touch.getCount() > 0
        self.tap = None
        if down and not self._down:
            x, y = M5.Touch.getX(), M5.Touch.getY()
            x0, x1, y1 = self._close
            if x0 <= x < x1 and y < y1:
                return False
            ox, oy = self._origin
            if ox <= x < ox + self.W and oy <= y < oy + self.H:  # daneben: gehört der Klammer
                self.tap = (x - ox, y - oy)
        self._down = down
        return True

    def show(self):
        """Bringt screen aufs Display."""
        self.screen.push(*self._origin)

    def tone(self, hz, ms):
        """Ton aus dem Lautsprecher; nicht mehr, sobald play() benutzt wurde."""
        if not self._played:
            M5.Speaker.tone(hz, ms)

    def online(self):
        """True, wenn das WLAN steht."""
        return wifi.connected()

    def weather(self, kind):
        """Sagt der Klammer, wie das Wetter ist; bei Nässe (WET) spannt sie den Schirm auf."""
        umbrella.rain(kind in WET)

    def get_json(self, url):
        """JSON-Antwort aus dem Netz als dict; None ohne WLAN, bei einem Fehler oder einer kaputten Antwort."""
        if not self.online():
            return None
        r = None
        try:
            import requests  # erst hier: am PC (Vorschau) gibt es das Modul der Firmware nicht
            r = requests.get(url, timeout=TIMEOUT_S)  # ohne Zeitlimit hängt das Gerät, wenn keine Antwort kommt
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
        finally:
            if r is not None:
                r.close()

    def play(self, url):
        """Spielt einen MP3-Strom aus dem Netz (nur http://); wartet bis zu 3,5 s, bis er läuft.
        True, wenn die Firmware ihn annimmt."""
        self._played = True
        return self._player.play(url)

    def playing(self):
        """True, sobald Daten fließen."""
        return self._played and self._player.playing()

    def volume(self, pct=None):
        """Lautstärke 0 bis 100 lesen, mit pct stellen."""
        if pct is not None:
            self._player.set_volume(pct)
        return self._player.volume

    def stop(self):
        """Musik aus."""
        if self._played:
            self._player.stop()

    def close(self):
        umbrella.rain(False)
        if self._played:
            self._player.close()
        self.screen.delete()
