# Alle bekannten Coding-Agents: Pfad der Anfrage (http://clippy.local:4711/<pfad>) -> Klasse.
from clippy.agent_hooks.claude import Claude
from clippy.agent_hooks.codex import Codex
from clippy.agent_hooks.copilot import Copilot

AGENTS = {"claude": Claude, "codex": Codex, "copilot": Copilot}
