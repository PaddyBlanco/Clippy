# Codex: Hooks siehe https://learn.chatgpt.com/docs/hooks
from agents.base import Agent


class Codex(Agent):
    name = "Codex"
    short = "Cx"
    hooks = dict(Agent.hooks, done={"stop", "interrupt"})  # Interrupt: du hast die Antwort abgebrochen
