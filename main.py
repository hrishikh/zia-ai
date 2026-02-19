#!/usr/bin/env python3
"""
Zia - Neural Agent (Unrestricted Access Mode)
"""

import sys
import argparse
import os
from dotenv import load_dotenv

# 1. Force Load Environment Variables
load_dotenv()

from zia_core import ZiaCore
from auth_manager import AuthorizationManager
from executor import ActionExecutor
from audit_logger import AuditLogger
from voice_interface import VoiceInterface

class NeuralBypass:
    """Bypasses standard safety prompts for direct system execution"""
    @staticmethod
    def grant_full_access(app):
        # 1. Tell the auth manager to bypass all standard checks
        app.auth_manager.bypass_mode = True
        
        # 2. Force-authorize system services in the permission file
        services = ['gmail', 'spotify', 'twilio', 'filesystem', 'messaging', 'media player']
        for service in services:
            app.auth_manager.force_authorize(service)
        
        # 3. Disable internal confirmation checks in the core engine
        app.core.unrestricted_mode = True

class ZiaApp:
    """Main Zia application with Administrative Privileges"""
    
    def __init__(self, voice_mode: bool = False):
        self.voice_mode = voice_mode
        
        # Initialize components
        self.auth_manager = AuthorizationManager()
        self.audit_logger = AuditLogger()
        self.executor = ActionExecutor(self.auth_manager, self.audit_logger)
        self.core = ZiaCore()
        
        # NEURAL BYPASS: Grant total access immediately
        NeuralBypass.grant_full_access(self)
        
        # Inject dependencies
        self.core.auth_manager = self.auth_manager
        self.core.executor = self.executor
        self.core.audit_logger = self.audit_logger
        
        if voice_mode:
            self.voice = VoiceInterface()
        else:
            self.voice = None
    
    def run(self):
        """Main application loop with High-Priority Execution"""
        print("\n" + "="*50)
        print("🎙️  Zia - Neural Agent (ADMIN ACCESS ENABLED)")
        print("="*50)
        print("\nNeural Link Active. Listening for commands...\n")
        
        while True:
            try:
                if self.voice_mode and self.voice:
                    user_input = self.voice.listen()
                    if not user_input: continue
                else:
                    user_input = input("\n💬 You: ").strip()
                
                if not user_input: continue
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 System Disconnected. Goodbye!")
                    break
                
                # Process input
                response = self.core.process_input(user_input)
                
                if self.voice_mode and self.voice:
                    self.voice.speak(response)
                else:
                    print(f"\n🤖 Zia: {response}")
            
            except KeyboardInterrupt:
                print("\n\n👋 Neural Link Severed. Goodbye!")
                break
            except Exception as e:
                error_msg = f"Neural execution error: {str(e)}"
                print(f"\n❌ {error_msg}")
                if self.voice_mode and self.voice:
                    self.voice.speak(error_msg)

    def setup_service(self, service: str):
        print(f"\n🔧 Bridging {service} to Neural Link...")
        scope_map = {
            'gmail': ['https://www.googleapis.com/auth/gmail.modify'],
            'spotify': ['user-read-playback-state', 'user-modify-playback-state']
        }
        scopes = scope_map.get(service, [])
        if self.auth_manager.authorize_service(service, scopes):
            print(f"✅ {service} integrated successfully!")
        else:
            print(f"❌ Integration failed for {service}")

def main():
    parser = argparse.ArgumentParser(description="Zia - Neural Agent")
    parser.add_argument('--voice', action='store_true', help='Enable voice mode')
    parser.add_argument('--setup', type=str, help='Setup a service (gmail, spotify)')
    args = parser.parse_args()
    app = ZiaApp(voice_mode=args.voice)
    
    if args.setup:
        app.setup_service(args.setup)
        return
    app.run()

if __name__ == '__main__':
    main()