import random
import re
import time
import questionary
from core.database import load_data, save_data, is_valid_name
from core.logger import log_action
from core.crypto_receipts import create_encrypted_receipt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED, HEAVY
from ui.animations import CYBERPUNK_STYLE, clear_screen

console = Console()

def get_fluctuated_market_agents(agents=None):
    """Calculate dynamic market price fluctuations and generate Rich markup badges for agents."""
    if agents is None:
        data = load_data()
        agents = data.get("agents", [])
        
    fluctuated_list = []
    for agent in agents:
        agent_copy = agent.copy()
        if "base_price" not in agent_copy:
            agent_copy["base_price"] = agent_copy["price"]
            
        pct = round(random.uniform(-3.5, 3.5), 1)
        if pct == 0.0:
            pct = 1.5
            
        new_price = max(10, int(round(agent_copy["base_price"] * (1 + pct / 100))))
        agent_copy["price"] = new_price
        agent_copy["fluctuation_pct"] = pct
        
        if pct >= 0:
            agent_copy["price_display"] = f"{new_price} TC [bold #00ff66]▲ +{pct:.1f}%[/bold #00ff66]"
        else:
            agent_copy["price_display"] = f"{new_price} TC [bold red]▼ {pct:.1f}%[/bold red]"
            
        fluctuated_list.append(agent_copy)
        
    return fluctuated_list

def search_agents(query):
    """Search for an agent by name or specialty"""
    data = load_data()
    query = query.lower()
    results = [a for a in data["agents"] if query in a["name"].lower() or query in a["specialty"].lower()]
    log_action("SYSTEM", f"Searched agents catalogue with query: '{query}' (Found {len(results)} results)")
    return results

