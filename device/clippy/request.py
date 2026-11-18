# Teile einer Web-Anfrage lesen: Adresse mit ?a=1&b=2 und einen sicheren Dateinamen daraus (für photo_drop.py).


def query(path):
    """'/photo?k=1&n=a.jpg' -> ('/photo', {'k': '1', 'n': 'a.jpg'}), %XX und + entschlüsselt."""
    path, _, rest = path.partition("?")
    out = {}
    for pair in rest.split("&"):
        key, _, value = pair.partition("=")
        if key:
            out[key] = unquote(value)
    return path, out


def unquote(s):
    """Formular- und Adress-Kodierung zurück in Text: 'F%C3%BC+x' -> 'Fü x'. + ist ein Leerzeichen, %XX ein Byte;
    ein % ohne zwei Hex-Ziffern bleibt stehen. Kaputtes UTF-8 wirft UnicodeError (ein ValueError)."""
    s = s.replace("+", " ")
    out, i = bytearray(), 0
    while i < len(s):
        if s[i] == "%" and len(s) - i >= 3:
            try:
                out.append(int(s[i + 1:i + 3], 16))
                i += 3
                continue
            except ValueError:
                pass
        out += s[i].encode()
        i += 1
    return out.decode()


def file_name(name, taken):
    """Name fürs Foto auf der Karte: ohne Endung nur Buchstaben, Ziffern, - und _, dazu .jpg; nie einer aus taken
    (Namen in Kleinbuchstaben). Höchstens 40 Zeichen vor der Endung."""
    base = name.rsplit(".", 1)[0] if "." in name else name
    out, gap = "", False
    for c in base:
        if "0" <= c <= "9" or "a" <= c <= "z" or "A" <= c <= "Z" or c in "-_":
            out, gap = out + c, False
        elif not gap and out:
            out, gap = out + "_", True
    base = out.strip("_")[:40] or "bild"
    out, n = base + ".jpg", 2
    while out.lower() in taken:
        out, n = "%s_%d.jpg" % (base, n), n + 1
    return out
