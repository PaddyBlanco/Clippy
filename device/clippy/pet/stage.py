# Wo die Klammer gezeichnet wird: in ihrem Feld rechts unten oder, solange sie kippt oder rollt, auf der Bühne,
# einem Streifen in Feldhöhe über die ganze Breite.
from clippy import win98
from clippy.pet.draw import FIELD_H, FIELD_W, FIELD_X, FIELD_Y, STAGE_W, STAGE_X, draw


class Stage:
    def __init__(self, display, paint):
        """paint(g): zeichnet den ganzen Desktop nach g; daraus kommt der Hintergrund der Bühne."""
        self.d, self.paint = display, paint
        self.work = display.newCanvas(FIELD_W, FIELD_H, 16, True)
        self.back = self.work.newCanvas(FIELD_W, FIELD_H, 16, True)  # Desktop-Ausschnitt, einmal geholt
        win98.backdrop(self.back, FIELD_X, FIELD_Y)
        self.wide = None         # (Leinwand, Hintergrund) der Bühne, erst beim ersten Bedarf angelegt
        self.was_wide = False

    def needs_wide(self, pose):
        """Kippt, liegt, rollt sie oder steht sie gerade wieder auf? Dann braucht sie die Bühne."""
        return pose["lean"] > 0 or pose["roll"] != 0 or self.was_wide

    def show(self, pose):
        wide = pose["lean"] > 0 or pose["roll"] != 0
        if wide or self.was_wide:
            if self.wide is None:
                work = self.d.newCanvas(STAGE_W, FIELD_H, 16, True)
                back = work.newCanvas(320, 240, 16, True)  # der ganze Desktop samt Symbolen
                self.paint(back)
                self.wide = (work, back)
            work, back = self.wide
            back.push(-STAGE_X, -FIELD_Y)
            draw(work, pose, STAGE_W - FIELD_W)
            work.push(STAGE_X, FIELD_Y)
        else:
            self.back.push(0, 0)
            draw(self.work, pose)
            self.work.push(FIELD_X, FIELD_Y)
        self.was_wide = wide
