# WLAN-Test: verbinden, Uhr stellen, Datei von GitHub holen und per ETag prüfen, ob sie sich geändert hat.
# Liest die Zugangsdaten vom PC (local/wifi.json), speichert nichts am Gerät.
# python -m mpremote connect COM6 resume mount local run firmware/nettest.py
import M5, network, time, json

M5.begin()
URL = "https://raw.githubusercontent.com/m5stack/uiflow-micropython/master/README.md"

with open("/remote/wifi.json") as f:
    cfg = json.load(f)
network.hostname("clippy")
w = network.WLAN(network.STA_IF)
w.active(True)
if not w.isconnected():
    w.connect(cfg["ssid"], cfg["password"])
    for _ in range(40):  # höchstens 20 s
        if w.isconnected():
            break
        time.sleep_ms(500)
print("verbunden:", w.isconnected(), "status", w.status())
if not w.isconnected():
    raise SystemExit
print("adresse:", w.ifconfig()[0], "signal:", w.status("rssi"), "name:", network.hostname())

try:
    import ntptime
    ntptime.settime()
    print("uhr (UTC):", time.localtime()[:6])
except Exception as e:
    print("uhr -> FEHLER", type(e).__name__, e)

import requests

t = time.ticks_ms()
r = requests.get(URL)
etag = r.headers.get("ETag") or r.headers.get("etag")
print("abruf 1:", r.status_code, len(r.content), "bytes,", time.ticks_diff(time.ticks_ms(), t), "ms, etag", etag)
r.close()
t = time.ticks_ms()
r = requests.get(URL, headers={"If-None-Match": etag})
print("abruf 2 (erwartet 304 = unveraendert):", r.status_code, time.ticks_diff(time.ticks_ms(), t), "ms")
r.close()
