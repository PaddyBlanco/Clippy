# Coding-Agents mit der Klammer verbinden

Claude Code, Codex und GitHub Copilot melden über **Hooks**, was sie gerade tun. Jeder Hook schickt sein
JSON unverändert mit `curl` an Clippy; Clippy wertet es selbst aus. Am PC braucht es dafür nichts außer `curl`
(in Windows 10/11, macOS und Linux eingebaut): kein Python, kein Repo, kein Skript.

```
Agent-Hook ──JSON auf stdin──▶ curl ──HTTP POST──▶ clippy.local:4711/<agent> ──▶ agent_hooks/ ──▶ pet/agents.py
```

## Einrichten (für Beschenkte)

1. WLAN am Gerät einrichten (Startmenü → „WLAN einrichten“ → „Mit Handy“).
2. Startmenü → **„Mit PC verbinden“**: Clippy zeigt einen Satz. Den Satz in Claude Code, Codex oder Copilot
   eintippen oder kopieren:
   `Richte Clippy ein: paddyblanco.github.io/Clippy/verbinden.txt`
3. Der Agent liest die Anleitung, trägt die Hooks in seine Benutzereinstellungen ein, fragt dabei nach und
   schickt zum Schluss eine Probe: Die Klammer springt vor Freude.

`manual/verbinden.txt` ist die Anleitung **für den Agent** (nicht für Menschen): je Agent und Betriebssystem
die genauen Einträge, und dass Bestehendes ergänzt statt überschrieben wird. Die Handbuch-Seite
`manual/verbinden.html` erklärt dasselbe für Menschen und zeigt den Satz zum Kopieren.

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

Alle drei schicken ein JSON-Objekt, in dem `hook_event_name` den Hook nennt (bei Copilot nur, wenn die Hooks in
der VS-Code-Schreibweise `Stop`, `PostToolUse`, ... eingetragen sind). Andere Hooks werden ignoriert.

## Am Gerät

| Datei | Aufgabe |
|---|---|
| `device/clippy/agent_hooks/server.py` | Kleiner Webserver auf Port 4711 (`config.AGENT_PORT`), sobald das WLAN steht. Nimmt je Schleifendurchlauf höchstens eine Anfrage an, antwortet sofort `200`. `POST /<agent>` mit dem Hook-JSON; `GET /` zeigt „Clippy hört zu“ (zum Ausprobieren im Browser) |
| `device/clippy/agent_hooks/base.py` | Schnittstelle `Agent`: `name` (Anzeige), `short` (Kürzel im Kästchen, zwei Zeichen), Hook-Namen je Zustand, `state(payload)` liefert den Zustand oder `None` |
| `device/clippy/agent_hooks/claude.py`, `codex.py`, `copilot.py` | Je Agent eine Klasse; ändert nur, was bei ihm anders ist |
| `device/clippy/agent_hooks/__init__.py` | `AGENTS`: Pfad der Anfrage (`claude`, `codex`, `copilot`) → Klasse |
| `device/clippy/pet/agents.py` | Merkt sich je Agent den Zustand, meldet der Klammer `agent_working`, `agent_waiting`, `agent_done` |

Große Meldungen (z. B. wenn der Agent eine lange Datei schreibt): Clippy liest höchstens 32 KB als JSON; ist die
Meldung größer, sucht es die nötigen Felder (`hook_event_name`, `notification_type`) direkt im Text.

**Neuer Agent:** Datei in `agent_hooks/` mit einer Unterklasse von `Agent`, in `AGENTS` eintragen, in
`manual/verbinden.txt` die Einträge für den Agent ergänzen, Tabelle oben ergänzen.

## Die Einträge

`curl` schickt stdin (`--data-binary @-`) an Clippy, wartet höchstens 2 s (Copilot 1 s) und endet immer still
mit 0, auch wenn Clippy aus ist. Gemessen am PC: unbekannter Name nach 1,5 s, Clippy an ohne Webserver nach 2 s;
Weitergabe von stdin geprüft über `cmd.exe`, PowerShell direkt und PowerShell → `cmd.exe`.

- **Claude Code**, `~/.claude/settings.json`, je Hook `"async": true` (Claude wartet nicht). Windows:
  `{"type": "command", "command": "cmd.exe", "args": ["/c", "curl.exe -s -m 2 --data-binary @- http://clippy.local:4711/claude & exit /b 0"], "async": true}`.
  macOS/Linux: `{"type": "command", "command": "curl -s -m 2 --data-binary @- http://clippy.local:4711/claude || true", "async": true}`.
  Kein HTTP-Hook (`"type": "http"`): der meldet bei ausgeschaltetem Clippy jedes Mal einen Fehler im Chat.
  Nicht in die Projektdatei `.claude/settings.json`: Copilot liest die mit und würde sich als Claude melden.
- **Codex**, `~/.codex/config.toml`, `async = true`, Windows-Befehl in `command_windows`.
- **Copilot**, `~/.copilot/hooks/clippy.json` (Kommandozeile und VS Code), Felder `bash` und `powershell`,
  `timeoutSec`; kennt kein `async`.

Die vollständigen Einträge stehen in [manual/verbinden.txt](../manual/verbinden.txt).

## Quellen

- Claude Code: https://code.claude.com/docs/en/hooks.md
- Codex: https://learn.chatgpt.com/docs/hooks
- Copilot: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference,
  https://code.visualstudio.com/docs/copilot/customization/hooks
