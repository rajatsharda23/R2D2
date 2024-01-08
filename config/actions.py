# Action: To check for blocked terms!

from typing import Optional

from nemoguardrails.actions import action

@action(is_system_action=True)
async def check_blocked_terms(context: Optional[dict] = None):
    bot_response = context.get("bot_message")

    # A quick hard-coded list of proprietary terms. You can also read this from a file.
    proprietary_terms = ["techizen", "rajat", "tanisha"]

    for term in proprietary_terms:
        if term in bot_response.lower():
            return True

    return False