# Was eine App vom Gerät bekommt: Zeichenfläche, Tipper, Ton, WLAN-Stand und Radio. Der Vertrag steht in
# docs/build-an-app.md; der Starter (launcher.py) legt je App ein Ctx an und räumt es wieder weg.
import time

import M5

from clippy import wifi, win98
from clippy.player import Player
from clippy.win98 import H, TITLE_H, W

CLOSE_ZONE = (W - 48, 40)  # Tipper rechts oben (ab x, bis y) schließt das Fenster


class Ctx:
    W, H = W, H - TITLE_H

    def __init__(self, display, title):
        win98.window(display, title)
        self.screen = display.newCanvas(self.W, self.H, 16, True)  # hierauf zeichnet die App
        self.screen.fillScreen(win98.FACE)
        self.tap = None       # (x, y) des Tippers in diesem Durchlauf, sonst None
        self._down = True     # der Tipper, der die App geöffnet hat, zählt nicht
        self._player = Player()  # legt noch nichts an; erst play() startet den Player der Firmware
        self._played = False     # nach play() gehört der Ton-Ausgang dem Player, tone() schweigt

    def update(self):
        """Einmal je Schleifendurchlauf aufrufen. Liefert False, sobald das Fenster geschlossen wurde."""
        time.sleep_ms(20)
        M5.update()
        down = M5.Touch.getCount() > 0
        self.tap = None
        if down and not self._down:
            x, y = M5.Touch.getX(), M5.Touch.getY()
            if x >= CLOSE_ZONE[0] and y < CLOSE_ZONE[1]:
                return False
            if y >= TITLE_H:
                self.tap = (x, y - TITLE_H)
        self._down = down
        return True

    def show(self):
        """Bringt screen aufs Display."""
        self.screen.push(0, TITLE_H)

    def tone(self, hz, ms):
        """Ton aus dem Lautsprecher; nicht mehr, sobald play() benutzt wurde."""
        if not self._played:
            M5.Speaker.tone(hz, ms)

    def online(self):
        """True, wenn das WLAN steht."""
        return wifi.connected()

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
        if self._played:
            self._player.close()
        self.screen.delete()
