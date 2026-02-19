"""
Zia AI — Twilio Voice Executor
Make outgoing voice calls via Twilio.
"""

import os
from typing import Any, Dict, List

from twilio.rest import Client

from app.config import settings
from app.executors.base import BaseExecutor


class TwilioVoiceExecutor(BaseExecutor):
    def get_supported_actions(self) -> List[str]:
        return ["twilio.make_call"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        self.validate_params(action_type, params, ["recipient"])

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = params.get("message", "Hello, this is Zia AI calling on behalf of a user.")

        call = client.calls.create(
            twiml=f"<Response><Say voice='alice'>{message}</Say></Response>",
            to=params["recipient"],
            from_=settings.TWILIO_PHONE_NUMBER,
        )
        return {"status": "call_initiated", "call_sid": call.sid}
