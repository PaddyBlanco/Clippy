# Bestandsaufnahme: python -m mpremote connect COM6 resume run checks/inventory.py
import M5, time

M5.begin()


def probe(name, fn):
    try:
        print(name, "->", fn())
    except Exception as e:
        print(name, "-> FEHLER", type(e).__name__, e)


help("modules")
print("M5:", [n for n in dir(M5) if not n.startswith("_")])
for part in ("Display", "Touch", "Imu", "Speaker", "Mic", "Power", "Rtc", "Als"):
    obj = getattr(M5, part, None)
    print(part + ":", [n for n in dir(obj) if not n.startswith("_")] if obj else None)

probe("imu accel", lambda: M5.Imu.getAccel())
probe("imu gyro", lambda: M5.Imu.getGyro())
probe("imu mag", lambda: M5.Imu.getMag())
probe("akku %", lambda: M5.Power.getBatteryLevel())
probe("akku mV", lambda: M5.Power.getBatteryVoltage())
probe("laedt", lambda: M5.Power.isCharging())
probe("rtc", lambda: M5.Rtc.getDateTime())
probe("helligkeit", lambda: M5.Display.getBrightness())
probe("fonts", lambda: [n for n in dir(M5.Display.FONTS)if not n.startswith("_")])
probe("ton", lambda: M5.Speaker.tone(880, 150))
probe("touch count", lambda: (M5.update(), M5.Touch.getCount())[1])


def wifi():
    import network
    w = network.WLAN(network.STA_IF)
    w.active(True)
    return sorted({(n[0].decode(), n[3]) for n in w.scan()}, key=lambda x: -x[1])[:5]


def sd():
    import os
    return os.listdir("/sd")


def cam():
    import camera
    return [n for n in dir(camera) if not n.startswith("_")]


def tls():
    import requests
    r = requests.get("https://raw.githubusercontent.com/m5stack/uiflow-micropython/master/README.md")
    out = (r.status_code, r.headers.get("ETag") or r.headers.get("etag"), len(r.content))
    r.close()
    return out


probe("wlan scan", wifi)
probe("sd", sd)
probe("kamera", cam)
probe("https github (nur mit WLAN)", tls)
