from rich.console import Console
from rich.panel import Panel

console = Console()

def check_agent_synergy(agents_list):
    """
    Calculate the strategic synergy multiplier based on agents in inventory or cart
    """
    if not agents_list:
        return []
        
    agent_names = [str(a.get("name", "")).lower() for a in agents_list]
    synergies_found = []
    
    # Rule 1: Combining coding agent with security agent (Cyber-Defense Grid)
    has_code = any("code" in name or "dev" in name or "deep" in name for name in agent_names)
    has_sec = any("sec" in name or "guard" in name or "shield" in name for name in agent_names)
    
    if has_code and has_sec:
        synergies_found.append({
            "title": "⚡ [bold green]Cyber-Defense Grid Synergy[/bold green]",
            "bonus": "+25% Processing Speed & Zero-Day Vulnerability Shield",
            "desc": "Combining software generation nodes with security guards locks down absolute system integrity."
        })
        
    # Rule 2: Owning 3 or more agents (Neural Swarm)
    if len(agents_list) >= 3:
        synergies_found.append({
            "title": "🧠 [bold cyan]Omni-Cluster Neural Swarm[/bold cyan]",
            "bonus": "+15% Token Efficiency & Multi-Agent Pipeline Link",
            "desc": "Operating 3+ specialized autonomous nodes forms a decentralized high-performance cluster."
        })
        
    return synergies_found

def display_synergy_report(agents_list):
    """Display synergy report in a cinematic format inside the terminal"""
    synergies = check_agent_synergy(agents_list)
    
    if not synergies:
        console.print("[dim]ℹ️ No active synergies detected. Purchase complementary agents to unlock multipliers.[/dim]")
        return
        
    console.print("\n[bold magenta]✦ ACTIVE AI AGENT SYNERGY MATRIX ✦[/bold magenta]")
    for syn in synergies:
        content = f"[bold white]Multiplier Bonus:[/bold white] {syn['bonus']}\n[dim]{syn['desc']}[/dim]"
        console.print(Panel(content, title=syn['title'], border_style="magenta", expand=False))
    console.print()
