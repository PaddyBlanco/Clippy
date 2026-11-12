# Sprüche der Klammer: je Ereignis eine Liste, aus der zufällig gewählt wird.
import json
import random

PATH = "/flash/apps/phrases.json"
_all = None


def pick(event):
    """Liefert einen Spruch zum Ereignis oder None, wenn es keinen gibt."""
    global _all
    if _all is None:
        try:
            with open(PATH) as f:
                _all = json.load(f)
        except (OSError, ValueError):
            _all = {}  # ohne Datei bleibt sie stumm, stürzt aber nicht ab
    options = _all.get(event)
    return random.choice(options) if options else None
