# WLAN: verbindet beim Start mit dem Netz aus config.WIFI_FILE, sucht Netze, speichert den Zugang.
import json
import time

from clippy import config

try:
    import network
except ImportError:  # am PC (Vorschau) gibt es kein WLAN
    network = None


def _wlan():
    w = network.WLAN(network.STA_IF)
    w.active(True)
    return w


def saved():
    """Gespeicherter Zugang als dict mit "ssid" und "password", oder None."""
    try:
        with open(config.WIFI_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def connect():
    """Startet die Verbindung mit dem gespeicherten Netz, ohne zu warten. Ohne Datei oder WLAN-Modul passiert nichts."""
    cfg = saved()
    if network is None or cfg is None:
        return
    network.hostname(config.HOSTNAME)
    w = _wlan()
    if not w.isconnected():
        w.connect(cfg["ssid"], cfg["password"])


def connected():
    return network is not None and network.WLAN(network.STA_IF).isconnected()


def sync_clock():
    """Stellt die Uhr übers Netz (NTP, UTC; die Zeitzone setzt desktop.run). Liefert True, wenn es geklappt hat."""
    if not connected():
        return False
    try:
        import ntptime
        ntptime.settime()
        return True
    except Exception:  # Zeitserver nicht erreichbar: später nochmal
        return False


def info():
    """(Netzname, Adresse), solange verbunden, sonst None."""
    if not connected():
        return None
    w = network.WLAN(network.STA_IF)
    return w.config("ssid"), w.ifconfig()[0]


def scan():
    """Netze in der Nähe, stärkstes zuerst: Liste von (Name, Empfang in dBm, mit Passwort)."""
    if network is None:
        return []
    best = {}
    for ssid, _, _, rssi, security, _ in _wlan().scan():
        try:
            name = ssid.decode()
        except UnicodeError:
            continue
        if name and (name not in best or rssi > best[name][1]):
            best[name] = (name, rssi, security != 0)
    return sorted(best.values(), key=lambda n: -n[1])


def join(ssid, password, wait_s=20):
    """Verbindet mit einem Netz und wartet höchstens wait_s Sekunden. Klappt es, wird der Zugang gespeichert.
    Klappt es nicht, verbindet sich Clippy wieder mit dem gespeicherten Netz. Liefert True oder False."""
    if network is None:
        return False
    network.hostname(config.HOSTNAME)
    w = _wlan()
    if w.isconnected():
        w.disconnect()
    w.connect(ssid, password)
    hopeless = [getattr(network, n) for n in ("STAT_WRONG_PASSWORD", "STAT_NO_AP_FOUND") if hasattr(network, n)]
    for _ in range(wait_s * 4):
        if w.status() in hopeless:  # falsches Passwort oder Netz weg: nicht weiter warten
            break
        if w.isconnected():
            with open(config.WIFI_FILE, "w") as f:
                json.dump({"ssid": ssid, "password": password}, f)
            return True
        time.sleep_ms(250)
    w.disconnect()
    connect()
    return False
