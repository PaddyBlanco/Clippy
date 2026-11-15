"""Selbsttest am PC: python tests/test_portal.py   (Einrichtungsseite und Namensauflösung von „Mit Handy“)"""
import os
import socket
import sys
import threading
import types
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "device"))
sys.modules["M5"] = types.ModuleType("M5")  # win98 braucht es nur zum Zeichnen
from clippy import portal_page, wifi_portal

# Formular auslesen, auch mit Umlauten, Leerzeichen und Sonderzeichen
body = urllib.parse.urlencode({"net": "Wohnzimmer WLAN", "pw": "Grüß Gott & 100% sicher"}).encode()
assert portal_page.credentials(body) == ("Wohnzimmer WLAN", "Grüß Gott & 100% sicher")
assert portal_page.credentials(b"net=&other=Versteckt&pw=x") == ("Versteckt", "x")
assert portal_page.credentials(b"net=&other=+&pw=x") is None
assert portal_page.credentials(b"") is None

# Seite: Netznamen werden maskiert, das erste ist vorausgewählt
html = portal_page.page([("<b>Böse</b>", -50, True), ("Offen", -70, False)]).decode()
assert "&lt;b&gt;Böse&lt;/b&gt;" in html and "<b>Böse" not in html
assert html.count("checked") == 1
assert "checked" in portal_page.page([]).decode()  # ohne Liste ist „Anderes WLAN“ gewählt

# Namensauflösung: Anfrage nach captive.apple.com (Typ A) → Antwort mit Clippys Adresse
q = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + b"\x07captive\x05apple\x03com\x00" + b"\x00\x01\x00\x01"
a = wifi_portal._answer(q)
assert a[:2] == b"\x12\x34" and a[2:4] == b"\x81\x80" and a[6:8] == b"\x00\x01"
assert a[12:len(q)] == q[12:] and a.endswith(bytes([192, 168, 4, 1]))

# Webteil: echte Sockets am PC, erst Seite holen, dann Formular abschicken
server = socket.socket()
server.bind(("127.0.0.1", 0))
server.listen(2)
server.setblocking(False)
url = "http://127.0.0.1:%d/" % server.getsockname()[1]
nets = [("Heimnetz", -50, True)]
for request in (urllib.request.Request(url + "hotspot-detect.html"),
                urllib.request.Request(url, data=urllib.parse.urlencode({"net": "Heimnetz", "pw": "geheim"}).encode())):
    reply = []
    t = threading.Thread(target=lambda: reply.append(urllib.request.urlopen(request, timeout=5).read().decode()))
    t.start()
    got = None
    while t.is_alive():
        got = wifi_portal._web(server, nets) or got
    t.join()
    if request.data:
        assert got == ("Heimnetz", "geheim") and "verbindet sich jetzt" in reply[0]
    else:
        assert got is None and "Mit welchem WLAN" in reply[0]
server.close()
print("ok")
