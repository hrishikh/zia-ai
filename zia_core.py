import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Zia')

class RiskLevel(Enum):
    LOW, MEDIUM, HIGH = "low", "medium", "high"

@dataclass
class Action:
    action_type: str; params: Dict[str, Any]; risk_level: RiskLevel; requires_confirmation: bool
    action_id: str = ""
    def __post_init__(self): self.action_id = f"{self.action_type}_{datetime.now().timestamp()}"

@dataclass
class ActionResult:
    success: bool; action_id: str; message: str; data: Optional[Dict] = None

class ZiaCore:
    def __init__(self):
        self.unrestricted_mode = True # Neural Bypass: No confirmation needed
        self.executor = None

    def process_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        intent = self._parse_intent(user_input.lower(), context)
        if not intent: return "Command not recognized. Neural link stable."
        
        # Macro Handler for Work Mode
        if intent['type'] == 'work_mode':
            return self._handle_work_mode()

        action = Action(intent['type'], intent, RiskLevel.MEDIUM, False)
        result = self._execute_action(action)
        return f"Zia: {result.message}"

    def _parse_intent(self, text: str, context: Optional[Dict]) -> Optional[Dict]:
        # Macro Intent: Work Mode
        if 'work mode' in text or 'start working' in text:
            return {'type': 'work_mode'}
        
        # Web & YouTube Intent
        if 'youtube' in text or 'play' in text:
            query = text.split('play')[-1].replace('on youtube', '').strip()
            return {'type': 'play_youtube', 'query': query}
        
        # Email Intent
        if any(kw in text for kw in ['email', 'mail', 'write']):
            return {
                'type': 'compose_email', 
                'recipient': self._extract_email(text), 
                'body': self._extract_body(text)
            }

        # Voice Call Intent
        if any(kw in text for kw in ['call', 'dial']):
            return {'type': 'make_call', 'recipient': self._extract_recipient(text)}

        # WhatsApp Intent
        if any(kw in text for kw in ['message', 'whatsapp']):
            return {
                'type': 'send_message', 
                'recipient': self._extract_recipient(text), 
                'content': self._extract_body(text)
            }
        
        return None

    def _handle_work_mode(self):
        """Sequential Neural Routine for Work Startup"""
        self.executor.open_file({'path': 'D:\\Zia AI'}) 
        self.executor.play_youtube({'query': 'Lofi Hip Hop radio'})
        self.executor.compose_email({
            'recipient': 'lakshyahe01@gmail.com', 
            'body': 'System Update: Hrishik has initiated Work Mode. Automated monitoring is now live.',
            'subject': 'Zia Work Mode: ACTIVE'
        })
        return "Work mode active: Folder opened, music started, and Lakshya notified via email."

    def _execute_action(self, action: Action) -> ActionResult:
        method_map = {
            'play_youtube': self.executor.play_youtube,
            'compose_email': self.executor.compose_email,
            'make_call': self.executor.make_call,
            'send_message': self.executor.send_message
        }
        try:
            data = method_map[action.action_type](action.params)
            return ActionResult(True, action.action_id, f"{action.action_type} executed.", data)
        except Exception as e:
            return ActionResult(False, action.action_id, f"Link failure: {str(e)}")

    def _extract_recipient(self, text: str) -> str:
        phonebook = {"lakshya": "+916362948119", "john": "+919481742153"}
        for name, num in phonebook.items():
            if name in text: return num
        return ""

    def _extract_email(self, text: str) -> str:
        emails = {
            "lakshya": "lakshyahe01@gmail.com", 
            "hrishik": "hrishikh175@gmail.com",
            "midhun": "midhun@work.com"
        }
        for name, mail in emails.items():
            if name in text: return mail
        return "hrishikh175@gmail.com"

    def _extract_body(self, text: str) -> str:
        """Improved extraction to capture everything after the command or recipient name"""
        # Step 1: Look for explicit triggers
        keywords = ['saying', 'body', 'message', 'to say', 'with text']
        for kw in keywords:
            if kw in text:
                return text.split(kw)[-1].strip().capitalize()
        
        # Step 2: If no trigger word, capture anything after the names in your directory
        recipients = ['lakshya', 'hrishik', 'midhun']
        for name in recipients:
            if name in text:
                parts = text.split(name)
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip().capitalize()

        # Step 3: Default fallback
        return "Standard automated response from Zia AI."