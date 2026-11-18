# Wo die Klammer gezeichnet wird: in ihrem Feld rechts unten oder, solange sie kippt oder rollt, auf der Bühne,
# einem Streifen in Feldhöhe über die ganze Breite. Darüber das Arbeitswort, wenn ein Agent arbeitet.
import time

from clippy import win98
from clippy.pet import extras
from clippy.pet.draw import FIELD_H, FIELD_W, FIELD_X, FIELD_Y, STAGE_W, STAGE_X, draw

UPRIGHT, UPSIDE_DOWN = 0, 2  # Display-Drehung (setRotation) für das normal stehende und das umgedrehte Gerät


def _on_stage(pose):
    # kippt, liegt oder rollt sie gerade?
    return pose["lean"] > 0 or pose["roll"] != 0


class Stage:
    def __init__(self, display, paint, agents):
        """paint(g): zeichnet den ganzen Desktop nach g; daraus kommt der Hintergrund der Bühne.
        agents: pet.agents.Agents, liefert das Arbeitswort."""
        self.d, self.paint, self.agents = display, paint, agents
        self.work = display.newCanvas(FIELD_W, FIELD_H, 16, True)
        self.back = self.work.newCanvas(FIELD_W, FIELD_H, 16, True)  # Desktop-Ausschnitt, einmal geholt
        win98.backdrop(self.back, FIELD_X, FIELD_Y)
        self.wide = None         # (Leinwand, Hintergrund) der Bühne, erst beim ersten Bedarf angelegt
        self.was_wide = False
        self.frame = 0           # zählt die Bilder; dreht den Stern des Arbeitsworts
        self.narrow = False      # links liegt ein App-Fenster: nie auf die breite Bühne, nur ins Feld
        self.flipped = False     # ist das Display gerade umgedreht

    def repaint(self):
        """Der Desktop hat sich geändert (z. B. ein Symbol): den Hintergrund der Bühne beim nächsten Mal neu holen."""
        self.wide = None

    def needs_wide(self, pose):
        """Kippt, liegt, rollt sie oder steht sie gerade wieder auf? Dann braucht sie die Bühne."""
        return (_on_stage(pose) or self.was_wide) and not self.narrow

    def turn(self, flipped):
        """Das Gerät wurde umgedreht: Display mitdrehen und den Desktop neu zeichnen."""
        self.flipped = flipped
        self.d.setRotation(UPSIDE_DOWN if flipped else UPRIGHT)
        self.paint(self.d)
        self.was_wide = False

    def show(self, pose):
        self.frame += 1
        wide = _on_stage(pose) and not self.narrow
        if wide or (self.was_wide and not self.narrow):
            if self.wide is None:
                work = self.d.newCanvas(STAGE_W, FIELD_H, 16, True)
                back = work.newCanvas(win98.W, win98.H, 16, True)  # der ganze Desktop samt Symbolen
                self.paint(back)
                self.wide = (work, back)
            work, back = self.wide
            back.push(-STAGE_X, -FIELD_Y)
            draw(work, pose, STAGE_W - FIELD_W)
            work.push(STAGE_X, FIELD_Y)
        else:
            self.back.push(0, 0)
            draw(self.work, pose)
            console = self.agents.console(time.ticks_ms())
            if console:  # ein Agent arbeitet: Konsole wie Claude Code im cmd-Fenster über dem Kopf
                extras.console(self.work, console, self.frame, FIELD_W)
            self.work.push(FIELD_X, FIELD_Y)
        self.was_wide = wide
