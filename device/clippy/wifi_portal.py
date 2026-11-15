# WLAN einrichten mit dem Handy: Clippy öffnet ein eigenes WLAN, zeigt QR-Codes und liefert die Einrichtungsseite
# aus. Ablauf in docs/architecture.md unter „Startmenü“.
import random
import socket

from clippy import portal_page, win98
from clippy.win98 import DARK, FACE

SSID = "Clippy-Setup"
ADDRESS = "192.168.4.1"  # Adresse des eigenen WLANs beim ESP32
URL = "http://%s/" % ADDRESS


def _screen(ctx, qr, lines):
    g = ctx.screen
    g.fillScreen(FACE)
    g.fillRect(6, 6, 140, 140, win98.LIGHT)
    g.drawQR(qr, 10, 10, 132, 5)
    for i, line in enumerate(lines):
        win98.text(g, line, 154, 14 + i * 22, DARK, FACE, bold=i == 0)
    win98.text(g, "X rechts oben bricht ab.", 160, 190, DARK, FACE, align="center")
    ctx.show()


def _answer(query):
    """Antwort auf eine DNS-Anfrage: Jeder Name gehört Clippy. So hält das Handy die Seite für eine Anmeldeseite."""
    end = 12
    while end < len(query) and query[end]:
        end += query[end] + 1
    end += 5  # Null-Byte, Typ und Klasse der Frage
    ip = bytes(int(p) for p in ADDRESS.split("."))
    return (query[:2] + b"\x81\x80" + query[4:6] + query[4:6] + b"\x00\x00\x00\x00" + query[12:end]
            + b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + ip)


def _dns(sock):
    try:
        query, addr = sock.recvfrom(512)
        sock.sendto(_answer(query), addr)
    except OSError:
        pass  # nichts da


def _send(conn, html):
    conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n")
    conn.send(html)


def _web(sock, networks):
    """Bedient höchstens eine Anfrage. Liefert (Netzname, Passwort), sobald das Formular abgeschickt wurde."""
    try:
        conn, _ = sock.accept()
    except OSError:
        return None
    try:
        conn.settimeout(3)
        request = conn.recv(1024)
        cut = request.find(b"\r\n\r\n")
        head, body = request[:cut].decode().lower(), request[cut + 4:]
        if not head.startswith("post"):
            _send(conn, portal_page.page(networks))  # jede Adresse bekommt die Seite
            return None
        length = 0
        for line in head.split("\r\n"):
            if line.startswith("content-length:"):
                length = int(line[15:])
        while len(body) < length:
            chunk = conn.recv(512)
            if not chunk:
                break
            body += chunk
        got = portal_page.credentials(body)
        _send(conn, portal_page.done(got[0]) if got else portal_page.page(networks, "Bitte ein WLAN wählen."))
        return got
    except (OSError, ValueError):
        return None
    finally:
        conn.close()


def run(ctx, networks):
    """Liefert (Netzname, Passwort) vom Handy oder None, wenn das Fenster geschlossen wurde."""
    import network
    password = "%08d" % random.randint(10000000, 99999999)
    network.WLAN(network.STA_IF).disconnect()  # sonst springt das ESP32 beim Suchen zwischen den Kanälen
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=password, authmode=network.AUTH_WPA2_PSK)
    dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns.bind(("0.0.0.0", 53))
    dns.setblocking(False)
    web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    web.bind(("0.0.0.0", 80))
    web.listen(2)
    web.setblocking(False)
    shown = None
    try:
        while ctx.update():
            try:
                joined = bool(ap.status("stations"))
            except (OSError, ValueError):
                joined = False
            if joined != shown:
                shown = joined
                if joined:
                    _screen(ctx, URL, ["2. Seite öffnen", "Handy verbunden.", "Geht keine Seite", "auf: QR scannen", "oder " + ADDRESS])
                else:
                    _screen(ctx, "WIFI:T:WPA;S:%s;P:%s;;" % (SSID, password),
                            ["1. QR scannen", "mit der Handy-", "Kamera. Oder WLAN", SSID, "Passwort " + password])
            _dns(dns)
            got = _web(web, networks)
            if got:
                return got
        return None
    finally:
        dns.close()
        web.close()
        ap.active(False)
