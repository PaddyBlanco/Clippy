# Bildschirm-Tastatur im Windows-98-Stil für Texteingaben (z. B. das WLAN-Passwort).
# Zeichnet in einen Canvas von 320×218 (die Fläche eines App-Fensters) und sagt, welche Taste getippt wurde.
from clippy import win98

KEY_W, KEY_H, PITCH = 30, 29, 32   # Taste, Abstand von Taste zu Taste
TOP = 54                           # erste Tastenreihe; darüber Frage und Eingabefeld
LETTERS = ("1234567890", "qwertzuiop", "asdfghjkl-", "yxcvbnm.")  # je Reihe höchstens 10 Tasten, die unterste
                                                                   # bekommt noch Umschalten und Löschen dazu
SYMBOLS = ("1234567890", "!\"#$%&/()=", "?@_+*'~;:,", "<>[]{}\\|^")
SHIFT, BACK, PAGE, SPACE, OK, CANCEL = "aA", "<-", "#+=", " ", "OK", "Abbr."


class Keyboard:
    def __init__(self, question, text=""):
        self.question, self.text = question, text
        self.symbols = self.upper = False

    def keys(self):
        """Alle Tasten als (x, y, w, h, Beschriftung)."""
        rows = SYMBOLS if self.symbols else LETTERS
        out = []
        for r, row in enumerate(rows):
            labels = list(row.upper() if self.upper and not self.symbols else row)
            if r == 3:  # unterste Zeichenreihe: links Umschalten, rechts Löschen
                labels = [SHIFT] + labels if not self.symbols else labels
                labels = labels + [BACK]
            for i, label in enumerate(labels):
                out.append((1 + i * PITCH, TOP + r * PITCH, KEY_W, KEY_H, label))
        y = TOP + 4 * PITCH
        page = "abc" if self.symbols else PAGE
        for x, w, label in ((1, 46, page), (49, 126, SPACE), (177, 70, CANCEL), (249, 70, OK)):
            out.append((x, y, w, KEY_H + 3, label))
        return out

    def draw(self, g):
        g.fillScreen(win98.FACE)
        win98.text(g, self.question, 6, 4, win98.DARK, win98.FACE)
        for x, y, w, h, label in self.keys():
            win98.button(g, x, y, w, h, "Leertaste" if label == SPACE else label, bold=label == OK)
        self.draw_text(g)

    def draw_text(self, g):
        win98.bevel(g, 4, 24, 312, 24, raised=False)
        g.fillRect(6, 26, 308, 20, win98.LIGHT)
        shown = self.text
        while shown and win98.text_width(g, shown + "_") > 300:
            shown = shown[1:]  # zu lang: nur das Ende zeigen
        win98.text(g, shown + "_", 9, 29, win98.DARK, win98.LIGHT)

    def tap(self, g, x, y):
        """Verarbeitet einen Tipper und zeichnet nach. Liefert "ok", "cancel" oder None (weiter tippen)."""
        for kx, ky, w, h, label in self.keys():
            if kx <= x < kx + w + 2 and ky <= y < ky + h + 3:
                break
        else:
            return None
        if label == OK:
            return "ok"
        if label == CANCEL:
            return "cancel"
        if label in (SHIFT, PAGE, "abc"):
            if label == SHIFT:
                self.upper = not self.upper
            else:
                self.symbols = not self.symbols
            self.draw(g)
            return None
        self.text = self.text[:-1] if label == BACK else self.text + label
        self.draw_text(g)
        return None
