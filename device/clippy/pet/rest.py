# Ruhehaltung der Klammer: was sie macht, wenn gerade keine Bewegung läuft.
from clippy.pet import moves
from clippy.pet.draw import REST


def rest_pose(senses, drumming):
    """drumming: es wird gerade mitgetrommelt."""
    if drumming:  # wartet mit erhobenem Schlägel auf den nächsten Schlag
        return dict(REST, arm=50, stick=True, drum=True, brow=2, look=(4, 3))
    if senses.dark:
        return dict(moves.DROWSY)
    if senses.agents.working():  # ein Agent arbeitet: sie schaut gespannt zu
        return dict(REST, look=(-5, -1), brow=2)
    # nachts müde Lider, der Blick folgt der Seitenneigung
    return dict(REST, lid=0.4 if senses.night else 0.0, look=(senses.tilt, 0))
