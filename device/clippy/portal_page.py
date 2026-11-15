# Die Einrichtungsseite, die das Handy bei „WLAN einrichten → Mit Handy“ sieht, und das Auslesen des Formulars.

STYLE = ("body{background:#008080;font-family:Tahoma,Verdana,sans-serif;margin:0;padding:10px}"
         ".w{background:#c0c0c0;border:2px outset #fff;max-width:420px;margin:0 auto}"
         ".t{background:#000080;color:#fff;font-weight:bold;padding:4px 6px}"
         ".c{padding:10px}label{display:block;padding:7px 4px;border-bottom:1px solid #a0a0a0;font-size:17px}"
         "input[type=text],input[type=password]{width:95%;font-size:17px;padding:5px;border:2px inset #fff}"
         "button{font-size:18px;padding:8px 20px;margin-top:12px;background:#c0c0c0;border:2px outset #fff}"
         ".e{color:#a00000;font-weight:bold}")


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def page(networks, note=""):
    """networks: Liste von (Name, Empfang, mit Passwort) aus wifi.scan(). Liefert die Seite als Bytes."""
    rows = []
    for i, (name, _, secure) in enumerate(networks):
        checked = " checked" if i == 0 else ""
        lock = " &#128274;" if secure else ""
        rows.append('<label><input type="radio" name="net" value="%s"%s> %s%s</label>'
                    % (_escape(name), checked, _escape(name), lock))
    rows.append('<label><input type="radio" name="net" value=""%s> Anderes WLAN: '
                '<input type="text" name="other" autocapitalize="off"></label>' % ("" if networks else " checked"))
    html = ('<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Clippy WLAN</title>'
            '<style>%s</style></head><body><div class="w"><div class="t">Clippy - WLAN einrichten</div>'
            '<div class="c">%s<p>Mit welchem WLAN soll sich Clippy verbinden?</p><form method="post" action="/">'
            '%s<p>Passwort:<br><input type="password" name="pw" autocapitalize="off" autocomplete="off"></p>'
            '<button type="submit">Verbinden</button></form>'
            '<p>Danach schließt Clippy dieses Einrichtungs-WLAN. Ob es geklappt hat, steht am Display von Clippy.</p>'
            '</div></div></body></html>') % (STYLE, '<p class="e">%s</p>' % _escape(note) if note else "",
                                             "".join(rows))
    return html.encode()


def done(name):
    """Antwort nach dem Abschicken; danach geht Clippys WLAN zu."""
    return ('<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><style>%s</style></head><body>'
            '<div class="w"><div class="t">Clippy - WLAN einrichten</div><div class="c">'
            '<p>Clippy verbindet sich jetzt mit <b>%s</b>.</p><p>Ob es geklappt hat, steht am Display von Clippy. '
            'Dein Handy verbindet sich wieder mit deinem WLAN.</p></div></div></body></html>'
            % (STYLE, _escape(name))).encode()


def _unquote(s):
    # Formular-Kodierung zurück in Text: + ist ein Leerzeichen, %XX ein Byte
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


def credentials(body):
    """Formular (application/x-www-form-urlencoded, Bytes) → (Netzname, Passwort) oder None, wenn kein Name."""
    fields = {}
    for part in body.decode().split("&"):
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key] = _unquote(value)
    name = fields.get("net") or fields.get("other", "").strip()
    return (name, fields.get("pw", "")) if name else None
