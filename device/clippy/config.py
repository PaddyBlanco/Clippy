# Einstellungen an einer Stelle. Wer das Repo übernimmt, ändert nur hier.

# Adresse des Handbuchs; das Startmenü zeigt sie als QR-Code.
MANUAL_URL = "https://paddyblanco.github.io/Clippy/"  # Handbuch-Webseite aus manual/, siehe docs/manual.md

# Wo abgerufene Apps und Sprüche am Gerät liegen
APPS_DIR = "/flash/apps"

# WLAN-Zugang {"ssid": ..., "password": ...}; kommt aus local/wifi.json, liegt nie im Repo
WIFI_FILE = "/flash/wifi.json"
HOSTNAME = "clippy"  # vom PC aus erreichbar als clippy.local

# Port, auf dem die Hook-Meldungen der Coding-Agents ankommen (siehe docs/agent-hooks.md)
AGENT_PORT = 4711
# Diesen Satz tippt man in Claude Code, Codex oder Copilot; die Anleitung für den Agent liegt in manual/verbinden.txt
CONNECT_SENTENCE = "Richte Clippy ein: paddyblanco.github.io/Clippy/verbinden.txt"
