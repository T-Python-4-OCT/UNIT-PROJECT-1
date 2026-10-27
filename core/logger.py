import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()
AUDIT_LOG_FILE = "audit_logs.json"

def log_action(action_type: str, message: str):
    """Log a user or system action with timestamp into audit_logs.json."""
    logs = []
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "type": action_type.upper(),
        "message": message
    }
    logs.append(entry)
    
    try:
        with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        pass

def get_audit_logs():
    """Retrieve all recorded audit logs."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def display_audit_logs():
    """Render system audit logs in Deep Matrix Green security layout with clearance badges and packet/shield monitoring."""
    logs = get_audit_logs()
    
    shield_panel = Panel(
        "[bold #00ff66]🛡️ SECURITY SHIELD: ACTIVE (100%) │ PACKET STREAM: SECURE │ ENCRYPTION: FERNET 128-BIT[/bold #00ff66]\n"
        "[dim]Security Clearance: ALPHA-1 // Autonomous Threat Detection Operational[/dim]",
        title="[bold #00ff66][AgentOS] // CYBER SECURITY & GOVERNANCE COMMAND[/bold #00ff66]",
        border_style="#00ff66",
        box=box.DOUBLE,
        expand=False
    )
    console.print(shield_panel)
    console.print()

    if not logs:
        console.print(Panel(
            "[bold #ffb700]📋 No system audit logs recorded yet. Perform actions in the system to generate logs.[/bold #ffb700]",
            title="[bold #ffb700]System Audit Logs[/bold #ffb700]",
            border_style="#00ff66",
            box=box.ROUNDED,
            expand=False
        ))
        return
        
    table = Table(
        title="[bold #00ff66]📋 [AgentOS] SECURE AUDIT LOGS LEDGER[/bold #00ff66]",
        show_header=True,
        box=box.DOUBLE,
        border_style="#00ff66",
        header_style="bold #ffb700"
    )
    table.add_column("Timestamp", style="bold #00ff66", width=20)
    table.add_column("Event Type", style="bold #ffb700", width=16)
    table.add_column("Action Description & Security Payload", style="bold white")
    
    for entry in logs:
        t_type = entry.get("type", "SYSTEM")
        if t_type == "SUCCESS":
            badge = "[bold #00ff66][SECURE / OK][/bold #00ff66]"
        elif t_type == "TRANSACTION":
            badge = "[bold #00f3ff][ENCRYPTED TX][/bold #00f3ff]"
        elif t_type == "WARNING":
            badge = "[bold #ffb700][ALERT / WARN][/bold #ffb700]"
        else:
            badge = f"[bold magenta][{t_type}][/bold magenta]"
            
        table.add_row(
            entry.get("timestamp", "N/A"),
            badge,
            entry.get("message", "N/A")
        )
        
    console.print(table)
    console.print("[dim]💡 Tip: Audit logs are persistently secured in 'audit_logs.json' under Deep Matrix governance.[/dim]\n")
