import os
import json
from datetime import datetime
from colorama import Fore

LOG_FILE = "security_log.json"

def log_activity(action_name):
  
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"[{timestamp}] {action_name}"
    
    logs = []
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
    logs.append(log_entry)
    
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(Fore.RED + f"❌ Error saving activity log: {e}")

def show_activity_log():
   
    print(Fore.CYAN + "\n" + "="*40)
    print(Fore.CYAN + "         SECURITY ACTIVITY LOG         ")
    print(Fore.CYAN + "="*40)
    
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        print(Fore.YELLOW + "📭 No security activity logged yet.")
        print(Fore.CYAN + "="*40)
        return
        
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        for entry in logs:
            print(Fore.WHITE + entry)
    except Exception:
        print(Fore.RED + "❌ Error reading activity log.")
    print(Fore.CYAN + "="*40)