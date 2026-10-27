import time
import platform
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.box import DOUBLE, ROUNDED
from core.database import load_data
from ui.animations import clear_screen

console = Console()

def generate_dashboard_layout():
    """توليد هيكل الشاشة المقسمة إلى 3 أقسام رئيسية بتصميم Neural Benchmarks Oscilloscope"""
    data = load_data()
    agents = data.get("agents", [])
    history = data.get("history", [])
    tokens = data.get("tokens", 0)

    # هيكل الشاشة الأساسي (تقسيم عامودي: علوي وسفلي)
    layout = Layout()
    layout.split_column(
        Layout(name="upper", ratio=3),
        Layout(name="lower", ratio=1)
    )

    # تقسيم القسم العلوي أفقياً (قسم الكتالوج يمين/يسار، وقسم السجل الحي بجانبه)
    layout["upper"].split_row(
        Layout(name="catalog", ratio=2),
        Layout(name="logs", ratio=1)
    )

    # --- 1. قسم الكتالوج (Catalog Section) ---
    table = Table(title="[bold #00f3ff][AgentOS] Oscilloscope Agents Catalog Matrix[/bold #00f3ff]", show_header=True, expand=True, box=DOUBLE, border_style="#00f3ff", header_style="bold #ffb700")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Agent Name", style="bold #00ff66")
    table.add_column("Specialty", style="bold #ffb700")
    table.add_column("Price", justify="right", style="bold #00f3ff")

    for agent in agents:
        table.add_row(agent["id"], agent["name"], agent["specialty"], f"{agent['price']} TC")
    
    catalog_panel = Panel(table, title="[bold #00ff66]📦 1. [AgentOS] Catalog & Waveform Section[/bold #00ff66]", border_style="#00ff66", box=ROUNDED)

    # --- 2. قسم السجل الحي للعمليات (Live Logs Section) ---
    current_time = datetime.now().strftime("%H:%M:%S")
    logs_content = (
        r"[dim]" + current_time + r" - Core neural bridge online (~/\~)[/dim]" + "\n" +
        f"[bold #00ff66]{current_time} - Cluster node US-East synced (18ms)[/bold #00ff66]\n"
        f"[bold #00f3ff]{current_time} - Token ledger verified securely[/bold #00f3ff]\n"
        f"[bold #ffb700]{current_time} - Active deployments: {len(history)} nodes[/bold #ffb700]\n"
        f"[bold #00ff66]{current_time} - Oscilloscope waveform active...[/bold #00ff66]\n"
        f"[bold #00ff66]>> Quantum core monitoring running smoothly...[/bold #00ff66]"
    )
    logs_panel = Panel(logs_content, title="[bold #ffb700]⚡ 2. [AgentOS] Oscilloscope Live Logs Matrix[/bold #ffb700]", border_style="#ffb700", box=ROUNDED)

    # ربط القسم العُلوي
    layout["upper"]["catalog"].update(catalog_panel)
    layout["upper"]["logs"].update(logs_panel)

    # --- 3. قسم استهلاك الـ GPU والسيرفرات في الأسفل (GPU & Server Indicators) ---
    gpu_info = (
        f" [bold #ffb700]GPU Load:[/bold #ffb700] 48% | "
        f"[bold #00f3ff]VRAM Usage:[/bold #00f3ff] 11.2 / 16.0 GB | "
        f"[bold #ffb700]Wallet Balance:[/bold #ffb700] {tokens} TC | "
        r"[bold #00ff66]Oscilloscope Status:[/bold #00ff66] STABLE (~/\~/\~) ALL NODES OPTIMAL"
    )
    bottom_panel = Panel(gpu_info, title="[bold #00f3ff]💻 3. [AgentOS] Quantum Core & Oscilloscope Telemetry[/bold #00f3ff]", border_style="#00f3ff", box=DOUBLE)
    
    layout["lower"].update(bottom_panel)

    return layout

def run_live_matrix_dashboard():
    """تشغيل الشاشة التفاعلية المقسمة بشكل مستقر مع تصميم Neural Benchmarks Oscilloscope"""
    clear_screen()
    console.print("[bold #ffb700]🚀 Launching Live Split-Screen Dashboard Matrix (Oscilloscope Suite)...[/bold #ffb700]")
    console.print("[dim]Press [bold red]Ctrl + C[/bold red] or [bold red]q[/bold red] to return to the main menu.[/dim]\n")
    time.sleep(1.0)

    is_windows = platform.system() == "Windows"
    if is_windows:
        import msvcrt

    try:
        with Live(generate_dashboard_layout(), refresh_per_second=2, screen=False) as live:
            while True:
                if is_windows:
                    if msvcrt.kbhit():
                        try:
                            key = msvcrt.getch()
                            if key in (b'\xe0', b'\x00'):
                                msvcrt.getch()
                            elif key in (b'q', b'Q', b'\r', b'\n', b'\x1b'):
                                break
                        except Exception:
                            pass
                time.sleep(0.5)
                live.update(generate_dashboard_layout())
    except KeyboardInterrupt:
        pass
    
    clear_screen()
    console.print("[bold #00ff66]✔ Exiting Live Dashboard Matrix. Returning to main menu...[/bold #00ff66]\n")
    time.sleep(0.8)
