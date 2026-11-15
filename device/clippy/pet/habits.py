# Gewohnheiten der Klammer als Tabellen: was sie von selbst tut und wie sie auf Ereignisse reagiert.
# Hier wird eingestellt, nicht programmiert. Die Bewegungen selbst stehen in moves.py.
from clippy.pet import moves
from clippy.pet.boredom import bored
from clippy.pet.tumble import tumble

# Was sie von selbst tut: Bewegung -> (erstes Mal nach ms, danach Pause von, bis in ms)
IDLE = {
    moves.blink: (2500, 2500, 6000),
    moves.glance: (6000, 8000, 20000),
    moves.curl: (60000, 180000, 360000),
    moves.lean_on: (40000, 120000, 300000),
    moves.attention: (75000, 120000, 240000),  # nur wenn sich eine Weile niemand um sie kümmert, siehe QUIET
    bored: (60000, 15000, 30000),         # nur nach längerer Ruhe, siehe QUIET
}
# Was sie stattdessen tut, solange es finster ist: gegen den Schlaf kämpfen
TIRED = {moves.drowsy: (2500, 2500, 5000)}
# Diese kommen erst, wenn so viele Sekunden lang kein Ereignis war
QUIET = {moves.attention: 60, bored: 60}
# Zu diesen sagt sie bei jedem zweiten Mal etwas: Bewegung -> Name in phrases.json
SPOKEN = {moves.curl: "curl", moves.attention: "attention", bored: "bored"}

# Wie sie reagiert: Ereignis -> (Bewegung, Mindestabstand in s, wie oft sie etwas dazu sagt von 0 bis 1)
REACT = {
    "shake": (moves.dizzy, 4, 1),
    "dark": (moves.drowsy, 10, 1),
    "near": (moves.perk, 15, 0.5),
    "tap": (moves.flinch, 0, 0.4),
    "grumpy": (moves.threaten, 0, 1),
    "pet": (moves.enjoy, 0, 0),
    "loud": (moves.startle, 3, 1),
    "beat": (moves.hit, 0, 0),
    "plugged": (moves.zap, 0, 1),
    "low_battery": (moves.yawn, 0, 1),
    "flip": (tumble, 0, 0),  # Spruch erst nach dem Rollen, siehe SOMETIMES
}
# Andauerndes: Ereignis -> (Spruch-Name zu Beginn, gilt so viele ms nach dem letzten Ereignis noch als andauernd)
ONGOING = {"beat": ("drum", 1500), "pet": ("pet", 900)}
# Manchmal reagiert sie anders: Ereignis -> (Bewegung, Spruch danach, wie oft von 0 bis 1)
SOMETIMES = {"shake": (moves.fall, "fall", 0.35), "flip": (tumble, "flip", 1)}

BRIGHT, DUSK, DIM = 220, 110, 60  # Helligkeit wach, bei zugehaltenem Sensor und schlafend, von 0 bis 255
# Sekunden ohne Ereignis, bis sie einschläft; nach der halben Zeit nickt sie einmal ein
SLEEP_AFTER_COVERED, SLEEP_AFTER_NIGHT, SLEEP_AFTER_DARK = 40, 180, 300  # Sensor zugehalten, nachts, dunkler Raum
SNOT_CHANCE = 0.1  # bei jedem zehnten Einschlafen schläft sie mit Rotzblase
