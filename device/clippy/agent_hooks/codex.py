# Codex: Hooks siehe https://learn.chatgpt.com/docs/hooks
from clippy.agent_hooks.base import Agent

_hooks = dict(Agent.hooks)
_hooks["done"] = ("stop", "interrupt")  # Interrupt: du hast die Antwort abgebrochen


class Codex(Agent):
    name = "Codex"
    short = "Cx"
    color = 0x10A37F  # OpenAI-Grün
    hooks = _hooks
