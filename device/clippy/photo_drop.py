# Fotos vom Handy empfangen (ctx.photos_from_phone): QR-Code mit Adresse und Geheimzahl zeigen, die Seite aus
# photo_page.py ausliefern, geschickte JPEGs auf die Karte schreiben. Der Port ist nur offen, solange das hier läuft.
import os
import random
import socket

from clippy import config, photo_page, request, sdcard, wifi, win98
from clippy.win98 import DARK, FACE

MAX_BYTES = 400 * 1024       # verkleinerte Fotos haben rund 20 KB; mehr nimmt Clippy nicht an
DONE = (226, 170, 88, 42)     # Knopf „Fertig“: x, y, Breite, Höhe in der Zeichenfläche 320 × 218
HEAD = "HTTP/1.1 %s\r\nContent-Type: %s\r\nConnection: close\r\n\r\n"


def _answer(conn, status, kind, body):
    conn.sendall((HEAD % (status, kind)).encode() + body)  # send() allein darf nur einen Teil schicken


def handle(conn, token, folder):
    """Bedient eine Anfrage. Liefert den Dateinamen, wenn ein Foto gespeichert wurde, sonst None."""
    conn.settimeout(5)
    data = b""
    while b"\r\n\r\n" not in data and len(data) < 4096:
        chunk = conn.recv(1024)
        if not chunk:
            return None
        data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode().split("\r\n")
    method, target = (lines[0].split(" ") + ["", ""])[:2]
    path, args = request.query(target)
    if args.get("k") != token:
        _answer(conn, "403 Forbidden", "text/html; charset=utf-8", photo_page.WRONG.encode())
        return None
    if method == "GET":
        _answer(conn, "200 OK", "text/html; charset=utf-8", photo_page.page(token))
        return None
    length = 0
    for line in lines[1:]:
        if line.lower().startswith("content-length:"):
            length = int(line[15:])
    if method != "POST" or path != "/photo" or not 0 < length <= MAX_BYTES:
        _answer(conn, "400 Bad Request", "text/plain", b"nein\n")
        return None
    photo = bytearray(body)
    while len(photo) < length:  # erst ganz empfangen (höchstens MAX_BYTES), dann in einem Zug auf die Karte
        chunk = conn.recv(min(4096, length - len(photo)))
        if not chunk:
            return None  # abgebrochen
        photo.extend(chunk)
    if photo[:2] != b"\xff\xd8":  # nur JPEGs, so wie die Seite sie schickt
        _answer(conn, "400 Bad Request", "text/plain", b"kein JPEG\n")
        return None
    with sdcard.access():  # Leitungen gehören solange der Karte; gezeichnet wird erst danach
        name = request.file_name(args.get("n", ""), {n.lower() for n in os.listdir(folder)})
        with open(folder + "/" + name, "wb") as f:
            f.write(photo)
    _answer(conn, "200 OK", "text/plain", b"ok\n")
    return name


def _screen(ctx, url, count):
    g = ctx.screen
    g.fillScreen(FACE)
    g.fillRect(6, 6, 140, 140, win98.LIGHT)
    g.drawQR(url, 10, 10, 132, 5)
    lines = ("Fotos vom Handy", "1. QR scanna. Handy", "im söbn WLAN", "wia da Clippy.", "2. Fotos aussuachn.")
    for i, line in enumerate(lines):
        win98.text(g, line, 154, 8 + i * 20, DARK, FACE, bold=i == 0)
    win98.text(g, "Scho do: %d" % count, 154, 118, win98.NAVY, FACE, bold=True)
    win98.text(g, "Kemman auf d'Kartn,", 6, 156, DARK, FACE)
    win98.text(g, "Ordner Clippy-Bilder.", 6, 174, DARK, FACE)
    win98.button(g, *DONE, "Fertig", bold=True)
    ctx.show()


def _done(tap):
    x, y, w, h = DONE
    return tap and x <= tap[0] < x + w and y <= tap[1] < y + h


def run(ctx, folder):
    """Empfängt Fotos nach folder, bis „Fertig“ oder X. Liefert die Anzahl."""
    if not wifi.connected():
        g = ctx.screen
        g.fillScreen(FACE)
        win98.text(g, "Ka WLAN. Zerst im Startmenü:", 160, 70, DARK, FACE, align="center")
        win98.text(g, "WLAN einrichten.", 160, 90, DARK, FACE, align="center")
        win98.button(g, *DONE, "Fertig", bold=True)
        ctx.show()
        while ctx.update() and not _done(ctx.tap):
            pass
        return 0
    with sdcard.access():
        try:
            os.mkdir(folder)
        except OSError:
            pass  # gibt es schon
    token = "%06d" % random.randint(0, 999999)
    url = "http://%s:%d/?k=%s" % (wifi.info()[1], config.PHOTO_PORT, token)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", config.PHOTO_PORT))
    sock.listen(2)
    sock.setblocking(False)
    count = 0
    _screen(ctx, url, count)
    try:
        while ctx.update() and not _done(ctx.tap):
            try:
                conn, _ = sock.accept()
            except OSError:
                continue  # niemand da
            try:
                if handle(conn, token, folder):
                    count += 1
                    _screen(ctx, url, count)
            except (OSError, ValueError):
                pass  # Handy weg oder Unsinn geschickt: nächste Anfrage
            finally:
                conn.close()
        return count
    finally:
        sock.close()
