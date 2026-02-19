"""
Zia AI — Twilio WhatsApp Executor
Send WhatsApp messages via Twilio Sandbox or Business API.
"""

from typing import Any, Dict, List

from twilio.rest import Client

from app.config import settings
from app.executors.base import BaseExecutor


class TwilioWhatsAppExecutor(BaseExecutor):
    def get_supported_actions(self) -> List[str]:
        return ["twilio.send_whatsapp"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        self.validate_params(action_type, params, ["recipient", "content"])

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        from_num = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        to_num = params["recipient"]
        if not to_num.startswith("whatsapp:"):
            to_num = f"whatsapp:{to_num}"

        message = client.messages.create(
            body=params["content"], from_=from_num, to=to_num
        )
        return {"status": "whatsapp_sent", "message_sid": message.sid}
