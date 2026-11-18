"""Selbsttest am PC: python tests/test_photo_drop.py
Fotos vom Handy (photo_drop.py, request.py): Adresse lesen, Dateinamen bilden, und eine echte Anfrage über einen
Socket auf 127.0.0.1 wie vom Handy: Seite holen, Fotos schicken, falsche Geheimzahl, kein JPEG, zu groß."""
import os
import shutil
import socket
import sys
import tempfile
import threading
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "device"))
from clippy import photo_drop, photo_page, request

# Adresse und Namen
assert request.query("/photo?k=123456&n=Foto%20vom%20See.JPG") == ("/photo", {"k": "123456", "n": "Foto vom See.JPG"})
assert request.query("/?k=1") == ("/", {"k": "1"}) and request.query("/") == ("/", {})
assert request.unquote("Gr%C3%BC%C3%9Fe+aus+Linz") == "Grüße aus Linz" and request.unquote("100%") == "100%"
assert request.unquote("%zz%4") == "%zz%4"  # % ohne zwei Hex-Ziffern bleibt stehen
try:
    request.unquote("%E2%82")  # kaputtes UTF-8
    raise AssertionError("hätte werfen sollen")
except ValueError:
    pass
taken = set()
for name, want in (("IMG_0001.HEIC", "IMG_0001.jpg"), ("img_0001.jpg", "img_0001_2.jpg"),
                   ("Grüße aus Linz (2).jpeg", "Gr_e_aus_Linz_2.jpg"), ("../../boot.py", "boot.jpg"),
                   ("", "bild.jpg"), ("äöü.png", "bild_2.jpg"), ("x" * 80 + ".jpg", "x" * 40 + ".jpg")):
    got = request.file_name(name, taken)
    assert got == want, (name, got)
    taken.add(got.lower())

# Die Seite fürs Handy enthält die Geheimzahl und schickt an /photo
assert b'var K = "424242"' in photo_page.page("424242") and b"/photo?k=" in photo_page.page("1")

folder = tempfile.mkdtemp()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 0))
server.listen(1)
port = server.getsockname()[1]
JPEG = b"\xff\xd8" + b"Bilddaten" * 2000 + b"\xff\xd9"  # 18 KB, wie ein verkleinertes Foto


def ask(raw, split=False):
    """Schickt eine Anfrage wie das Handy und lässt photo_drop.handle sie bedienen. Liefert (Antwort, Rückgabe).
    split: Kopf und Inhalt getrennt schicken, mit einer kleinen Pause dazwischen (wie manche Handys)."""
    answer, result = [], []

    def phone():
        c = socket.create_connection(("127.0.0.1", port))
        if split:
            cut = raw.index(b"\r\n\r\n") + 4
            c.sendall(raw[:cut])
            time.sleep(0.3)
            c.sendall(raw[cut:])
        else:
            c.sendall(raw)
        data = b""
        try:
            while True:
                chunk = c.recv(4096)
                if not chunk:
                    break
                data += chunk
        except ConnectionResetError:  # abgelehnt, bevor das Foto ganz drüben war: Clippy legt einfach auf
            pass
        answer.append(data)
        c.close()

    t = threading.Thread(target=phone)
    t.start()
    conn, _ = server.accept()
    try:
        result.append(photo_drop.handle(conn, "424242", folder))
    finally:
        conn.close()
    t.join(5)
    return answer[0], result[0]


def post(name, body, token="424242", length=None):
    head = "POST /photo?k=%s&n=%s HTTP/1.1\r\nHost: clippy\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n"
    return (head % (token, name, len(body) if length is None else length)).encode() + body


answer, saved = ask(b"GET /?k=424242 HTTP/1.1\r\nHost: clippy\r\n\r\n")
assert answer.startswith(b"HTTP/1.1 200") and b"Fotos an Clippy" in answer and saved is None
answer, saved = ask(b"GET /?k=111111 HTTP/1.1\r\n\r\n")
assert answer.startswith(b"HTTP/1.1 403") and saved is None  # wer den QR-Code nicht hat, darf nicht
answer, saved = ask(post("Urlaub%20am%20See.jpg", JPEG))
assert answer.startswith(b"HTTP/1.1 200") and saved == "Urlaub_am_See.jpg"
assert open(os.path.join(folder, saved), "rb").read() == JPEG
_, saved = ask(post("Urlaub%20am%20See.jpg", JPEG))
assert saved == "Urlaub_am_See_2.jpg"  # nichts wird überschrieben
answer, saved = ask(post("x.jpg", JPEG, token="000000"))
assert answer[:12] in (b"", b"HTTP/1.1 403") and saved is None  # abgelehnt, mit Antwort oder Abbruch
answer, saved = ask(post("virus.jpg", b"MZ ein Programm"))
assert answer[:12] in (b"", b"HTTP/1.1 400") and saved is None
answer, saved = ask(post("virus.jpg", b"MZ ein Programm"), split=True)  # Inhalt kommt erst später
assert answer[:12] in (b"", b"HTTP/1.1 400") and saved is None
answer, saved = ask(post("spaet.jpg", JPEG), split=True)
assert answer.startswith(b"HTTP/1.1 200") and saved == "spaet.jpg"
answer, saved = ask(post("riesig.jpg", b"\xff\xd8", length=photo_drop.MAX_BYTES + 1))
assert answer[:12] in (b"", b"HTTP/1.1 400") and saved is None
assert sorted(os.listdir(folder)) == ["Urlaub_am_See.jpg", "Urlaub_am_See_2.jpg", "spaet.jpg"]

server.close()
shutil.rmtree(folder)
print("ok")
