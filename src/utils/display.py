from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def display_header():
    title = "[bold red]🚨 CRISIS MANAGEMENT & LOGISTICS SIMULATOR 🚨[/bold red]"
    subtitle = "[cyan]Secure Emergency Response & Fleet Dispatch Command Center[/cyan]"
    panel = Panel(
        Align.center(f"{title}\n{subtitle}"),
        border_style="bright_blue",
        padding=(1, 2)
    )
    console.print(panel)

def display_supplies_table(supplies):
    table = Table(
        title="📦 Emergency Supplies Inventory", 
        title_style="bold magenta", 
        border_style="cyan",
        header_style="bold bright_cyan"
    )
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="white")
    table.add_column("Category", style="green")
    table.add_column("Quantity", style="yellow", justify="right")
    table.add_column("Unit Weight (kg)", style="blue", justify="right")

    for item in supplies:
        # قراءة آمنة لجميع الاحتمالات والمفاتيح
        item_id = str(item.get("id") or item.get("item_id") or "N/A")
        name = str(item.get("name") or "Unknown")
        category = str(item.get("category") or "General")
        qty = str(item.get("quantity") or 0)
        weight = str(item.get("unit_weight") or item.get("unit_weight_kg") or 0.0)

        # تلوين الكميات المنخفضة لتحذير المستخدم بوجود نقص
        try:
            qty_int = int(qty)
            qty_str = f"[red]{qty_int} (Low)[/red]" if qty_int < 10 else f"[green]{qty_int}[/green]"
        except ValueError:
            qty_str = qty

        table.add_row(item_id, name, category, qty_str, weight)
        
    console.print(table)

def simulate_dispatch_progress(shipment_id):
    console.print(f"\n[bold yellow]🚚 Initializing dispatch protocols for shipment {shipment_id}...[/bold yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        t1 = progress.add_task("[cyan]Verifying transport route safety...", total=100)
        t2 = progress.add_task("[green]Loading cargo onto assigned vehicle...", total=100)
        t3 = progress.add_task("[magenta]Dispatched successfully to destination zone...", total=100)

        while not progress.finished:
            progress.update(t1, advance=15)
            time.sleep(0.15)
            if progress.tasks[0].completed >= 100:
                progress.update(t2, advance=20)
            if progress.tasks[1].completed >= 100:
                progress.update(t3, advance=25)
            time.sleep(0.1)

    console.print(f"[bold green]✨ Shipment {shipment_id} is successfully on the move and tracked by command![/bold green]\n")