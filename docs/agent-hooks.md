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
| `working` | Agent arbeitet (Anfrage bekommen, Werkzeug benutzt) | merkt auf; solange gearbeitet wird, schaut sie gespannt zur Seite und über ihrem Kopf dreht sich ein Arbeitswort wie in Claude Code, in einem kleinen alten Eingabefenster („C:\>Percolating_“, siehe [pet.md](pet.md)); keine Sprechblasen, solange gearbeitet wird | gelb |
| `waiting` | Agent wartet auf eine Freigabe oder Antwort | hüpft, winkt, ruft; nach 30 und 60 s noch einmal, also höchstens dreimal (`CALLS`), und nicht mehr, sobald ein neuer Zustand kommt oder du sie antippst | rot, bleibt bis zum nächsten Zustand |
| `done` | Agent ist mit seiner Antwort fertig | freut sich und sagt es | grün |
| `gone` | Sitzung beendet | – | verschwindet |

Kommt 30 Minuten lang nichts von einem Agent, verschwindet sein Kästchen ebenfalls. Mehrere Sitzungen desselben
Agents teilen sich ein Kästchen; die letzte Meldung gilt.

## Nutzung und Limits (nur Claude Code)

Zwei Quellen, weil die VS-Code-Erweiterung keine Statuszeile ausführt (am PC geprüft: Hooks aus derselben Sitzung
kamen an, die Statuszeile nie):

**1. `claude -p /usage` (VS Code und Terminal).** Ein zweiter Hook bei `Stop` fragt Clippy
(`GET /claude/usage`), ob es neue Zahlen braucht: Antwort `bitte`, wenn die letzten älter als 3 Minuten sind
(`USAGE_MS` in `pet/agents.py`), sonst `danke`. Bei `bitte` startet der Hook das laufende Claude Code noch einmal im
Druckmodus und schickt dessen Ausgabe an `POST /claude/usage`. Den Pfad zum Programm liefert die Umgebungsvariable
`CLAUDE_PID`, die Claude Code jedem Hook mitgibt (auch in VS Code, wo `claude` nicht im Suchpfad liegt):
`(Get-Process -Id $env:CLAUDE_PID).Path -p /usage --no-session-persistence --setting-sources project`.
`--setting-sources project` lädt die Benutzereinstellungen nicht, also auch nicht die Clippy-Hooks (sonst ruft sich
das im Kreis); `--no-session-persistence` legt keine Sitzung an. Dauer am PC: 2,4 s für `/usage`, knapp 6 s für den
ganzen Hook über PowerShell, im Hintergrund (`async`); am PC so aufgerufen wie Claude Code es tut (Liste von
Argumenten, ohne Shell) und am Gerät angekommen. Die Variante für macOS/Linux in `manual/verbinden.txt` ist
ungetestet. Die genauen Einträge stehen dort.
Die Ausgabe ist Text, ausgewertet von `Claude.usage_text`:
`Current session: 9% used · resets Nov 16, 11:49pm (Europe/Vienna)` (5-Stunden-Fenster) und
`Current week (all models): 8% used · resets Nov 21, 9:59pm (Europe/Vienna)`. Clippy zeigt die Zeit als
`bis 23:49` (heute) bzw. `bis 21.11. 21:59`. So holt Claude Code die Zahlen selbst (intern über
`/api/oauth/usage`, steht in seinem Protokoll); Clippy fasst kein Anmelde-Token an.

**2. Statuszeile (nur Terminal).** Claude Code ruft seine **Statuszeile** bei jeder Antwort auf und gibt ihr ein JSON mit, unter anderem
`rate_limits.five_hour` und `rate_limits.seven_day` (`used_percentage`, `resets_at` in Unix-Sekunden; nur bei
Pro/Max und erst nach der ersten Antwort), `context_window.used_percentage`, `cost.total_cost_usd`,
`cost.total_lines_added`/`removed`, `model.display_name`, `workspace.project_dir`
(https://code.claude.com/docs/en/statusline.md). Die Statuszeile ist ein einzelner Befehl:

- Windows (läuft in Git Bash oder PowerShell, `'@-'` in Anführungszeichen für PowerShell):
  `"statusLine": {"type": "command", "command": "curl.exe -s -m 1 --data-binary '@-' http://clippy.local:4711/claude/status"}`
- macOS/Linux: `"command": "curl -s -m 1 --data-binary @- http://clippy.local:4711/claude/status"`

Clippy merkt sich die Werte und **antwortet mit der Zeile**, die Claude Code unten anzeigt, z. B.
`Clippy · 5h 42% · Woche 18% · Kontext 31%`. Ist Clippy aus, bleibt die Zeile leer. Hat jemand schon eine eigene
Statuszeile, ersetzt der Agent sie nur nach Rückfrage.

Am Gerät: Symbol **„Nutzung“** am Desktop öffnet ein Fenster links (die Klammer bleibt rechts sichtbar und lebt
weiter), siehe [architecture.md](architecture.md). Erreicht das 5-Stunden-Limit 80 %, meldet die Klammer
`usage_high` (einmal je Zeitfenster). Codex hat seine Limits nur in internen Dateien am PC, Copilot gar nicht;
ohne Programm am PC kommt Clippy da nicht ran, daher nur Claude.

Auswertung: `Agent.usage(payload)` (Statuszeile) und `Agent.usage_text(text)` (Ausgabe von `/usage`) in
`agent_hooks/` (Claude füllt sie, die anderen liefern `None`), zusammengeführt in `pet/agents.py`: was die neue
Meldung nicht hat (z. B. Kontext bei `/usage`), bleibt vom letzten Mal. Antworttext von `agent_hooks/usage.py`.
`GET /claude/status` zeigt zum Nachsehen, was zuletzt ankam; `GET /` zeigt, welcher Agent sich zuletzt gemeldet hat.

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
| `device/clippy/agent_hooks/server.py` | Kleiner Webserver auf Port 4711 (`config.AGENT_PORT`), sobald das WLAN steht. Nimmt je Schleifendurchlauf höchstens eine Anfrage an, antwortet sofort `200`. `POST /<agent>` mit dem Hook-JSON, `POST /<agent>/status` mit dem Statuszeilen-JSON (Antwort: die Statuszeile), `GET /<agent>/probe` spielt „fertig“; `GET /` zeigt „Clippy hört zu“ |
| `device/clippy/agent_hooks/usage.py` | Statuszeilen-Text aus den gemerkten Werten, Prozent-Schwelle für die Warnung |
| `device/clippy/agent_hooks/base.py` | Schnittstelle `Agent`: `name` (Anzeige), `short` (Kürzel im Kästchen, zwei Zeichen), `color` (Farbe des Arbeitsworts), Hook-Namen je Zustand, `state(payload)` liefert den Zustand oder `None` |
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
