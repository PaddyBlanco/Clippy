# WLAN: verbindet beim Start mit dem Netz aus config.WIFI_FILE, ohne auf die Verbindung zu warten.
import json

from clippy import config

try:
    import network
except ImportError:  # am PC (Vorschau) gibt es kein WLAN
    network = None


def connect():
    """Startet die Verbindung. Ohne Datei oder ohne WLAN-Modul passiert nichts."""
    if network is None:
        return
    try:
        with open(config.WIFI_FILE) as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return
    network.hostname(config.HOSTNAME)
    w = network.WLAN(network.STA_IF)
    w.active(True)
    if not w.isconnected():
        w.connect(cfg["ssid"], cfg["password"])


def connected():
    return network is not None and network.WLAN(network.STA_IF).isconnected()
