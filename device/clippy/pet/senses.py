# Die Sinne der Klammer: liest die Sensoren und meldet, was passiert ist, als Wörter (Ereignisse).
import array
import math
import time

import M5

from clippy.pet.draw import FIELD_X, FIELD_Y

SHAKE_G = 0.8    # Abweichung von 1 g, ab der eine Messung als Rütteln zählt
NEAR = 60        # Annäherung: frei 0–6, Finger auf dem Sensor ca. 300
COVERED = 150    # ab hier gilt der Sensor als zugehalten
TILT_MAX = 9     # so weit rollen die Augen höchstens zur Seite, in Pixeln
LOUD = 12000     # Mikrofon: Ruhe bis ca. 500, Klatschen bis 32767
KNOCK = 4000     # ab hier zählt ein Geräusch als Schlag (Klopfen aufs Gehäuse oder den Tisch)
LOW_BATTERY = 15
HOLD_MS = 350    # liegt der Finger länger auf ihr, ist es Streicheln statt Antippen


class Senses:
    def __init__(self):
        M5.Speaker.end()  # Mikrofon und Lautsprecher teilen sich die Leitung
        M5.Mic.begin()
        self.sound = array.array("h", bytes(1920))  # 60 ms bei 16 kHz, knapp ein Schleifendurchlauf
        self.beats = []        # Zeitpunkte der letzten Schläge
        self.knocking = False
        self.shakes = 0
        self.near = self.covered = self.touching = False
        self.taps = []
        self.touch_start = self.stroke_at = 0
        self.stroked = False
        self.tilt = 0         # Seitenneigung als Blickversatz in Pixeln
        self.light = 100
        self.night = False
        self.charging = M5.Power.isCharging()
        self.hungry_since = None

    def pause(self):
        """Für Apps: Mikrofon aus, Lautsprecher an. Beide teilen sich die Leitung."""
        M5.Mic.end()
        M5.Speaker.begin()

    def resume(self):
        M5.Speaker.end()
        M5.Mic.begin()

    def poll(self):
        """Schnelle Sinne, jeden Schleifendurchlauf. Liefert eine Liste von Ereignissen."""
        events = []
        ax, ay, az = M5.Imu.getAccel()
        rough = abs(math.sqrt(ax * ax + ay * ay + az * az) - 1) > SHAKE_G
        self.shakes = self.shakes + 1 if rough else max(0, self.shakes - 1)
        if self.shakes >= 3:
            self.shakes = 0
            events.append("shake")
        self.tilt = max(-TILT_MAX, min(TILT_MAX, int(-ax * 16)))

        prox = M5.Als.getProximitySensorData()
        covered = prox > COVERED
        near = prox > NEAR
        if covered and not self.covered:
            events.append("face_down")
        elif near and not self.near and not covered:
            events.append("near")
        self.covered, self.near = covered, near

        touching = M5.Touch.getCount() > 0 and M5.Touch.getX() >= FIELD_X and M5.Touch.getY() >= FIELD_Y
        now = time.ticks_ms()
        if touching and not self.touching:
            self.touch_start, self.stroked = now, False
        if touching and time.ticks_diff(now, self.touch_start) > HOLD_MS:
            if not self.stroked or time.ticks_diff(now, self.stroke_at) > 400:  # solange gestreichelt wird, alle 0,4 s
                self.stroked, self.stroke_at = True, now
                events.append("pet")
        if self.touching and not touching and not self.stroked:  # kurz angetippt und losgelassen
            self.taps = [t for t in self.taps if time.ticks_diff(now, t) < 5000] + [now]
            if len(self.taps) >= 3:
                self.taps = []
                events.append("grumpy")
            else:
                events.append("tap")
        self.touching = touching

        if not M5.Mic.isRecording():
            peak = max(max(self.sound), -min(self.sound))
            knocking = peak > KNOCK
            if knocking and not self.knocking:  # nur der Anfang eines Geräuschs zählt als Schlag
                now = time.ticks_ms()
                self.beats = [t for t in self.beats if time.ticks_diff(now, t) < 1500] + [now]
                if len(self.beats) >= 3:
                    events.append("beat")   # drei Schläge kurz hintereinander: da trommelt wer
                elif len(self.beats) == 1 and peak > LOUD:
                    events.append("loud")   # ein einzelner Knall
            self.knocking = knocking
            M5.Mic.record(self.sound, 16000, False)
        return events

    def slow(self):
        """Langsame Sinne, einmal je Sekunde: Strom, Licht, Uhrzeit."""
        events = []
        charging = M5.Power.isCharging()
        if charging and not self.charging:
            events.append("plugged")
        self.charging = charging
        now = time.ticks_ms()
        if M5.Power.getBatteryLevel() < LOW_BATTERY and not charging:
            if self.hungry_since is None or time.ticks_diff(now, self.hungry_since) > 300000:
                self.hungry_since = now
                events.append("low_battery")
        self.light = M5.Als.getLightSensorData()
        t = time.localtime()
        self.night = t[0] >= 2024 and (t[3] >= 23 or t[3] < 6)  # vor 2024 = Uhr noch nicht gestellt
        return events
