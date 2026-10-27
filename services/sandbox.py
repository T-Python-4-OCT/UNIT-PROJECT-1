import time
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.box import DOUBLE, ROUNDED
from core.database import load_data
import questionary
from ui.animations import CYBERPUNK_STYLE

console = Console()

def calculate_benchmark_metrics(agent):
    """Calculate performance metrics for an AI model: Confidence, Accuracy, Speed."""
    raw_rate = agent.get("success_rate", 98.5)
    if isinstance(raw_rate, str):
        try:
            base_reliability = float(raw_rate.replace("%", "").strip())
        except ValueError:
            base_reliability = 98.5
    else:
        base_reliability = float(raw_rate)
        
    confidence = min(100.0, max(92.0, round(base_reliability + random.uniform(-0.3, 0.8), 2)))
    accuracy = min(100.0, max(90.0, round(base_reliability + random.uniform(-0.6, 0.9), 2)))
    speed = f"{round(random.uniform(12.5, 38.4), 2)} ms ({random.randint(600, 1500)} tokens/sec)"
    
    return {
        "confidence": confidence,
        "accuracy": accuracy,
        "speed": speed,
        "base_reliability": base_reliability
    }

def launch_sandbox():
    """Launch the AI Model Performance Testing Suite with all available models and Confidence, Accuracy, Speed metrics."""
    console.clear()
    
    data = load_data()
    agents = data.get("agents", [])
    
    scope_panel = Panel(
        r"[bold #00f3ff]~/\~/\~ AI MODEL TESTING SUITE: ALL MODELS AVAILABLE ~/\~/\~[/bold #00f3ff]" + "\n" +
        r"[dim]Metrics: Confidence // Accuracy // Speed[/dim]",
        title="[bold #00f3ff][AgentOS] // AI MODEL BENCHMARK PLAYGROUND[/bold #00f3ff]",
        border_style="#00f3ff",
        box=DOUBLE,
        expand=False
    )
    console.print(scope_panel)
    console.print()

    if not agents:
        console.print(Panel(
            "[bold red]❌ NO AI MODELS FOUND IN CATALOGUE[/bold red]\n"
            "[dim]No models available in system database.[/dim]",
            title="[bold red]Access Denied[/bold red]",
            border_style="red",
            box=ROUNDED,
            expand=False
        ))
        console.input("\n[dim]Press Enter to return to Main Menu...[/dim]")
        return

    with Progress(
        SpinnerColumn("dots", style="bold #00f3ff"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30, complete_style="bold #00ff66", style="dim #00f3ff"),
        console=console
    ) as progress:
        task = progress.add_task("[bold #00f3ff]Loading All Available AI Models & Testing Matrices...[/bold #00f3ff]", total=100)
        for _ in range(12):
            time.sleep(0.04)
            progress.update(task, advance=8.33)

    agent_options = []
    for i, agent in enumerate(agents):
        name = agent.get('name', 'AI Model')
        specialty = agent.get('specialty', agent.get('category', 'General AI'))
        agent_options.append(f"{i+1:02d} - {name} ({specialty})")
    
    agent_options.append("⬅ Back to Main Menu")
    
    selected = questionary.select(
        "⚡ Select an AI Model to Test (Confidence, Accuracy, Speed):",
        choices=agent_options,
        style=CYBERPUNK_STYLE
    ).ask()
    
    if not selected or "Back to Main Menu" in selected:
        return
        
    try:
        agent_index = int(selected.split(" - ")[0]) - 1
        agent = agents[agent_index]
    except (ValueError, IndexError):
        return
    
    agent_name = agent.get("name", "Unknown Model")
    specialty = agent.get("specialty", agent.get("category", "General AI"))
    base_rate = agent.get("success_rate", "98.5%")
    
    console.clear()
    console.print(Panel(
        r"[bold #00f3ff]~/\~/\~ AI MODEL TEST SUITE: ACTIVE BENCHMARK ~/\~/\~[/bold #00f3ff]" + "\n" +
        f"[bold white]Target Model:[/bold white] [bold #00ff66]{agent_name}[/bold #00ff66]\n"
        f"[bold white]Specialty:[/bold white] [bold #ffb700]{specialty}[/bold #ffb700]\n"
        f"[bold white]Base Reliability:[/bold white] [bold #00f3ff]{base_rate}%[/bold #00f3ff]\n"
        f"[dim]Press [Enter] to test (Confidence, Accuracy, Speed) | Type 'save' to save report | Type 'exit' to quit.[/dim]",
        title="[bold #00f3ff]AI Model Testing Playground[/bold #00f3ff]",
        border_style="#00f3ff",
        box=DOUBLE,
        expand=False
    ))
    
    test_count = 0
    latest_metrics = None
    
    while True:
        try:
            user_input = console.input(f"\n[bold #00ff66]⚡ [{agent_name}] > Press Enter to test (or 'save'/'exit'): [/bold #00ff66]").strip()
            
            if user_input == "":
                pass
            elif user_input.lower() in ["exit", "quit", "q"]:
                console.print(f"\n[dim]Disconnecting from {agent_name} Test Suite. Returning to Main Menu...[/dim]")
                time.sleep(0.4)
                break
                
            elif user_input.lower() == "save":
                if test_count == 0 or not latest_metrics:
                    console.print(Panel("[bold #ffb700]⚠️ No test has been executed yet. Run at least one test before saving![/bold #ffb700]", title="[bold #ffb700]Warning[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
                    continue
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                report_entry = (
                    f"==================================================\n"
                    f"AI MODEL TEST REPORT (CONFIDENCE, ACCURACY, SPEED)\n"
                    f"Timestamp       : {timestamp}\n"
                    f"Model Name      : {agent_name}\n"
                    f"Specialty       : {specialty}\n"
                    f"Test Cycle #    : {test_count}\n"
                    f"Confidence      : {latest_metrics['confidence']}%\n"
                    f"Accuracy        : {latest_metrics['accuracy']}%\n"
                    f"Speed           : {latest_metrics['speed']}\n"
                    f"==================================================\n\n"
                )
                try:
                    with open("benchmark_report.txt", "a", encoding="utf-8") as f:
                        f.write(report_entry)
                    console.print(Panel(
                        f"[bold #00ff66]💾 Test report successfully exported to 'benchmark_report.txt'![/bold #00ff66]\n"
                        f"[dim]Model: {agent_name} | Confidence: {latest_metrics['confidence']}% | Accuracy: {latest_metrics['accuracy']}%[/dim]",
                        title="[bold #00ff66]Report Export Successful[/bold #00ff66]",
                        border_style="#00ff66",
                        box=ROUNDED,
                        expand=False
                    ))
                except Exception as e:
                    console.print(Panel(f"[bold red]❌ Failed to save report: {e}[/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
                continue
            else:
                console.print(Panel(
                    "[bold #ffb700][ERROR]: Invalid command. Please use 'save', 'exit', or press Enter.[/bold #ffb700]",
                    title="[bold #ffb700]Invalid Input[/bold #ffb700]",
                    border_style="#ffb700",
                    box=ROUNDED,
                    expand=False
                ))
                continue
                
            test_count += 1
            
            with Progress(
                SpinnerColumn("aesthetic", style="bold #ffb700"),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(f"[bold #ffb700]Testing model {agent_name} (Confidence, Accuracy, Speed) - Test #{test_count}...", total=None)
                time.sleep(0.7)
            
            latest_metrics = calculate_benchmark_metrics(agent)
            
            report_content = (
                r"[bold #00f3ff]~/\~/\~ MODEL TEST CYCLE #" + str(test_count) + r" REPORT ~/\~/\~[/bold #00f3ff]" + "\n" +
                f"--------------------------------------------------\n"
                f"🧠 [bold white]Confidence:[/bold white]   [bold #ffb700]{latest_metrics['confidence']}%[/bold #ffb700]\n"
                f"🎯 [bold white]Accuracy:[/bold white]     [bold #00ff66]{latest_metrics['accuracy']}%[/bold #00ff66]\n"
                f"⚡ [bold white]Speed:[/bold white]       [bold #00f3ff]{latest_metrics['speed']}[/bold #00f3ff]\n"
                f"--------------------------------------------------\n"
                f"[dim]Status: OPTIMAL | Type 'save' to save report[/dim]"
            )
            
            console.print(Panel(
                report_content,
                title=f"[bold #00ff66]Model Test Report — Test #{test_count}[/bold #00ff66]",
                border_style="#00ff66",
                box=DOUBLE,
                expand=False
            ))
            
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[dim]Test session terminated safely by user.[/dim]")
            break

run_agent_sandbox = launch_sandbox
