# Alle bekannten Coding-Agents: Name auf der Befehlszeile von agent_hook.py -> Klasse.
from agents.claude import Claude
from agents.codex import Codex
from agents.copilot import Copilot

AGENTS = {"claude": Claude, "codex": Codex, "copilot": Copilot}
