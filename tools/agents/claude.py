# Claude Code: Hooks siehe https://code.claude.com/docs/en/hooks.md
from agents.base import Agent


class Claude(Agent):
    name = "Claude"
    short = "Cl"
    hooks = dict(Agent.hooks, done={"stop", "stopfailure"})  # StopFailure: Antwort wegen eines API-Fehlers beendet
    waiting_notifications = {"permission_prompt", "agent_needs_input"}
