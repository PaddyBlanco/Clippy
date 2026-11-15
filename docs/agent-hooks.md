# Coding-Agents mit der Klammer verbinden

Claude Code, Codex und GitHub Copilot melden über **Hooks**, was sie gerade tun. Ein Skript am PC übersetzt jede
Meldung in einen von vier Zuständen und schickt ihn per WLAN an das Gerät. Dort reagiert die Klammer, und unten in
der Taskleiste zeigt ein Kästchen je Agent den Zustand.

```
Agent-Hook ──JSON auf stdin──▶ tools/agent_hook.py <agent> ──UDP──▶ clippy.local:4711 ──▶ pet/agents.py
```

## Zustände

| Zustand | Bedeutung | Klammer | Kästchen |
|---|---|---|---|
| `working` | Agent arbeitet (Anfrage bekommen, Werkzeug benutzt) | merkt auf; solange gearbeitet wird, schaut sie gespannt zur Seite; Spruch höchstens alle 30 s | gelb |
| `waiting` | Agent wartet auf eine Freigabe oder Antwort | hüpft, winkt, ruft; wiederholt alle 30 s, bis ein neuer Zustand kommt oder du sie antippst | rot |
| `done` | Agent ist mit seiner Antwort fertig | freut sich und sagt es | grün |
| `gone` | Sitzung beendet | – | verschwindet |

Kommt 30 Minuten lang nichts von einem Agent, verschwindet sein Kästchen ebenfalls. Mehrere Sitzungen desselben
Agents teilen sich ein Kästchen; die letzte Meldung gilt.

## Welcher Hook welchen Zustand meldet

| Agent | `working` | `waiting` | `done` | `gone` |
|---|---|---|---|---|
| Claude Code | `UserPromptSubmit`, `PostToolUse` | `PermissionRequest`; `Notification` mit `permission_prompt` oder `agent_needs_input` | `Stop`, `StopFailure` | `SessionEnd` |
| Codex | `UserPromptSubmit`, `PostToolUse` | `PermissionRequest` | `Stop`, `Interrupt` | `SessionEnd` |
| Copilot (CLI und VS Code) | `UserPromptSubmit`, `PostToolUse` | `PermissionRequest`; `notification` mit `permission_prompt` | `Stop` | `SessionEnd` |

Alle drei schicken ein JSON-Objekt auf stdin, in dem `hook_event_name` den Hook nennt (bei Copilot nur, wenn die
Hooks in der VS-Code-Schreibweise `Stop`, `PostToolUse`, ... eingetragen sind, siehe unten). Andere Hooks und
Benachrichtigungen werden ignoriert.

## Aufbau am PC

| Datei | Aufgabe |
|---|---|
| `tools/agent_hook.py` | Wird vom Hook aufgerufen: `python tools/agent_hook.py claude`. Liest stdin, fragt den Agent nach dem Zustand, schickt das Paket. Endet immer mit 0 und schweigt, auch ohne Gerät |
| `tools/agents/base.py` | Schnittstelle `Agent`: `name` (Anzeige), `short` (Kürzel im Kästchen, zwei Zeichen), Hook-Namen je Zustand, `state(payload)` liefert den Zustand oder `None` |
| `tools/agents/claude.py`, `codex.py`, `copilot.py` | Je Agent eine Klasse; ändert nur, was bei ihm anders ist |
| `tools/agents/__init__.py` | `AGENTS`: Name auf der Befehlszeile → Klasse |

**Neuer Agent:** Datei in `tools/agents/` mit einer Unterklasse von `Agent`, in `AGENTS` eintragen, Hooks des Agents
auf `python tools/agent_hook.py <name>` richten, Tabelle oben ergänzen. Am Gerät ist nichts zu tun.

Adresse: `clippy.local`, abweichend mit der Umgebungsvariable `CLIPPY_HOST`. Die Namensauflösung kann bei
ausgeschaltetem Gerät einige Sekunden dauern; das Skript merkt sich deshalb die Adresse 10 Minuten lang und einen
Fehlschlag 1 Minute lang in `%TEMP%\clippy-address.txt`.

## Nachricht ans Gerät

UDP an Port 4711 (`config.AGENT_PORT`), je Paket ein JSON-Objekt:

```json
{"agent": "Claude", "short": "Cl", "state": "working"}
```

Das Gerät braucht keinen Code je Agent: `agent` steht in den Sprüchen (`{agent}` in `apps/phrases.json`),
`short` im Kästchen. Kein Rückkanal; ist das Gerät aus, geht die Meldung verloren.

## Am Gerät

`device/clippy/wifi.py` verbindet sich beim Start mit dem WLAN aus `/flash/wifi.json`, ohne zu warten.
`device/clippy/pet/agents.py` horcht, sobald die Verbindung steht, auf dem Port, merkt sich je Agent den Zustand
und meldet der Klammer die Ereignisse `agent_working`, `agent_waiting` und `agent_done` (siehe [pet.md](pet.md)).
Die Taskleiste zeichnet die Kästchen links neben der Uhr (`shell.tray`).

## Einrichten

1. **WLAN:** `local/wifi.json` anlegen (liegt nicht im Repo):
   `{"ssid": "MeinNetz", "password": "..."}`. `tools/install.ps1` kopiert sie nach `/flash/wifi.json`.
2. **Probe ohne Agent:** `'{"hook_event_name": "Stop"}' | python tools/agent_hook.py claude` → die Klammer freut sich.
3. **Hooks eintragen**, jeweils in den Benutzereinstellungen (gelten für alle Projekte). `<REPO>` ist der Pfad zu
   diesem Repo mit Schrägstrichen, z. B. `C:/Projects/Clippy`.

**Claude Code**, `~/.claude/settings.json` (laufen mit `async` im Hintergrund, Claude wartet nicht):

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "PostToolUse": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "PermissionRequest": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "Notification": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "StopFailure": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "async": true}]}],
    "SessionEnd": [{"hooks": [{"type": "command", "command": "python", "args": ["<REPO>/tools/agent_hook.py", "claude"], "timeout": 3}]}]
  }
}
```

Nicht in die Projektdatei `.claude/settings.json` eintragen: Copilot liest die mit und würde sich als Claude melden.

**Codex**, `~/.codex/config.toml`, je Hook ein Block dieser Art (`UserPromptSubmit`, `PostToolUse`,
`PermissionRequest`, `Stop`, `Interrupt`; bei `SessionEnd` ohne `async`, das läuft immer synchron):

```toml
[[hooks.Stop]]
[[hooks.Stop.hooks]]
type = "command"
command = 'python "<REPO>/tools/agent_hook.py" codex'
async = true
```

**Copilot** (Kommandozeile und VS Code), `~/.copilot/hooks/clippy.json`. Die Hook-Namen in VS-Code-Schreibweise,
nur dann steht `hook_event_name` im JSON; Copilot kennt kein `async`, daher kurze Wartezeit:

```json
{
  "version": 1,
  "hooks": {
    "UserPromptSubmit": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}],
    "PostToolUse": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}],
    "PermissionRequest": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}],
    "notification": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}],
    "Stop": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}],
    "SessionEnd": [{"type": "command", "command": "python \"<REPO>/tools/agent_hook.py\" copilot", "timeoutSec": 5}]
  }
}
```

Copilot-Hooks in VS Code sind laut Hersteller noch eine Vorschau und können sich ändern.

## Quellen

- Claude Code: https://code.claude.com/docs/en/hooks.md
- Codex: https://learn.chatgpt.com/docs/hooks
- Copilot: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference,
  https://code.visualstudio.com/docs/copilot/customization/hooks