def add_to_cart(agent_id):
    """Add an agent to the shopping cart"""
    data = load_data()
    agent = next((a for a in data["agents"] if a["id"] == agent_id), None)
    
    if not agent:
        console.print(Panel(f"[bold red]❌ Agent ID '{agent_id}' not found![/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        return False
        
    if any(item["id"] == agent_id for item in data["cart"]):
        console.print(Panel(f"[bold #ffb700]⚠️ Agent '{agent['name']}' is already in your cart.[/bold #ffb700]", title="[bold #ffb700]Cart Warning[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        return False
        
    data["cart"].append(agent)
    save_data(data)
    log_action("SUCCESS", f"Added agent '{agent['name']}' (ID: {agent_id}) to shopping cart.")
    console.print(Panel(f"[bold #00ff66]✔ Added {agent['name']} to cart successfully![/bold #00ff66]", title="[bold #00ff66]Success[/bold #00ff66]", border_style="#00ff66", box=ROUNDED, expand=False))
    return True

def remove_from_cart(agent_id):
    """Remove an agent from the cart"""
    data = load_data()
    cart = data["cart"]
    new_cart = [item for item in cart if item["id"] != agent_id]
    
    if len(new_cart) == len(cart):
        console.print(Panel(f"[bold red]❌ Agent ID '{agent_id}' is not in your cart.[/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        return False
        
    data["cart"] = new_cart
    save_data(data)
    log_action("SYSTEM", f"Removed agent ID '{agent_id}' from shopping cart.")
    console.print(Panel("[bold #00ff66]✔ Agent removed from cart successfully![/bold #00ff66]", title="[bold #00ff66]Success[/bold #00ff66]", border_style="#00ff66", box=ROUNDED, expand=False))
    return True

def list_cart():
    """Display shopping cart contents with High-end Cyberpunk Neon exchange ticker layout"""
    data = load_data()
    cart = data["cart"]
    
    ticker_panel = Panel(
        "[bold #00f3ff]⚡ MARKET EXCHANGE: CART & DEPLOYMENT DESK │ STATUS: LIVE SYNC[/bold #00f3ff]\n"
        "[dim]Review selected AI agent cluster items prior to quantum checkout execution.[/dim]",
        title="[bold #00f3ff][AgentOS] // NEURAL TRADING CART[/bold #00f3ff]",
        border_style="#00f3ff",
        box=ROUNDED,
        expand=False
    )
    console.print(ticker_panel)
    console.print()

    if not cart:
        console.print(Panel("[bold #ffb700]🛒 Your cart is currently empty.[/bold #ffb700]", title="[bold #ffb700]Shopping Cart[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        return 0
        
    table = Table(title="[bold #00f3ff]🛒 [AgentOS] SELECTED CLUSTER AGENTS CART[/bold #00f3ff]", show_header=True, box=ROUNDED, border_style="#00f3ff", header_style="bold #ffb700")
    table.add_column("ID", style="dim")
    table.add_column("Agent Name", style="bold #00ff66")
    table.add_column("Specialty", style="bold #ffb700")
    table.add_column("Price (TC)", justify="right", style="bold #00f3ff")
    
    total = 0
    for item in cart:
        table.add_row(item["id"], item["name"], item.get("specialty", "Neural AI"), f"{item['price']} TC")
        total += item["price"]
        
    console.print(table)
    console.print(Panel(f"[bold #00f3ff]Total Cart Cluster Value: {total} TC[/bold #00f3ff]", title="[bold #00f3ff]Financial Summary[/bold #00f3ff]", border_style="#00f3ff", box=ROUNDED, expand=False))
    return total

def get_recommendations():
    """Provide smart AI recommendations to the operator based on purchase history"""
    data = load_data()
    history = data.get("history", [])
    agents = data["agents"]
    
    if not history:
        recs = sorted(agents, key=lambda x: x["success_rate"], reverse=True)[:2]
    else:
        bought_ids = {item["id"] for item in history}
        recommended = [a for a in agents if a["id"] not in bought_ids]
        recs = recommended[:2] if recommended else agents[:2]
        
    log_action("SYSTEM", f"Generated {len(recs)} AI recommendations for operator.")
    return recs

def top_up_tokens():
    """Token top-up feature with Settings & System Configuration modular industrial control panel layout"""
    data = load_data()
    current_tokens = data.get("tokens", 0)
    
    # 1. Full Name
    name = None
    while True:
        clear_screen()
        control_panel = Panel(
            f"[bold #ffb700]⚙️ CONFIG BLOCK: WALLET TOP-UP │ 🟢 GATEWAY ACTIVE[/bold #ffb700]\n"
            f"[bold #00f3ff]💳 Current Balance:[/bold #00f3ff] [bold #ffb700]{current_tokens} TC[/bold #ffb700]\n"
            "[dim]Modular Industrial Control Panel // Secure Hardware Diagnostic Active[/dim]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION & WALLET[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        )
        console.print(control_panel)
        console.print()
        
        name = questionary.text("Full Name:", style=CYBERPUNK_STYLE).ask()
        if not name or not name.strip():
            return
        valid, err_msg = is_valid_name(name)
        if valid:
            break
            
        console.print(Panel(f"[bold red]{err_msg}[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", f"Top-up attempt failed: {err_msg}")
        time.sleep(1.2)

    # 2. Saudi Mobile Number
    mobile = None
    while True:
        clear_screen()
        control_panel = Panel(
            f"[bold #ffb700]⚙️ CONFIG BLOCK: WALLET TOP-UP │ 🟢 GATEWAY ACTIVE[/bold #ffb700]\n"
            f"[bold #00f3ff]💳 Current Balance:[/bold #00f3ff] [bold #ffb700]{current_tokens} TC[/bold #ffb700]\n"
            f"[bold white]Full Name:[/bold white] [bold #00f3ff]{name.strip()}[/bold #00f3ff]\n"
            "[dim]Modular Industrial Control Panel // Saudi Mobile Validation[/dim]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION & WALLET[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        )
        console.print(control_panel)
        console.print()
        
        mobile = questionary.text("Saudi Mobile Number (e.g. 05XXXXXXXX):", style=CYBERPUNK_STYLE).ask()
        if not mobile or not mobile.strip():
            return
        if re.match(r"^05[0-9]{8}$", mobile.strip()):
            break
            
        console.print(Panel("[bold red]❌ Invalid Saudi Mobile Number! Must start with '05' followed by 8 digits (e.g., 0512345678).[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", "Top-up attempt failed due to invalid Saudi mobile number format.")
        time.sleep(1.2)

    # 3. Bank Card Number
    card_number = None
    while True:
        clear_screen()
        control_panel = Panel(
            f"[bold #ffb700]⚙️ CONFIG BLOCK: WALLET TOP-UP │ 🟢 GATEWAY ACTIVE[/bold #ffb700]\n"
            f"[bold #00f3ff]💳 Current Balance:[/bold #00f3ff] [bold #ffb700]{current_tokens} TC[/bold #ffb700]\n"
            f"[bold white]Full Name:[/bold white] [bold #00f3ff]{name.strip()}[/bold #00f3ff]\n"
            f"[bold white]Saudi Mobile:[/bold white] [bold #00f3ff]{mobile.strip()}[/bold #00f3ff]\n"
            "[dim]Modular Industrial Control Panel // Bank Card Security Check[/dim]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION & WALLET[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        )
        console.print(control_panel)
        console.print()
        
        card_number = questionary.text("Bank Card Number (16 digits):", style=CYBERPUNK_STYLE).ask()
        if not card_number or not card_number.strip():
            return
        if card_number.isdigit() and len(card_number) == 16:
            break
            
        console.print(Panel("[bold red]❌ Invalid Bank Card Number! Must be exactly 16 numeric digits.[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", "Top-up attempt failed due to invalid bank card number format.")
        time.sleep(1.2)

    # 4. Token Amount
    amount_str = None
    while True:
        clear_screen()
        control_panel = Panel(
            f"[bold #ffb700]⚙️ CONFIG BLOCK: WALLET TOP-UP │ 🟢 GATEWAY ACTIVE[/bold #ffb700]\n"
            f"[bold #00f3ff]💳 Current Balance:[/bold #00f3ff] [bold #ffb700]{current_tokens} TC[/bold #ffb700]\n"
            f"[bold white]Full Name:[/bold white] [bold #00f3ff]{name.strip()}[/bold #00f3ff]\n"
            f"[bold white]Saudi Mobile:[/bold white] [bold #00f3ff]{mobile.strip()}[/bold #00f3ff]\n"
            f"[bold white]Bank Card:[/bold white] [bold #ffb700]****-****-****-{card_number[-4:]}[/bold #ffb700]\n"
            "[dim]Modular Industrial Control Panel // Final Token Allocation[/dim]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION & WALLET[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        )
        console.print(control_panel)
        console.print()
        
        amount_str = questionary.text("Enter Token amount to top-up (e.g. 1000):", style=CYBERPUNK_STYLE).ask()
        if not amount_str or not amount_str.strip():
            return
        if amount_str.isdigit() and int(amount_str) > 0:
            break
            
        console.print(Panel("[bold red]❌ Invalid token amount entered. Must be a positive integer.[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", "Top-up attempt failed due to invalid token amount.")
        time.sleep(1.2)

    amount = int(amount_str)
    data["tokens"] = current_tokens + amount
    save_data(data)
    
    ref_id = f"TOPUP-{random.randint(1000,9999)}"
    masked_card = f"****-****-****-{card_number[-4:]}"
    
    create_encrypted_receipt(
        ref_id,
        f"Wallet Top-Up ({name.strip()})",
        f"+{amount} TC",
        receipt_type="TOKEN TOP-UP",
        extra_data={
            "full_name": name.strip(),
            "saudi_mobile": mobile.strip(),
            "card_number": card_number
        }
    )
    
    log_action("TRANSACTION", f"Wallet top-up successful: +{amount} TC added by {name.strip()} (Mobile: {mobile.strip()}). New balance: {data['tokens']} TC")
    
    success_banner = (
        f"[bold #00ff66]🎉 TOKEN RECHARGE SUCCESSFUL! 🎉[/bold #00ff66]\n\n"
        f"[bold white]Full Name:[/bold white] [bold #00f3ff]{name.strip()}[/bold #00f3ff]\n"
        f"[bold white]Saudi Mobile:[/bold white] [bold #00f3ff]{mobile.strip()}[/bold #00f3ff]\n"
        f"[bold white]Bank Card:[/bold white] [bold #ffb700]{masked_card}[/bold #ffb700]\n"
        f"[bold white]Amount Added:[/bold white] [bold #00ff66]+{amount} TC[/bold #00ff66]\n"
        f"[bold white]New Wallet Balance:[/bold white] [bold #ffb700]{data['tokens']} TC[/bold #ffb700]\n\n"
        f"[dim]Reference ID: {ref_id} │ Industrial Secure Control Block[/dim]"
    )
    
    console.print(Panel(
        success_banner,
        title="[bold #ffb700]⚙️ RECHARGE CONFIGURATION SECURED[/bold #ffb700]",
        border_style="#ffb700",
        box=HEAVY,
        expand=False
    ))
    console.input("\n[dim]Press Enter to return to menu...[/dim]")

def redeem_promo_code():
    """Redeem discount coupons with Settings & System Configuration industrial control panel theme"""
    data = load_data()
    if "redeemed_codes" not in data:
        data["redeemed_codes"] = []
        
    while True:
        clear_screen()
        control_panel = Panel(
            "[bold #ffb700]⚙️ CONFIG BLOCK: PROMO CODE REDEMPTION │ 🟢 TOGGLE ACTIVE[/bold #ffb700]\n"
            "[dim]Inject promotional discount coupons into system configuration.[/dim]\n"
            "[bold #ffb700]💡 Hint: Try codes like 'GRAD2026', 'CYBER100', 'AGENTOS500', or 'VIP2026'[/bold #ffb700]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #ffb700][AgentOS] // SYSTEM CONFIGURATION HUB[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        )
        console.print(control_panel)
        console.print()
        
        code = questionary.text("Enter Promo Code:", style=CYBERPUNK_STYLE).ask()
        if not code or not code.strip():
            return
            
        clean_code = code.strip().upper()
        
        promo_rewards = {
            "GRAD2026": 1000,
            "CYBER100": 500,
            "AGENTOS500": 500,
            "OGB500": 500,
            "VIP2026": 2000
        }
        
        if clean_code not in promo_rewards:
            console.print(Panel(
                f"[bold red]❌ INVALID PROMO CODE: '{code}'[/bold red]\n"
                "[dim]The configuration block rejects unknown coupon signatures.[/dim]",
                title="[bold red]Redemption Failed[/bold red]",
                border_style="red",
                box=HEAVY,
                expand=False
            ))
            log_action("WARNING", f"Attempted to redeem invalid promo code: '{code}'")
            time.sleep(1.2)
            continue
            
        if clean_code in data["redeemed_codes"]:
            console.print(Panel(
                f"[bold #ffb700]⚠️ PROMO CODE ALREADY REDEEMED[/bold #ffb700]\n"
                f"[dim]Configuration flag for '{clean_code}' has already been triggered.[/dim]",
                title="[bold #ffb700]Already Claimed[/bold #ffb700]",
                border_style="#ffb700",
                box=HEAVY,
                expand=False
            ))
            log_action("WARNING", f"Attempted to re-redeem already claimed promo code: '{clean_code}'")
            time.sleep(1.2)
            continue
            
        name = questionary.text("Enter Full Name:", style=CYBERPUNK_STYLE).ask()
        if not name or not name.strip():
            return
        mobile = questionary.text("Enter Mobile Number:", style=CYBERPUNK_STYLE).ask()
        if not mobile or not mobile.strip():
            return

        bonus = promo_rewards[clean_code]
        data["tokens"] = data.get("tokens", 2000) + bonus
        data["redeemed_codes"].append(clean_code)
        save_data(data)
        
        ref_id = f"PROMO-{clean_code}-{random.randint(100,999)}"
        create_encrypted_receipt(
            ref_id,
            f"Promo Code Reward ({clean_code})",
            f"+{bonus} TC",
            receipt_type="PROMO CODE",
            extra_data={
                "full_name": name.strip(),
                "saudi_mobile": mobile.strip(),
                "promo_code": clean_code
            }
        )
        
        new_balance = data["tokens"]
        log_action("TRANSACTION", f"Promo code '{clean_code}' redeemed successfully. Bonus: +{bonus} TC. New balance: {new_balance} TC")
        
        success_banner = (
            f"[bold #00ff66]🎉 PROMO CODE CONFIGURATION ACCEPTED! 🎉[/bold #00ff66]\n\n"
            f"[bold white]Redeemed Code:[/bold white] [bold #00f3ff]{clean_code}[/bold #00f3ff]\n"
            f"[bold white]Bonus Awarded:[/bold white] [bold #00ff66]+{bonus} TC[/bold #00ff66]\n"
            f"[bold white]New Wallet Balance:[/bold white] [bold #ffb700]{new_balance} TC[/bold #ffb700]\n\n"
            f"[dim]Industrial control block successfully updated.[/dim]"
        )
        
        console.print(Panel(
            success_banner,
            title="[bold #ffb700]⚙️ CONFIGURATION APPLIED[/bold #ffb700]",
            border_style="#ffb700",
            box=HEAVY,
            expand=False
        ))
        console.input("\n[dim]Press Enter to return to menu...[/dim]")
        break
