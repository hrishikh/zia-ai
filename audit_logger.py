import os
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import asdict


class AuditLogger:
    """
    Log all Zia actions for transparency and debugging.
    """
    
    def __init__(self, log_dir: str = "~/.zia/logs"):
        self.log_dir = os.path.expanduser(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "activity.jsonl")
    
    def log_action(self, action, result):
        """Log an executed action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_id': action.action_id,
            'action_type': action.action_type,
            'params': action.params,
            'risk_level': action.risk_level.value,
            'success': result.success,
            'message': result.message,
            'error': result.error
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent activity logs"""
        if not os.path.exists(self.log_file):
            return []
        
        logs = []
        with open(self.log_file, 'r') as f:
            for line in f:
                logs.append(json.loads(line.strip()))
        
        return logs[-limit:]
    
    def export_logs(self, output_path: str):
        """Export logs to file"""
        logs = self.get_recent_logs(limit=10000)
        
        with open(output_path, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def purge_logs(self, before_date: datetime = None):
        """Delete old logs"""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        print("✅ Logs purged")
