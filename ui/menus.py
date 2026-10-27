import questionary
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE
from core.database import load_data, save_data
from ui.animations import clear_screen, CYBERPUNK_STYLE, display_banner, get_current_theme_colors

console = Console()

def display_agent_table(agents):
    """Display AI agents marketplace with Neon Cyan Cyberpunk Exchange theme."""
    from services.store import get_fluctuated_market_agents
    market_agents = get_fluctuated_market_agents(agents)
    
    ticker_panel = Panel(
        "[bold #00f3ff]⚡ MARKET EXCHANGE: AI-X UP +2.4% │ TRADING DESK: ONLINE │ VOLUME: 48,290 TC[/bold #00f3ff]\n"
        "[dim]Cyberpunk Neon Exchange // Real-time Fluctuating Agent Valuation & Quantum Pricing[/dim]",
        title="[bold #00f3ff][AgentOS] // NEURAL EXCHANGE TRADING FLOOR[/bold #00f3ff]",
        border_style="#00f3ff",
        box=ROUNDED,
        expand=False
    )
    console.print(ticker_panel)
    console.print()

    table = Table(
        title="[bold #00f3ff]🛒 [AgentOS] AI AGENTS MARKETPLACE (LIVE STOCK EXCHANGE)[/bold #00f3ff]",
        show_header=True,
        box=DOUBLE,
        border_style="#00f3ff",
        header_style="bold #ffb700"
    )
    table.add_column("ID", style="dim", width=4)
    table.add_column("Agent Name", style="bold #00ff66")
    table.add_column("Specialty", style="bold #ffb700")
    table.add_column("Success Rate", style="bold #00f3ff")
    table.add_column("Market Price (TC)", justify="right", style="bold #ffb700")

    for agent in market_agents:
        price_str = agent.get("price_display", f"{agent['price']} TC")
        table.add_row(agent["id"], agent["name"], agent["specialty"], f"{agent['success_rate']}%", price_str)
    console.print(table)

def calculate_operator_rank(data):
    """Calculate operator rank based on purchase history and activity"""
    history = data.get("history", [])
    count = len(history)
    
    if count >= 6:
        return "👑 [bold #ffb700]Master Architect[/bold #ffb700]"
    elif count >= 3:
        return "⚡ [bold #00ff66]Elite Hacker[/bold #00ff66]"
    elif count >= 1:
        return "💻 [bold #00f3ff]Cyber Specialist[/bold #00f3ff]"
    else:
        return "🌱 [dim]Novice Operator[/dim]"

def display_status_panel():
    data = load_data()
    tokens = data.get("tokens", 0)
    current_theme = data.get("theme", "Cyberpunk Neon")
    colors = get_current_theme_colors()
    operator_rank = calculate_operator_rank(data)
    
    status_text = (
        f"[{colors['accent']}]💰 WALLET:[/{colors['accent']}] [bold #00ff66]{tokens} TC[/bold #00ff66]     │     "
        f"[{colors['banner_style']}]🎨 THEME:[/{colors['banner_style']}] [bold white]{current_theme}[/bold white]     │     "
        f"[{colors['banner_style']}]RANK:[/{colors['banner_style']}] {operator_rank}     │     "
        f"[bold #00ff66]⚡ STATUS: ONLINE (8K ULTRA)[/bold #00ff66]"
    )
    panel = Panel(
        Align.center(Text.from_markup(status_text)),
        title=f"[{colors['banner_style']}]✦ [AgentOS] SYSTEM TELEMETRY & QUANTUM CORE STATUS ✦[/{colors['banner_style']}]",
        border_style=colors["border_style"],
        box=ROUNDED,
        padding=(1, 4),
        expand=True
    )
    console.print(panel)

