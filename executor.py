import os
import subprocess
import time
import base64
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
from pathlib import Path

# Google & Selenium Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class ActionExecutor:
    def __init__(self, auth_manager, audit_logger):
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
        # Scope required for sending emails
        self.gmail_scopes = ['https://www.googleapis.com/auth/gmail.send']

    def _get_gmail_service(self):
        """
        Handles the Gmail OAuth2 flow. 
        If token.json is missing or invalid, it forces a browser popup using client_secret.json.
        """
        creds = None
        # Step 1: Try to load existing credentials from token.json
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.gmail_scopes)
        
        # Step 2: If credentials don't exist, are invalid, or lack refresh fields
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None # Force re-auth if refresh fails
            
            # Step 3: Trigger the browser popup if no valid credentials exist
            if not creds:
                if not os.path.exists('client_secret.json'):
                    raise FileNotFoundError("Missing 'client_secret.json' in D:\\Zia AI. Please download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', self.gmail_scopes)
                # This line opens your default browser
                creds = flow.run_local_server(port=0)
            
            # Step 4: Save the new credentials to token.json for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    # ========== GMAIL AUTOMATION ==========

    def compose_email(self, params: Dict) -> Dict:
        """Sends email via Gmail API with automatic authentication check"""
        try:
            service = self._get_gmail_service()
            
            recipient = params.get('recipient', 'hrishikh175@gmail.com')
            subject = params.get('subject', 'Zia Automated Message')
            body = params.get('body', 'Neural transmission from Zia AI.')
            
            message = MIMEText(body)
            message['to'] = recipient
            message['subject'] = subject
            
            # Encode the message for the Gmail API
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId='me', body={'raw': raw}).execute()
            
            return {'status': 'email_sent', 'to': recipient}
        except Exception as e:
            return {'error': str(e)}

    # ========== WEB & YOUTUBE (SELENIUM) ==========
    
    def play_youtube(self, params: Dict) -> Dict:
        """Takes direct control of Chrome to search and play YouTube"""
        query = params.get('query', '')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True) # Keeps browser open
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            time.sleep(3) # Wait for results to load
            first_video = driver.find_element(By.ID, "video-title")
            first_video.click()
            return {'status': 'youtube_playing', 'query': query}
        except Exception as e:
            return {'error': str(e)}

    # ========== VOICE & MESSAGING (TWILIO) ==========
    
    def make_call(self, params: Dict) -> Dict:
        """Outgoing call using the Voice-verified number (+1830...)"""
        from twilio.rest import Client
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        call = client.calls.create(
            twiml="<Response><Say voice='alice'>Hello, Zia here. Hrishik asked me to call.</Say></Response>",
            to=params['recipient'],
            from_=os.getenv('TWILIO_PHONE_NUMBER')
        )
        return {'call_sid': call.sid, 'status': 'dialing'}

    def send_message(self, params: Dict) -> Dict:
        """WhatsApp using the Sandbox Number (+1415...)"""
        from twilio.rest import Client
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        from_num = f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}"
        to_num = f"whatsapp:{params['recipient']}" if not params['recipient'].startswith('whatsapp:') else params['recipient']
        message = client.messages.create(body=params['content'], from_=from_num, to=to_num)
        return {'message_sid': message.sid, 'status': 'sent_whatsapp'}

    # ========== SYSTEM & FILES ==========

    def open_file(self, params: Dict) -> Dict: 
        os.startfile(params.get('path'))
        return {'status': 'opened', 'path': params.get('path')}