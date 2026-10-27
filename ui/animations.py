import time
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.box import ROUNDED, DOUBLE
from core.database import load_data
import questionary

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

console = Console()
_BOOTED = False

CYBERPUNK_STYLE = questionary.Style([
    ('qmark', 'fg:#00f3ff bold'),
    ('question', 'bold white'),
    ('answer', 'fg:#00ff66 bold'),
    ('pointer', 'fg:#00f3ff bold'),
    ('highlighted', 'fg:#00f3ff bold'),
    ('selected', 'fg:#00ff66 bold'),
    ('instruction', 'dim fg:#ffb700'),
])

def clear_screen():
    """Clear screen entirely and adjust cursor position to fix view and prevent buffer stacking"""
    os.system('cls' if os.name == 'nt' else 'clear')
    console.clear()

THEMES = {
    "Cyberpunk Neon": {"banner_style": "bold #00f3ff", "border_style": "#00f3ff", "accent": "bold #ffb700"},
    "Matrix Hacker": {"banner_style": "bold #00ff66", "border_style": "#00ff66", "accent": "bold #00ff66"},
    "Gold Luxury": {"banner_style": "bold #ffb700", "border_style": "#ffb700", "accent": "bold #ffb700"}
}

BANNER_TEXT = """
  ╔═════════════════════════════════════════════════════════════════════════════╗
  ║      █████╗   ██████╗ ███████╗███╗   ██╗████████╗ ██████╗  ███████╗         ║
  ║     ██╔══██╗ ██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗ ██╔════╝         ║
  ║     ███████║ ██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║   ██║ ███████╗         ║
  ║     ██╔══██║ ██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║ ╚╚══██║         ║
  ║     ██║  ██║ ╚██████╔╝███████╗██║ ╚████║   ██║   ╚██████╔╝ ███████║         ║
  ╚═════════════════════════════════════════════════════════════════════════════╝
"""

def get_current_theme_colors():
    data = load_data()
    theme_name = data.get("theme", "Cyberpunk Neon")
    return THEMES.get(theme_name, THEMES["Cyberpunk Neon"])

def display_banner(breadcrumb="Main Grid"):
    colors = get_current_theme_colors()
    b_style = colors["banner_style"]
    
    typography_art = (
        f"[{b_style}] █████╗   ██████╗ ███████╗███╗   ██╗████████╗ ██████╗  ███████╗\n"
        "██╔══██╗ ██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗ ██╔════╝\n"
        "███████║ ██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║   ██║ ███████╗\n"
        "██╔══██║ ██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║ ╚╚══██║\n"
        f"██║  ██║ ╚██████╔╝███████╗██║ ╚████║   ██║   ╚██████╔╝ ███████║[/{b_style}]"
    )
    
    console.print(Align.center(typography_art))
    console.print()

def cinematic_startup_sequence():
    global _BOOTED
    if _BOOTED:
        return
    _BOOTED = True

    clear_screen()
    display_banner("System Boot")
    
    console.print("\n[bold #00f3ff]✨ [AgentOS] NEURAL ORCHESTRATION ENGINE INITIALIZING...[/bold #00f3ff]")
    console.print("[dim]   [Please stand by while core systems and project branding load][/dim]\n")
    time.sleep(2.0)
    
    console.print("[bold #ffb700]⚡ BOOTING UP SYSTEM KERNEL v4.8...[/bold #ffb700]\n")
    time.sleep(1.0)
    
    steps = [
        ("[dim]>> [01/04] Initializing Quantum Neural Core & Memory Grids...[/dim]", 0.6),
        ("[bold #00f3ff]>> [02/04] Establishing secure quantum handshake with AI cluster nodes...[/bold #00f3ff]", 0.7),
        ("[bold #00f3ff]>> [03/04] Calibrating token encryption & decryption matrices...[/bold #00f3ff]", 0.7),
        ("[bold #00ff66]>> [04/04] Synchronizing decentralized node memory banks...[/bold #00ff66]", 0.8)
    ]
    
    for text, delay in steps:
        console.print(text)
        time.sleep(delay)
        
    with Progress(
        SpinnerColumn("dots", style="bold #00f3ff"),
        TextColumn("[bold #00f3ff]{task.description}[/bold #00f3ff]"),
        BarColumn(bar_width=40, style="dim #00f3ff", complete_style="bold #00ff66"),
        TextColumn("[bold #ffb700]{task.percentage:>3.0f}%[/bold #ffb700]"),
        console=console
    ) as progress:
        task = progress.add_task("Stabilizing Quantum Fields", total=100)
        while not progress.finished:
            progress.update(task, advance=25)
            time.sleep(0.3)
            
    console.print("\n[bold #00ff66]✔ SUCCESS: AgentOS online and fully operational. Welcome, Operator.[/bold #00ff66]\n")
    time.sleep(1.5)

