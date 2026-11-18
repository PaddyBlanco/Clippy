# Bilder auf der Karte finden (in `with ctx.card():`) und aus den gelesenen Daten bestimmen, wie groß sie sind und
# ob das Gerät sie zeichnen kann.
# Videos und alles andere werden übergangen; progressive JPEGs kann die Firmware nicht (docs/device.md).
import os

EXT = (".jpg", ".jpeg", ".png")
DEPTH, LIMIT = 4, 3000  # so tief in Unterordner (z. B. DCIM/Camera); höchstens so viele Bilder


def _entries(path):
    """(Name, ist Ordner) je Eintrag. Am Gerät ilistdir (schnell), am PC stat."""
    if hasattr(os, "ilistdir"):
        for e in os.ilistdir(path):
            yield e[0], e[1] == 0x4000
    else:
        for name in os.listdir(path):
            yield name, os.stat(path + "/" + name)[0] & 0x4000 != 0


def find(root):
    """Alle Bilder unter root, nach Pfad sortiert (Fotos einer Kamera damit nach Zeit)."""
    found, todo = [], [(root, 0)]
    while todo and len(found) < LIMIT:
        path, depth = todo.pop()
        for name, folder in _entries(path):
            if name.startswith(".") or name == "System Volume Information":
                continue  # versteckt oder von Windows
            full = path + "/" + name
            if folder:
                if depth < DEPTH:
                    todo.append((full, depth + 1))
            elif name.lower().endswith(EXT):
                found.append(full)
    found.sort()
    return found[:LIMIT]


def _jpeg(d):
    # Abschnitte bis zum Bildkopf (SOF) überspringen; nur SOF0 und SOF1 kann das Gerät zeichnen
    if d[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 4 <= len(d):
        if d[i] != 0xFF:
            return None
        kind = d[i + 1]
        if kind == 0xFF:  # Füllbyte
            i += 1
            continue
        if kind == 0x01 or 0xD0 <= kind <= 0xD7:  # Abschnitte ohne Länge
            i += 2
            continue
        if 0xC0 <= kind <= 0xCF and kind not in (0xC4, 0xC8, 0xCC):  # Bildkopf
            if kind not in (0xC0, 0xC1) or i + 9 > len(d):
                return None  # progressiv, verlustfrei oder arithmetisch: kann die Firmware nicht
            return d[i + 7] << 8 | d[i + 8], d[i + 5] << 8 | d[i + 6]
        i += 2 + (d[i + 2] << 8 | d[i + 3])
    return None


def _png(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(d[16:20], "big"), int.from_bytes(d[20:24], "big")


def size(data, path):
    """(Breite, Höhe), wenn das Gerät das Bild zeichnen kann, sonst None. data: der Inhalt der Datei."""
    got = _png(data) if path.lower().endswith(".png") else _jpeg(data)
    return got if got and got[0] > 0 and got[1] > 0 else None


def fit(w, h, room_w, room_h):
    """(x, y, Maßstab), damit ein Bild w × h ganz und mittig in room_w × room_h passt."""
    k = min(room_w / w, room_h / h)
    return (room_w - int(w * k)) // 2, (room_h - int(h * k)) // 2, k
