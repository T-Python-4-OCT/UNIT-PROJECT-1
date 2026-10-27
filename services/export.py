import csv
from datetime import datetime
from core.database import load_data
from rich.console import Console
from rich.panel import Panel
from rich.box import HEAVY

console = Console()

def export_data_to_csv():
    """Export purchase history and system data to report.csv with Settings & System Configuration industrial control theme."""
    data = load_data()
    history = data.get("history", [])
    agents = data.get("agents", [])
    
    filename = "report.csv"
    
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            
            writer.writerow(["=== [AgentOS] EXPORT REPORT ==="])
            writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["Total Tokens Remaining", data.get("tokens", 0)])
            writer.writerow([])
            
            writer.writerow(["--- TRANSACTION & DEPLOYMENT HISTORY ---"])
            writer.writerow(["Transaction #", "Agent ID", "Agent Name", "Buyer Name", "Specialty", "Purchase Time", "Price (TC)"])
            
            if history:
                for idx, item in enumerate(history, 1):
                    writer.writerow([
                        idx,
                        item.get("id", "N/A"),
                        item.get("name", "N/A"),
                        item.get("buyer", "Authorized Developer"),
                        item.get("specialty", "N/A"),
                        item.get("timestamp", "N/A"),
                        item.get("price", 0)
                    ])
            else:
                writer.writerow(["No transactions recorded yet", "", "", "", "", "", ""])
                
            writer.writerow([])
            
            writer.writerow(["--- LIVE AGENTS INVENTORY ---"])
            writer.writerow(["Agent ID", "Agent Name", "Specialty", "Success Rate (%)", "Price (TC)", "Stock"])
            
            for agent in agents:
                writer.writerow([
                    agent.get("id"),
                    agent.get("name"),
                    agent.get("specialty"),
                    agent.get("success_rate"),
                    agent.get("price"),
                    agent.get("stock", 10)
                ])
                
        console.print(Panel(
            f"[bold #ffb700]⚙️ CONFIG BLOCK: CSV EXPORT SECURED │ 🟢 REPORT SAVED TO '{filename}'[/bold #ffb700]\n"
            "[dim]Industrial control panel telemetry exported successfully for Excel or external data viewers.[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION EXPORT[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        ))
        return True
    except Exception as e:
        console.print(Panel(
            f"[bold red]❌ Failed to export CSV report: {e}[/bold red]",
            title="[bold red]Export Failed[/bold red]",
            border_style="red",
            box=HEAVY,
            expand=False
        ))
        return False