def show_loading_spinner(message="Processing Neural Bridge..."):
    with Progress(
        SpinnerColumn("dots", style="bold #00f3ff"),
        TextColumn("[bold #00f3ff]{task.description}[/bold #00f3ff]"),
        BarColumn(bar_width=40, style="dim #00f3ff", complete_style="bold #00ff66"),
        console=console
    ) as progress:
        task = progress.add_task(message, total=100)
        while not progress.finished:
            progress.update(task, advance=25)
            time.sleep(0.12)

def show_deployment_animation(agent_name):
    console.print(f"\n[bold #ffb700]🚀 Initiating deployment sequence for {agent_name}...[/bold #ffb700]")
    show_loading_spinner(f"Allocating GPU Tokens for {agent_name}")
    show_loading_spinner(f"Syncing REST Endpoint")
    console.print(f"[bold #00ff66]✔ {agent_name} deployed successfully to cluster![/bold #00ff66]\n")

def smooth_menu_transition(section_name):
    clear_screen()
    display_banner(section_name)
    console.print(f"\n[bold #00f3ff]⚡ Loading [bold #ffb700]{section_name}[/bold #ffb700]...[/bold #00f3ff]")
    
    with Progress(
        SpinnerColumn("dots", style="bold #00f3ff"),
        TextColumn("[bold #00f3ff]{task.description}[/bold #00f3ff]"),
        BarColumn(bar_width=35, style="dim #00f3ff", complete_style="bold #00ff66"),
        console=console,
        transient=False
    ) as progress:
        task = progress.add_task(f"Synchronizing {section_name}", total=100)
        while not progress.finished:
            progress.update(task, advance=34)
            time.sleep(0.15)
            
    console.print(f"[bold #00ff66]>> [{section_name}] Initialized successfully.[/bold #00ff66]")
    time.sleep(0.5)
    console.print("─" * 80, style="dim")

def cinematic_exit():
    clear_screen()
    display_banner("System Shutdown")
    
    warning_panel = Panel(
        "[bold #ffb700]WARNING:[/bold #ffb700] Initiating emergency quantum core shutdown & local storage data encryption...\n"
        "[dim]Disconnecting neural nodes, flushing memory buffers, and securing local state.[/dim]",
        title="[bold #ffb700][AgentOS] // CRITICAL SHUTDOWN PROTOCOL[/bold #ffb700]",
        border_style="#ffb700",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(warning_panel)
    time.sleep(1.0)
    
    console.print()
    
    with Progress(
        SpinnerColumn("dots", style="#00f3ff"),
        TextColumn("[bold #00f3ff]{task.description}[/bold #00f3ff]"),
        BarColumn(bar_width=40, style="dim #00f3ff", complete_style="bold #00ff66"),
        TextColumn("[bold #ffb700]{task.percentage:>3.0f}%[/bold #ffb700]"),
        console=console
    ) as progress:
        task1 = progress.add_task("Cooling down Quantum Cores...", total=100)
        while not progress.finished:
            progress.update(task1, advance=25)
            time.sleep(0.2)
            
    time.sleep(0.3)
    
    with Progress(
        SpinnerColumn("dots", style="#00f3ff"),
        TextColumn("[bold #00f3ff]{task.description}[/bold #00f3ff]"),
        BarColumn(bar_width=40, style="dim #00f3ff", complete_style="bold #00ff66"),
        TextColumn("[bold #ffb700]{task.percentage:>3.0f}%[/bold #ffb700]"),
        console=console
    ) as progress:
        task2 = progress.add_task("Encrypting local storage (data_store.json)...", total=100)
        while not progress.finished:
            progress.update(task2, advance=34)
            time.sleep(0.25)
            
    time.sleep(0.4)
    
    success_msg = "[🚀] SYSTEM OFFLINE. ALL NODES SECURED.\nHave a great day, Operator! See you at the top. ✨"
    success_panel = Panel(
        f"[bold #00ff66]{success_msg}[/bold #00ff66]",
        title="[bold #00ff66][AgentOS] // OFFLINE[/bold #00ff66]",
        border_style="#00ff66",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(success_panel)
    time.sleep(0.8)

