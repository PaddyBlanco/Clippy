# GitHub Copilot (Kommandozeile und VS Code): Hooks siehe
# https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference
# Nur in VS-Code-Schreibweise eingetragene Hooks (Stop, PostToolUse, ...) bringen hook_event_name mit.
from clippy.agent_hooks.base import Agent


class Copilot(Agent):
    name = "Copilot"
    short = "Co"
    color = 0x8957E5  # Copilot-Lila
    waiting_notifications = ("permission_prompt",)
