# Claude Code: Hooks siehe https://code.claude.com/docs/en/hooks.md
from clippy.agent_hooks.base import Agent

_hooks = dict(Agent.hooks)
_hooks["done"] = ("stop", "stopfailure")  # StopFailure: Antwort wegen eines API-Fehlers beendet


class Claude(Agent):
    name = "Claude"
    short = "Cl"
    hooks = _hooks
    waiting_notifications = ("permission_prompt", "agent_needs_input")
