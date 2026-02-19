import os
import json
import keyring
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from dataclasses import dataclass

@dataclass
class AuthToken:
    service: str
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    scopes: List[str]

class AuthorizationManager:
    """
    Manages OAuth2 tokens and permissions for Zia.
    """
    SERVICE_NAME = "Zia-Assistant"
    
    def __init__(self, config_dir: str = "~/.zia"):
        self.config_dir = os.path.expanduser(config_dir)
        os.makedirs(self.config_dir, exist_ok=True)
        self.tokens_file = os.path.join(self.config_dir, "tokens.json")
        self.permissions_file = os.path.join(self.config_dir, "permissions.json")
        self.bypass_mode = False  # Set by main.py for Neural Agent mode

    def force_authorize(self, service: str):
        """NEURAL BYPASS: Forcefully marks a service as authorized"""
        permissions = self._load_permissions()
        permissions[service] = {
            'scopes': ['full_access'],
            'authorized_at': datetime.now().isoformat(),
            'neural_bypass': True
        }
        self._save_permissions(permissions)
        print(f"🔓 Neural Link established for: {service}")

    def is_authorized(self, service: str, scope: str = None) -> bool:
        """Checks if a service is authorized, bypassing if mode is enabled"""
        if self.bypass_mode:
            return True
        permissions = self._load_permissions()
        return service in permissions

    def authorize_service(self, service: str, scopes: List[str]) -> bool:
        oauth_configs = {
            'gmail': {
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': os.getenv('GMAIL_CLIENT_ID'),
                'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
                'redirect_uri': 'http://localhost:8080/callback'
            },
            'spotify': {
                'auth_uri': 'https://accounts.spotify.com/authorize',
                'token_uri': 'https://accounts.spotify.com/api/token',
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
                'redirect_uri': 'http://localhost:8888/callback'
            }
        }
        
        if service not in oauth_configs:
            return False
        
        config = oauth_configs[service]
        auth_url = self._build_auth_url(config, scopes)
        print(f"\n🔐 Authorization Required for {service}\nURL: {auth_url}\n")
        auth_code = input("Enter authorization code: ")
        
        tokens = self._exchange_code_for_tokens(config, auth_code, scopes)
        if tokens:
            self._store_tokens(service, tokens, scopes)
            return True
        return False

    def get_access_token(self, service: str) -> Optional[str]:
        if self.bypass_mode and service not in ['gmail', 'spotify']:
            return "bypass_token"
        token_data = self._load_token_data(service)
        if not token_data: return None
        return token_data['access_token']

    def _load_permissions(self) -> Dict:
        if os.path.exists(self.permissions_file):
            with open(self.permissions_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_permissions(self, permissions: Dict):
        with open(self.permissions_file, 'w') as f:
            json.dump(permissions, f, indent=2)

    def _build_auth_url(self, config: Dict, scopes: List[str]) -> str:
        import urllib.parse
        params = {
            'client_id': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'access_type': 'offline',
            'prompt': 'consent'
        }
        return f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"

    def _exchange_code_for_tokens(self, config: Dict, code: str, scopes: List[str]) -> Optional[Dict]:
        try:
            response = requests.post(config['token_uri'], data={
                'code': code,
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'redirect_uri': config['redirect_uri'],
                'grant_type': 'authorization_code'
            })
            if response.status_code == 200: return response.json()
        except Exception as e:
            print(f"Token exchange failed: {str(e)}")
        return None

    def _store_tokens(self, service: str, tokens: Dict, scopes: List[str]):
        keyring.set_password(self.SERVICE_NAME, f"{service}_access_token", tokens['access_token'])
        expires_at = datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
        token_data = {'expires_at': expires_at.isoformat(), 'scopes': scopes}
        
        all_tokens = {}
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f: all_tokens = json.load(f)
        all_tokens[service] = token_data
        with open(self.tokens_file, 'w') as f: json.dump(all_tokens, f, indent=2)
        
        permissions = self._load_permissions()
        permissions[service] = {'scopes': scopes, 'authorized_at': datetime.now().isoformat()}
        self._save_permissions(permissions)

    def _load_token_data(self, service: str) -> Optional[Dict]:
        if not os.path.exists(self.tokens_file): return None
        with open(self.tokens_file, 'r') as f: all_tokens = json.load(f)
        if service not in all_tokens: return None
        token_data = all_tokens[service]
        token_data['access_token'] = keyring.get_password(self.SERVICE_NAME, f"{service}_access_token")
        return token_data