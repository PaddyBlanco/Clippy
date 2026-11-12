"""Macht aus einer TTF-Schrift eine geglättete Geräte-Schrift (VLW-Format, lesbar mit Display.loadFont).

    python tools/make_font.py local/fonts/dejavu/DejaVuSans.ttf 12 device/res/font12.vlw

Enthält ASCII, deutsche Umlaute und ein paar Satzzeichen. Die Schrift muss frei weitergegeben werden dürfen.
"""
import struct
import sys

from PIL import ImageFont

CHARS = "".join(chr(c) for c in range(0x21, 0x7F)) + "ÄÖÜäöüß€°–…„“”’·×"


def build(ttf, size):
    font = ImageFont.truetype(ttf, size)
    ascent, descent = font.getmetrics()
    table, bitmaps = b"", b""
    for ch in sorted(set(CHARS)):  # das Gerät sucht binär, also aufsteigend sortiert
        left, top, right, bottom = font.getbbox(ch)
        mask = font.getmask(ch, mode="L")
        w, h = mask.size
        assert (w, h) == (right - left, bottom - top), ch
        # Zeichencode, Höhe, Breite, Vorschub, Oberkante über der Grundlinie, linker Versatz, Füllfeld
        table += struct.pack(">7i", ord(ch), h, w, round(font.getlength(ch)), ascent - top, left, 0)
        bitmaps += bytes(mask)
    header = struct.pack(">6I", len(set(CHARS)), 11, ascent + descent, 0, ascent, descent)
    return header + table + bitmaps


def selftest(data):
    count, version, _, _, ascent, descent = struct.unpack(">6I", data[:24])
    rows = [struct.unpack(">7i", data[24 + i * 28:52 + i * 28]) for i in range(count)]
    assert version == 11 and ascent > 0 and descent >= 0
    assert [r[0] for r in rows] == sorted(r[0] for r in rows), "nicht sortiert"
    assert len(data) == 24 + count * 28 + sum(r[1] * r[2] for r in rows), "Bitmap-Länge passt nicht"


if __name__ == "__main__":
    ttf, size, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    data = build(ttf, size)
    selftest(data)
    with open(out, "wb") as f:
        f.write(data)
    print("%s: %d Bytes" % (out, len(data)))