def main_menu():
    while True:
        clear_screen()
        display_banner("Main Grid")
        display_status_panel()
        console.print()
        
        category = questionary.select(
            "❯ Choose AI Orchestration Category:",
            choices=[
                "🛒  Marketplace & Store (AI Agents & Cart)",
                "🧪  AI Sandbox & Simulations",
                "💳  Wallet & Finance Hub (Tokens & Promos)",
                "📊  System Reports & Analytics",
                "⚙️  Administration & Theme Engine",
                "🚪  Exit AgentOS"
            ],
            style=CYBERPUNK_STYLE
        ).ask()
        
        if category is None or "Exit" in category:
            return "🚪  Exit"
            
        if "Marketplace & Store" in category:
            sub_choice = questionary.select(
                "❯ Marketplace & Store Menu:",
                choices=[
                    "🛒  Browse AI Agents Catalogue",
                    "🔍  Search for an Agent",
                    "💡  Get AI Recommendations",
                    "🛍️  View My Cart & Checkout",
                    "📦  Track Deployment Status",
                    "⬅️  Back to Main Menu"
                ],
                style=CYBERPUNK_STYLE
            ).ask()
            if sub_choice and "Back" not in sub_choice:
                return sub_choice
                
        elif "Sandbox & Simulations" in category:
            sub_choice = questionary.select(
                "❯ AI Sandbox & Simulations Menu:",
                choices=[
                    "🤖 Test AI Model (Sandbox)",
                    "🖥️  Live Split-Screen Dashboard Matrix",
                    "🎨 ASCII Glitch Restorer (Mini-Game)",
                    "⬅️  Back to Main Menu"
                ],
                style=CYBERPUNK_STYLE
            ).ask()
            if sub_choice and "Back" not in sub_choice:
                return sub_choice

        elif "Wallet & Finance Hub" in category:
            sub_choice = questionary.select(
                "❯ Wallet & Finance Menu:",
                choices=[
                    "💳  Top-Up Wallet Tokens",
                    "🎟️  Redeem Promo Code",
                    "⬅️  Back to Main Menu"
                ],
                style=CYBERPUNK_STYLE
            ).ask()
            if sub_choice and "Back" not in sub_choice:
                return sub_choice
                
        elif "System Reports & Analytics" in category:
            sub_choice = questionary.select(
                "❯ System Reports & Analytics Menu:",
                choices=[
                    "📊  View Live System Dashboard",
                    "📋  View System Audit Logs",
                    "📁  Export Data Report to CSV",
                    "⬅️  Back to Main Menu"
                ],
                style=CYBERPUNK_STYLE
            ).ask()
            if sub_choice and "Back" not in sub_choice:
                return sub_choice
                
        elif "Administration & Theme" in category:
            sub_choice = questionary.select(
                "❯ Administration & Theme Menu:",
                choices=[
                    "⚙️  Manager Portal",
                    "🎨  Switch Terminal Theme",
                    "⬅️  Back to Main Menu"
                ],
                style=CYBERPUNK_STYLE
            ).ask()
            if sub_choice and "Back" not in sub_choice:
                return sub_choice

def select_theme_menu():
    """System Configuration Theme Engine under Gold Luxury / Industrial theme"""
    control_panel = Panel(
        "[bold #ffb700]⚙️ CONFIG BLOCK: VISUAL THEME ENGINE │ 🟢 CONTROL ACTIVE[/bold #ffb700]\n"
        "[dim]Select terminal aesthetic styling across system modules.[/dim]",
        title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION[/bold #ffb700]",
        border_style="#ffb700",
        box=HEAVY,
        expand=False
    )
    console.print(control_panel)
    console.print()

    choice = questionary.select(
        "❯ Choose a Visual Theme Style:",
        choices=[
            "Cyberpunk Neon",
            "Matrix Hacker",
            "Gold Luxury"
        ],
        style=CYBERPUNK_STYLE
    ).ask()
    
    if choice:
        data = load_data()
        data["theme"] = choice
        save_data(data)
        console.print(Panel(f"[bold #00ff66]✔ Theme configuration updated to '{choice}'! Re-open or refresh to apply full banner styles.[/bold #00ff66]", title="[bold #00ff66]Configuration Applied[/bold #00ff66]", border_style="#00ff66", box=HEAVY, expand=False))
