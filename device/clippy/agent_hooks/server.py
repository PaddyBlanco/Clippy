# Kleiner Webserver für die Hook-Meldungen der Coding-Agents (docs/agent-hooks.md).
# POST /<agent> mit dem Hook-JSON, GET /<agent>/probe zum Ausprobieren, GET / zeigt „Clippy hört zu“.
import json
import socket
import time

from clippy import config, wifi

HOST = "0.0.0.0"       # alle Adressen; der Selbsttest am PC nimmt nur 127.0.0.1
MAX_JSON = 32 * 1024   # größere Meldungen nicht als Ganzes lesen, sondern nur die nötigen Felder suchen
MAX_KEEP = 64 * 1024   # so viel vom Anfang einer Meldung aufheben; der Rest wird nur abgeholt
FIELDS = ("hook_event_name", "notification_type")
TEXT = "HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nConnection: close\r\n\r\n%s\n"


def fields(raw):
    """Die nötigen Textfelder aus einer (zu großen oder abgeschnittenen) Meldung, ohne JSON zu lesen."""
    out = {}
    for key in FIELDS:
        at = raw.find(b'"' + key.encode() + b'"')
        colon = raw.find(b":", at) if at >= 0 else -1
        start = raw.find(b'"', colon) if colon >= 0 else -1
        end = raw.find(b'"', start + 1) if start >= 0 else -1
        if end > start >= 0:
            out[key] = raw[start + 1:end].decode()
    return out


def parse(raw):
    """Hook-Meldung als dict; bei kaputtem oder sehr großem JSON nur die nötigen Felder."""
    if len(raw) <= MAX_JSON:
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload
        except ValueError:
            pass
    return fields(raw)


class HookServer:
    def __init__(self):
        self.sock = None
        self.next_try = time.ticks_ms()

    def _listen(self, now):
        """Öffnet den Port, sobald das WLAN steht; bis dahin einmal je Sekunde nachsehen."""
        if self.sock is None and time.ticks_diff(now, self.next_try) > 0:
            self.next_try = time.ticks_add(now, 1000)
            if wifi.connected():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((HOST, config.AGENT_PORT))
                    s.listen(4)
                    s.setblocking(False)
                    self.sock = s
                except OSError:
                    pass
        return self.sock

    def poll(self, now):
        """Bedient höchstens eine Anfrage. Liefert (Agent, Meldung als dict) oder None."""
        sock = self._listen(now)
        if sock is None:
            return None
        try:
            conn, _ = sock.accept()
        except OSError:
            return None  # niemand da
        try:
            conn.settimeout(2)
            data = b""
            while b"\r\n\r\n" not in data and len(data) < 8192:  # Kopfzeilen können in Stücken kommen
                chunk = conn.recv(2048)
                if not chunk:
                    break
                data += chunk
            cut = data.find(b"\r\n\r\n")
            if cut < 0:
                return None  # keine vollständige Anfrage
            head, body = data[:cut].decode(), data[cut + 4:]
            method, path = head.split(" ")[:2]
            parts = path.strip("/").split("/")
            if method != "POST":
                if len(parts) > 1 and parts[1] == "probe":
                    conn.send((TEXT % "Clippy freut sich.").encode())
                    return parts[0], {"hook_event_name": "Stop"}
                conn.send((TEXT % "Clippy hört zu.").encode())
                return None
            length = 0
            for line in head.lower().split("\r\n"):
                if line.startswith("content-length:"):
                    length = int(line[15:])
                if line.startswith("expect:") and "100-continue" in line:
                    conn.send(b"HTTP/1.1 100 Continue\r\n\r\n")  # sonst wartet curl bei großen Meldungen 1 s
            received = len(body)
            while received < length:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                received += len(chunk)
                if len(body) < MAX_KEEP:
                    body += chunk
            conn.send((TEXT % "ok").encode())
            return parts[0], parse(body)
        except (OSError, ValueError, IndexError):
            return None
        finally:
            conn.close()
