# Internetradio: ein MP3-Strom aus dem Netz über den Player der Firmware (ESP-ADF, Modul audio).
# Nur http, kein https. Der Player richtet den Verstärker AW88298 selbst ein, wenn der vorher aus dem Reset ist
# (den hält M5.Speaker.end() fest) und niemand sonst den Bus benutzt; fragt die App dabei den Touch ab, geht die
# Einrichtung verloren. Darum wartet play() kurz und hilft notfalls nach. Die Lautstärke schreibt dieses Modul
# selbst in den Verstärker; der Player tut es nicht verlässlich (docs/device.md). Am PC tut alles nichts.
import time

import M5

try:
    import audio
    from machine import I2C, Pin
except ImportError:
    audio = None

AW9523, AW88298 = 0x58, 0x36  # IO-Erweiterung (Bit 2 von P0 = Reset des Verstärkers) und Verstärker
AMP_ON = 0x4040               # Register 0x04 eines eingeschalteten Verstärkers
# was der Player selbst einstellt (am Gerät ausgelesen): Takt, I2S, kein Stummschalten, ein
AMP_SETUP = ((0x61, 0x0673), (0x06, 0x3C08), (0x05, 0x0008), (0x04, AMP_ON))
SETTLE_MS, WAIT_MS = 500, 3000  # so lange nach den ersten Daten Ruhe auf dem Bus; so lange höchstens auf Daten warten
# Lautstärke in 0x0C, oberes Byte: Dämpfung in halben dB (0 = voll, 0xC0 = -96 dB). Regler 100 = 0 dB, jeder
# Punkt darunter -0,5 dB, also 40 = -30 dB; 0 = 0xC0, praktisch stumm. Das untere Byte 0x64 setzt auch der Player
MUTE = 0xC0
_volume = [40]      # zuletzt gestellte Lautstärke 0 bis 100, bleibt bis zum Neustart des Geräts
_firmware = [None]  # der Player der Firmware: einmal angelegt, bleibt er; jeder neue kostet rund 10 KB für immer
_bus = [None]       # interner Bus: Kanal 1 wie Firmware und Player. Kanal 0 nimmt ihnen die Pins weg (Touch!)


def _write(addr, reg, value):
    _bus[0].writeto(addr, bytes([reg, value >> 8, value & 0xFF]) if addr == AW88298 else bytes([reg, value]))


def _read(addr, reg):
    _bus[0].writeto(addr, bytes([reg]), False)
    b = _bus[0].readfrom(addr, 2 if addr == AW88298 else 1)
    return b[0] << 8 | b[1] if addr == AW88298 else b[0]


def amp_reset_off():
    """Verstärker aus dem Reset holen; nur Bit 2, die anderen Ausgänge der IO-Erweiterung bleiben, wie sie sind."""
    _write(AW9523, 0x02, _read(AW9523, 0x02) | 0x04)


def amp_check():
    """Nach dem Start: die eigene Lautstärke, dann einschalten, falls der Player es nicht getan hat."""
    amp_volume()  # zuerst: nach einem Reset steht der Verstärker auf voll
    if _read(AW88298, 0x04) != AMP_ON:
        for reg, value in AMP_SETUP:
            _write(AW88298, reg, value)


def amp_volume():
    att = 100 - _volume[0] if _volume[0] else MUTE
    _write(AW88298, 0x0C, att << 8 | 0x64)


class Player:
    def __init__(self):
        self.error = 0   # Fehlercode der Firmware vom letzten play(), 0 = angenommen

    @property
    def volume(self):
        return _volume[0]

    def play(self, url):
        """Startet den Strom und wartet, bis er läuft (bis rund 3,5 s). True, wenn die Firmware ihn angenommen hat."""
        if audio is None:
            return False
        try:
            # Reihenfolge ist wichtig, sonst stürzt das Gerät ab: erst Lautsprecher aus (gibt den Ton-Ausgang frei,
            # setzt dabei aber den Verstärker in den Reset), dann der Bus, dann der Player, dann den Reset lösen
            M5.Speaker.end()
            if _bus[0] is None:
                _bus[0] = I2C(1, scl=Pin(11), sda=Pin(12), freq=400000)
            if _firmware[0] is None:
                _firmware[0] = audio.Player(lambda *a: None)  # ein Rückruf ist Pflicht, auch ein leerer
            else:
                _firmware[0].stop()
            amp_reset_off()
            self.error = _firmware[0].play(url, volume=0, sync=False) or 0  # leise starten, amp_check stellt ein
            if self.error == 0:
                start = time.ticks_ms()  # warten ohne Bus-Verkehr, sonst geht die Einrichtung des Verstärkers verloren
                while not _firmware[0].pos() and time.ticks_diff(time.ticks_ms(), start) < WAIT_MS:
                    time.sleep_ms(50)
                time.sleep_ms(SETTLE_MS)
                amp_check()
        except OSError as e:   # Codec, I2S oder Bus nicht bereit
            self.error = e.args[0] if e.args else -1
        return self.error == 0

    def playing(self):
        """True, sobald Daten fließen."""
        return _firmware[0] is not None and bool(_firmware[0].pos())

    def set_volume(self, pct):
        _volume[0] = max(0, min(100, pct))
        if _bus[0]:
            amp_volume()

    def stop(self):
        if _firmware[0]:
            _firmware[0].stop()

    def close(self):
        """Am Ende der App: aufhören. Der Player der Firmware bleibt für das nächste Mal."""
        self.stop()
