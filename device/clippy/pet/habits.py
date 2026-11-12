# Gewohnheiten der Klammer als Tabellen: was sie von selbst tut und wie sie auf Ereignisse reagiert.
# Hier wird eingestellt, nicht programmiert. Die Bewegungen selbst stehen in moves.py.
from clippy.pet import moves

# Was sie von selbst tut: Bewegung -> (erstes Mal nach ms, danach Pause von, bis in ms)
IDLE = {
    moves.blink: (2500, 2500, 6000),
    moves.glance: (6000, 8000, 20000),
    moves.curl: (60000, 180000, 360000),
    moves.bored: (30000, 30000, 70000),   # nur nach längerer Ruhe, siehe QUIET
    moves.nod: (50000, 60000, 150000),    # ebenso
    moves.zap: (25000, 20000, 40000),     # nur solange sie lädt
}
# Diese kommen erst, wenn so viele Sekunden lang kein Ereignis war
QUIET = {moves.bored: 120, moves.nod: 210}
# Zu diesen sagt sie bei jedem zweiten Mal etwas: Bewegung -> Name in phrases.json
SPOKEN = {moves.curl: "curl", moves.bored: "bored", moves.nod: "nod"}

# Wie sie reagiert: Ereignis -> (Bewegung, Mindestabstand in s, wie oft sie etwas dazu sagt von 0 bis 1)
REACT = {
    "shake": (moves.dizzy, 4, 1),
    "face_down": (moves.grump, 10, 1),
    "near": (moves.perk, 15, 0.5),
    "tap": (moves.flinch, 0, 0.4),
    "grumpy": (moves.threaten, 0, 1),
    "pet": (moves.enjoy, 0, 0),
    "loud": (moves.startle, 3, 1),
    "beat": (moves.hit, 0, 0),
    "plugged": (moves.zap, 0, 1),
    "low_battery": (moves.yawn, 0, 1),
}
# Andauerndes: Ereignis -> (Spruch-Name zu Beginn, gilt so viele ms nach dem letzten Ereignis noch als andauernd)
ONGOING = {"beat": ("drum", 1500), "pet": ("pet", 900)}
# Manchmal reagiert sie anders: Ereignis -> (Bewegung, Spruch danach, wie oft von 0 bis 1)
SOMETIMES = {"shake": (moves.fall, "fall", 0.35)}

BRIGHT, DIM = 220, 60  # Helligkeit wach und schlafend, von 0 bis 255
SLEEP_AFTER_DARK, SLEEP_AFTER_NIGHT = 300, 180  # Sekunden ohne Ereignis, bis sie einschläft
SNOT_CHANCE = 0.1  # bei jedem zehnten Einschlafen schläft sie mit Rotzblase
