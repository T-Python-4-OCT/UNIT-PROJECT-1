import sys
import os
os.environ["PROMPT_TOOLKIT_NO_WINDOWS_CONSOLE"] = "1"
import questionary
from core.database import load_data, save_data, is_valid_name
from core.crypto_receipts import display_encrypted_receipts
from core.logger import log_action
from services.export import export_data_to_csv
from ui.animations import clear_screen, smooth_menu_transition, CYBERPUNK_STYLE
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import DOUBLE, ROUNDED
import time

console = Console()

MANAGER_PIN = "1234"

def manager_login():
    """Manager login portal with Deep Matrix Green governance theme and security clearance badges."""
    while True:
        clear_screen()
        
        shield_panel = Panel(
            "[bold #00ff66]🛡️ SECURITY SHIELD: ACTIVE (100%) │ CLEARANCE: ALPHA-1 ROOT[/bold #00ff66]\n"
            "[dim]Authentication required for Cyber Security & Governance Command Center.[/dim]\n"
            "[dim]💡 Type 'hint' below to reveal manager PIN hint[/dim]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #00ff66][AgentOS] // GOVERNANCE SECURITY GATEWAY[/bold #00ff66]",
            border_style="#00ff66",
            box=DOUBLE,
            expand=False
        )
        console.print(shield_panel)
        console.print()

        pin = console.input("\n[bold #00ff66]🔑 Enter Manager Access PIN: [/bold #00ff66]")
        
        if not pin.strip():
            console.print("[dim]Returning to Main Menu...[/dim]")
            time.sleep(0.4)
            return False
            
        if pin.strip().lower() == "hint":
            console.print(Panel("[bold #ffb700]💡 Hint Reminder: The manager PIN is 1234[/bold #ffb700]", title="[bold #ffb700]Hint[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
            time.sleep(1.5)
            continue

        if pin.strip() == MANAGER_PIN:
            console.print(Panel("[bold #00ff66]✔ ACCESS GRANTED. Alpha-1 Clearance Verified. Welcome, System Architect.[/bold #00ff66]", title="[bold #00ff66]Authentication Success[/bold #00ff66]", border_style="#00ff66", box=DOUBLE, expand=False))
            log_action("SUCCESS", "Manager successfully authenticated into the Cyber Security & Governance Portal.")
            time.sleep(0.8)
            return True
        else:
            console.print(Panel("[bold red]❌ ACCESS DENIED: Invalid Security PIN or Unauthorized Probe Detected.[/bold red]", title="[bold red]Authentication Failed[/bold red]", border_style="red", box=DOUBLE, expand=False))
            log_action("WARNING", "Manager authentication failed: Invalid security PIN entered.")
            time.sleep(1.2)

def manager_dashboard():
    """Manager dashboard for inventory management and registering new agents under Cyber Security & Governance theme."""
    if not manager_login():
        return
        
    while True:
        clear_screen()
        
        shield_panel = Panel(
            "[bold #00ff66]🛡️ GOVERNANCE ACTIVE │ SYSTEM INTEGRITY: 100% │ ENCRYPTION: FERNET[/bold #00ff66]\n"
            "[dim]Cyber Security & Governance Category Control Center[/dim]",
            title="[bold #00ff66][AgentOS] // ADMINISTRATOR COMMAND PORTAL[/bold #00ff66]",
            border_style="#00ff66",
            box=DOUBLE,
            expand=False
        )
        console.print(shield_panel)
        console.print()

        choice = questionary.select(
            "Manager Control Panel:",
            choices=[
                "📊 View All Inventory & Stock",
                "➕ Register New AI Agent",
                "✏️ Edit AI Agent",
                "🗑️ Delete AI Agent",
                "📜 View Encrypted Purchase Receipts & History",
                "📁 Export System Data to CSV (report.csv)",
                "🗑️  Data Reset (Clear History & Logs)",
                "🔙 Back to Main Menu"
            ],
            style=CYBERPUNK_STYLE
        ).ask()
        
        if choice == "📊 View All Inventory & Stock":
            smooth_menu_transition("Manager Inventory")
            show_inventory()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "➕ Register New AI Agent":
            smooth_menu_transition("Register New Agent")
            add_new_agent()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "✏️ Edit AI Agent":
            smooth_menu_transition("Edit AI Agent")
            edit_agent()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "🗑️ Delete AI Agent":
            smooth_menu_transition("Delete AI Agent")
            delete_agent()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "📜 View Encrypted Purchase Receipts & History":
            smooth_menu_transition("Encrypted Purchase Receipts & History")
            display_encrypted_receipts()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "📁 Export System Data to CSV (report.csv)":
            smooth_menu_transition("CSV Exporter")
            export_data_to_csv()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        elif choice == "🗑️  Data Reset (Clear History & Logs)":
            smooth_menu_transition("System Data Reset")
            reset_system_data()
            console.input("\n[dim]Press Enter to continue...[/dim]")
        else:
            log_action("SYSTEM", "Manager exited Administrator Portal and returned to main orchestration grid.")
            break

def reset_system_data():
    """Reset system data and clear logs and receipts using robust select menu under governance theme"""
    confirm_choice = questionary.select(
        "⚠️ WARNING: This will permanently wipe all history, cart items, encrypted receipts (receipts.json), audit logs (audit_logs.json), text receipts (receipts_log.txt), and reset wallet tokens to default (2000 TC). Proceed?",
        choices=[
            "No (Cancel)",
            "Yes (Proceed)"
        ],
        style=CYBERPUNK_STYLE
    ).ask()
    
    if confirm_choice != "Yes (Proceed)":
        console.print(Panel("[bold #ffb700]ℹ️ Data reset canceled by operator.[/bold #ffb700]", title="[bold #ffb700]Action Aborted[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        return

    from core.database import DEFAULT_AGENTS
    fresh_data = {
        "agents": DEFAULT_AGENTS,
        "cart": [],
        "history": [],
        "tokens": 2000,
        "theme": "Cyberpunk Neon",
        "redeemed_codes": []
    }
    save_data(fresh_data)

    files_to_remove = ["receipts.json", "audit_logs.json", "receipts_log.txt"]
    removed_count = 0
    for f_name in files_to_remove:
        if os.path.exists(f_name):
            try:
                os.remove(f_name)
                removed_count += 1
            except Exception:
                pass

    log_action("SUCCESS", "System Data Reset executed: History, cart, receipts, and audit logs cleared.")
    
    success_panel = (
        f"[bold #00ff66]✨ SYSTEM DATA RESET COMPLETE ✨[/bold #00ff66]\n\n"
        f"[bold white]• Wallet Tokens:[/bold white] [bold #ffb700]2000 TC (Default)[/bold #ffb700]\n"
        f"[bold white]• Shopping Cart:[/bold white] [bold #00ff66]Cleared (0 items)[/bold #00ff66]\n"
        f"[bold white]• Purchase History:[/bold white] [bold #00ff66]Reset (0 records)[/bold #00ff66]\n"
        f"[bold white]• Purged Files:[/bold white] [bold #00ff66]{removed_count} ledger files (receipts.json, audit_logs.json, receipts_log.txt)[/bold #00ff66]\n\n"
        f"[dim]AgentOS governance vault re-initialized with a clean slate.[/dim]"
    )
    
    console.print(Panel(
        success_panel,
        title="[bold #00ff66]🧹 CLEAN SLATE RESTORED[/bold #00ff66]",
        border_style="#00ff66",
        box=DOUBLE,
        expand=False
    ))

def show_inventory():
    """Display current inventory table under Cyber Security & Governance theme"""
    data = load_data()
    agents = data["agents"]
    
    table = Table(title="[bold #00ff66]🛡️ [AgentOS] GOVERNANCE INVENTORY & STOCK CONTROL[/bold #00ff66]", show_header=True, box=DOUBLE, border_style="#00ff66", header_style="bold #ffb700")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold #00ff66")
    table.add_column("Specialty", style="bold #ffb700")
    table.add_column("Stock", justify="right", style="bold #00f3ff")
    table.add_column("Price", justify="right", style="bold #ffb700")
    
    for agent in agents:
        table.add_row(
            agent["id"],
            agent["name"],
            agent["specialty"],
            str(agent.get("stock", 10)),
            f"{agent['price']} TC"
        )
    console.print(table)
    log_action("SYSTEM", f"Manager viewed inventory table containing {len(agents)} agents.")

def add_new_agent():
    """Register a new AI agent to the store under Cyber Security & Governance theme with validation"""
    data = load_data()
    
    while True:
        clear_screen()
        smooth_menu_transition("Register New Agent")
        console.print("[dim]Press Enter to return to menu[/dim]\n")
        
        name = questionary.text("Enter Agent Name:", style=CYBERPUNK_STYLE).ask()
        if not name or not name.strip():
            return
        valid, err_msg = is_valid_name(name)
        if not valid:
            console.print(Panel(f"[bold red]{err_msg}[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
            log_action("WARNING", f"Agent registration failed: {err_msg}")
            time.sleep(1.2)
            continue
            
        specialty = questionary.text("Enter Specialty (e.g. Vision, NLP):", style=CYBERPUNK_STYLE).ask()
        if not specialty or not specialty.strip():
            return
            
        try:
            success_rate_str = questionary.text("Enter Success Rate (e.g. 98.5):", style=CYBERPUNK_STYLE).ask()
            if not success_rate_str or not success_rate_str.strip():
                return
            success_rate = float(success_rate_str)
            
            price_str = questionary.text("Enter Price in Tokens (e.g. 400):", style=CYBERPUNK_STYLE).ask()
            if not price_str or not price_str.strip():
                return
            price = int(price_str)
            
            stock_str = questionary.text("Enter Initial Stock Quantity:", style=CYBERPUNK_STYLE).ask()
            if not stock_str or not stock_str.strip():
                return
            stock = int(stock_str)
            break
        except ValueError:
            console.print(Panel("[bold red]❌ Invalid input! Letters are not allowed in numbers.[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
            log_action("WARNING", "Agent registration failed due to invalid numeric inputs (letters in numbers).")
            time.sleep(1.2)
            continue
        
    new_id = str(len(data["agents"]) + 1).zfill(2)
    new_agent = {
        "id": new_id,
        "name": name.strip(),
        "specialty": specialty.strip(),
        "success_rate": success_rate,
        "price": price,
        "stock": stock
    }
    
    data["agents"].append(new_agent)
    save_data(data)
    log_action("SUCCESS", f"Registered new AI Agent '{name.strip()}' (Specialty: {specialty.strip()}, Price: {price} TC, Stock: {stock}) to marketplace.")
    console.print(Panel(f"[bold #00ff66]✔ Agent '{name.strip()}' successfully registered to the marketplace catalogue![/bold #00ff66]", title="[bold #00ff66]Registration Successful[/bold #00ff66]", border_style="#00ff66", box=DOUBLE, expand=False))

def edit_agent():
    """Edit an existing AI agent in the catalogue"""
    data = load_data()
    agents = data["agents"]
    
    if not agents:
        console.print(Panel("[bold red]❌ No agents available to edit.[/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        return

    while True:
        clear_screen()
        smooth_menu_transition("Edit AI Agent")
        show_inventory()
        console.print("\n[dim]Press Enter without text to return to menu[/dim]\n")
        
        agent_id = questionary.text("Enter Agent ID to edit (e.g. 01, 02):", style=CYBERPUNK_STYLE).ask()
        if not agent_id or not agent_id.strip():
            return
            
        target_agent = None
        for agent in agents:
            if agent["id"] == agent_id.strip():
                target_agent = agent
                break
                
        if not target_agent:
            console.print(Panel(f"[bold red]❌ Agent ID '{agent_id.strip()}' not found.[/bold red]", title="[bold red]Not Found[/bold red]", border_style="red", box=ROUNDED, expand=False))
            time.sleep(1.2)
            continue
            
        console.print(Panel(f"[bold #00ff66]Editing Agent: {target_agent['name']} (ID: {target_agent['id']})[/bold #00ff66]", title="[bold #00ff66]Agent Editor[/bold #00ff66]", border_style="#00ff66", box=ROUNDED, expand=False))
        
        new_name = questionary.text(f"Enter New Name [{target_agent['name']}]:", default=target_agent['name'], style=CYBERPUNK_STYLE).ask()
        if new_name is None:
            return
        if new_name.strip():
            valid, err_msg = is_valid_name(new_name)
            if not valid:
                console.print(Panel(f"[bold red]{err_msg}[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
                time.sleep(1.2)
                continue
            target_agent['name'] = new_name.strip()
            
        new_specialty = questionary.text(f"Enter New Specialty [{target_agent['specialty']}]:", default=target_agent['specialty'], style=CYBERPUNK_STYLE).ask()
        if new_specialty is None:
            return
        if new_specialty.strip():
            target_agent['specialty'] = new_specialty.strip()
            
        try:
            new_success_str = questionary.text(f"Enter New Success Rate [{target_agent['success_rate']}]:", default=str(target_agent['success_rate']), style=CYBERPUNK_STYLE).ask()
            if new_success_str is None:
                return
            if new_success_str.strip():
                target_agent['success_rate'] = float(new_success_str.strip())
                
            new_price_str = questionary.text(f"Enter New Price in Tokens [{target_agent['price']}]:", default=str(target_agent['price']), style=CYBERPUNK_STYLE).ask()
            if new_price_str is None:
                return
            if new_price_str.strip():
                target_agent['price'] = int(new_price_str.strip())
                
            new_stock_str = questionary.text(f"Enter New Stock Quantity [{target_agent.get('stock', 10)}]:", default=str(target_agent.get('stock', 10)), style=CYBERPUNK_STYLE).ask()
            if new_stock_str is None:
                return
            if new_stock_str.strip():
                target_agent['stock'] = int(new_stock_str.strip())
        except ValueError:
            console.print(Panel("[bold red]❌ Invalid input! Letters are not allowed in numbers.[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
            time.sleep(1.2)
            continue
            
        save_data(data)
        log_action("SUCCESS", f"Successfully updated Agent ID {target_agent['id']} ('{target_agent['name']}').")
        console.print(Panel(f"[bold #00ff66]✔ Agent '{target_agent['name']}' successfully updated![/bold #00ff66]", title="[bold #00ff66]Update Successful[/bold #00ff66]", border_style="#00ff66", box=DOUBLE, expand=False))
        break

def delete_agent():
    """Delete an AI agent from the marketplace catalogue"""
    data = load_data()
    agents = data["agents"]
    
    if not agents:
        console.print(Panel("[bold red]❌ No agents available to delete.[/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        return

    while True:
        clear_screen()
        smooth_menu_transition("Delete AI Agent")
        show_inventory()
        console.print("\n[dim]Press Enter without text to return to menu[/dim]\n")
        
        agent_id = questionary.text("Enter Agent ID to delete (e.g. 01, 02):", style=CYBERPUNK_STYLE).ask()
        if not agent_id or not agent_id.strip():
            return
            
        target_agent = None
        target_index = -1
        for idx, agent in enumerate(agents):
            if agent["id"] == agent_id.strip():
                target_agent = agent
                target_index = idx
                break
                
        if not target_agent:
            console.print(Panel(f"[bold red]❌ Agent ID '{agent_id.strip()}' not found.[/bold red]", title="[bold red]Not Found[/bold red]", border_style="red", box=ROUNDED, expand=False))
            time.sleep(1.2)
            continue
            
        confirm = questionary.select(
            f"⚠️ Are you sure you want to delete agent '{target_agent['name']}' (ID: {target_agent['id']})?",
            choices=["No (Cancel)", "Yes (Delete)"],
            style=CYBERPUNK_STYLE
        ).ask()
        
        if confirm != "Yes (Delete)":
            console.print(Panel("[bold #ffb700]ℹ️ Deletion canceled by operator.[/bold #ffb700]", title="[bold #ffb700]Action Aborted[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
            time.sleep(1.0)
            continue
            
        agents.pop(target_index)
        save_data(data)
        log_action("SUCCESS", f"Successfully deleted Agent ID {target_agent['id']} ('{target_agent['name']}').")
        console.print(Panel(f"[bold #00ff66]✔ Agent '{target_agent['name']}' successfully deleted from catalogue![/bold #00ff66]", title="[bold #00ff66]Deletion Successful[/bold #00ff66]", border_style="#00ff66", box=DOUBLE, expand=False))
        break
