# Radio-Probe: python -m mpremote connect COM4 resume run checks/radio.py
# Direkt nach einem Neustart laufen lassen (sonst steckt noch der Player des Hauptprogramms im Speicher).
# Spielt wie die App Radio zweimal je 5 s Ö3 auf Lautstärke 20; dazwischen lauscht das Mikrofon wie am Desktop
# (das verdrahtete früher die Ton-Anschlüsse um, und das zweite Radio blieb stumm). Liest jedes Mal den Verstärker
# aus und prüft danach, ob Mikrofon, Sensoren und Touch wieder gehen. Hörbar, aber leise; kein Piepsen.
import array
import time

import M5
import network
from clippy import player

URL = "http://orf-live.ors-shoutcast.at/oe3-q1a"


def mic_level():
    """Lauscht einmal 60 ms wie die Klammer und liefert den Pegel (Ruhe: einstellig bis ein paar hundert)."""
    sound = array.array("h", bytes(1920))
    M5.Mic.record(sound, 16000, False)
    time.sleep(0.3)
    return max(max(sound), -min(sound))


def amp(reg):
    return "%04X" % player._read(player.AW88298, reg)


def radio(n):
    """Eine Runde wie beim Öffnen und Schließen der App (senses.pause, play, close, senses.resume)."""
    M5.Mic.end()
    M5.Speaker.begin()
    p = player.Player()
    p.set_volume(20)
    print("runde", n, "play ->", p.play(URL), "fehler", p.error)
    t0 = time.ticks_ms()
    while not p.playing() and time.ticks_diff(time.ticks_ms(), t0) < 12000:
        time.sleep_ms(100)
    print("  daten nach", time.ticks_diff(time.ticks_ms(), t0), "ms")
    time.sleep(1)
    # gesund: SYSST 0311 (Takt eingerastet), SYSCTRL 4040 (eingeschaltet); VOL hängt an der Lautstärke
    print("  verstärker: SYSST", amp(0x01), "SYSCTRL", amp(0x04), "VOL", amp(0x0C))
    time.sleep(4)
    p.close()
    M5.Speaker.end()
    M5.Mic.begin()


M5.begin()
w = network.WLAN(network.STA_IF)
for _ in range(30):  # nach einem Neustart braucht das WLAN ein paar Sekunden
    if w.isconnected():
        break
    time.sleep(0.5)
print("wlan:", w.isconnected())
M5.Speaker.end()
M5.Mic.begin()
print("mikrofon vorher:", mic_level())
radio(1)
print("mikrofon zwischen den runden:", mic_level(), mic_level())
radio(2)
M5.update()
print("danach: mikrofon", mic_level(), "akku", M5.Power.getBatteryLevel(), "lage", M5.Imu.getAccel(),
      "touch", M5.Touch.getCount())
print("fertig")
