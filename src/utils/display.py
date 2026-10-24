from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

console = Console()

def display_header():
    """Display a rich styled banner for the application"""
    console.print(Panel.fit(
        "[bold white]CRISIS LOGISTICS & FLEET SIMULATOR[/bold white]\n[cyan]Emergency Response & Relief Dispatch System[/cyan]",
        border_style="bold red"
    ))

def display_supplies_table(supplies_list):
    """Display supplies inventory inside a rich colored table"""
    if not supplies_list:
        console.print("[bold yellow]No supplies currently available in inventory.[/bold yellow]")
        return

    table = Table(title="Emergency Supplies Inventory", header_style="bold magenta")
    
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="bold white")
    table.add_column("Category", style="green")
    table.add_column("Quantity", justify="right")
    table.add_column("Unit Weight (kg)", justify="right")

    for item in supplies_list:
        qty = item.get("quantity", 0)
        qty_style = "bold green" if qty > 10 else "bold red"
        
        table.add_row(
            item.get("item_id", ""),
            item.get("name", ""),
            item.get("category", ""),
            f"[{qty_style}]{qty}[/{qty_style}]",
            str(item.get("unit_weight_kg", ""))
        )

    console.print(table)

def simulate_dispatch_progress(shipment_id):
    """Simulate a progress bar for shipment dispatch"""
    console.print(f"\n[bold yellow]Dispatching Shipment {shipment_id}...[/bold yellow]")
    for _ in track(range(10), description="[green]In Transit to Crisis Zone...[/green]"):
        time.sleep(0.2)
    console.print(f"[bold green]✅ Shipment {shipment_id} successfully delivered![/bold green]\n")