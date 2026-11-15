# „WLAN einrichten“ aus dem Startmenü: Netz wählen, Passwort eingeben, verbinden. Läuft im App-Fenster (Ctx),
# der Ablauf steht in docs/architecture.md unter „Startmenü“.
from clippy import config, wifi, wifi_portal, win98
from clippy.keyboard import Keyboard
from clippy.win98 import DARK, FACE

ROW_Y, ROW_H, ROWS = 26, 30, 5   # Netzliste: erste Zeile, Zeilenhöhe, Zeilen je Seite
BAR_Y, BAR_H = 182, 32           # Knopfleiste unten


def _wait(ctx):
    """Nächster Tipper (x, y) im Fenster; None, wenn das Fenster über das X geschlossen wurde."""
    while ctx.update():
        if ctx.tap:
            return ctx.tap
    return None


def _say(ctx, lines, buttons=()):
    """Zeigt Zeilen und Knöpfe. Mit Knöpfen: wartet und liefert die Nummer des getippten Knopfs, None = zu."""
    g = ctx.screen
    g.fillScreen(FACE)
    for i, line in enumerate(lines):
        win98.text(g, line, 160, 40 + i * 24, DARK, FACE, align="center")
    w = 140
    xs = [160 - (len(buttons) * (w + 8) - 8) // 2 + i * (w + 8) for i in range(len(buttons))]
    for x, caption in zip(xs, buttons):
        win98.button(g, x, BAR_Y, w, BAR_H, caption)
    ctx.show()
    while buttons:
        tap = _wait(ctx)
        if tap is None:
            return None
        for i, x in enumerate(xs):
            if x <= tap[0] < x + w and tap[1] >= BAR_Y - 6:
                return i


def _pick(ctx):
    """Zeigt die Netze in der Nähe. Liefert ("net", Name, mit Passwort), ("phone", Netze) für „Mit Handy“
    oder None, wenn das Fenster geschlossen wurde."""
    nets, page = None, 0
    while True:
        g = ctx.screen
        if nets is None:
            _say(ctx, ["Suche WLANs ..."])
            nets, page = wifi.scan(), 0
        g.fillScreen(FACE)
        now = wifi.info()
        win98.text(g, "Verbunden mit " + now[0] if now else "Wähle dein WLAN:", 6, 4, DARK, FACE)
        shown = nets[page * ROWS:(page + 1) * ROWS]
        more = len(nets) > (page + 1) * ROWS
        for i, (name, rssi, secure) in enumerate(shown):
            y = ROW_Y + i * ROW_H
            win98.bevel(g, 4, y, 312, ROW_H - 2)
            win98.text(g, name[:26], 12, y + 6, DARK, FACE)
            if secure:
                win98.lock(g, 262, y + 6)
            win98.signal(g, 284, y + 6, 4 if rssi > -55 else 3 if rssi > -65 else 2 if rssi > -75 else 1)
        if not nets:
            win98.text(g, "Kein WLAN gefunden.", 160, 90, DARK, FACE, align="center")
        win98.button(g, 4, BAR_Y, 100, BAR_H, "Neu suchen")
        win98.button(g, 108, BAR_Y, 100, BAR_H, "Mit Handy", bold=True)
        if page > 0:
            win98.button(g, 214, BAR_Y, 48, BAR_H, "<")
        if more:
            win98.button(g, 268, BAR_Y, 48, BAR_H, ">")
        ctx.show()
        tap = _wait(ctx)
        if tap is None:
            return None
        x, y = tap
        if y >= BAR_Y - 6:
            if x < 106:
                nets = None
            elif x < 210:
                return "phone", nets
            elif x < 264 and page > 0:
                page -= 1
            elif x >= 264 and more:
                page += 1
        elif ROW_Y <= y < ROW_Y + len(shown) * ROW_H:
            name, _, secure = shown[(y - ROW_Y) // ROW_H]
            return "net", name, secure


def _password(ctx, name, text):
    """Passwort über die Tastatur. Liefert den Text, "" bei Abbrechen oder None, wenn das Fenster zu ist."""
    kb = Keyboard("Passwort für %s:" % name[:22], text)
    kb.draw(ctx.screen)
    ctx.show()
    while True:
        tap = _wait(ctx)
        if tap is None:
            return None
        answer = kb.tap(ctx.screen, *tap)
        ctx.show()
        if answer == "ok":
            return kb.text
        if answer == "cancel":
            return ""


def _connect(ctx, name, password, buttons):
    """Verbindet. Klappt es: Erfolg zeigen, None. Sonst: Fehler und Knöpfe zeigen, Nummer des Knopfs (None = zu)."""
    _say(ctx, ["Verbinde mit", name, "..."])
    if wifi.join(name, password):
        now = wifi.info()
        _say(ctx, ["Verbunden mit " + name, "Adresse " + (now[1] if now else "?"),
                   "Im Netz heißt Clippy " + config.HOSTNAME + ".local"], ["Fertig"])
        return None
    return _say(ctx, ["Hat nicht geklappt.", "Passwort falsch oder WLAN zu weit weg?"], buttons)


def run(ctx):
    while True:
        picked = _pick(ctx)
        if picked is None:
            return
        if picked[0] == "phone":
            got = wifi_portal.run(ctx, picked[1])
            if got is None:
                wifi.connect()  # abgebrochen: zurück zum gespeicherten WLAN
                return
            if _connect(ctx, got[0], got[1], ["Andere WLANs"]) is None:
                return
            continue
        _, name, secure = picked
        password = ""
        while True:
            if secure:
                password = _password(ctx, name, password)
                if password is None:
                    return
                if not password:
                    break  # abgebrochen: zurück zur Liste
            buttons = ["Nochmal", "Andere WLANs"] if secure else ["Andere WLANs"]
            choice = _connect(ctx, name, password, buttons)
            if choice is None:
                return
            if not secure or choice == 1:
                break
