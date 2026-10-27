import time
import random
import uuid
from datetime import datetime
from core.database import load_data, save_data, is_valid_name
from core.logger import log_action
from core.crypto_receipts import create_encrypted_receipt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
import questionary
from services.synergy import display_synergy_report
from ui.animations import CYBERPUNK_STYLE, clear_screen

console = Console()

def process_checkout():
    """Complete checkout, generate ASCII Art digital license certificate, and save it"""
    data = load_data()
    cart = data["cart"]
    
    if not cart:
        console.print(Panel("[bold #ffb700]🛒 Your cart is empty. Add agents before checkout.[/bold #ffb700]", title="[bold #ffb700]Cart Empty[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        return False
        
    total_price = sum(item["price"] for item in cart)
    current_tokens = data.get("tokens", 2000)
    
    if current_tokens < total_price:
        console.print(Panel(f"[bold red]❌ Insufficient tokens! You have {current_tokens} TC, but need {total_price} TC.[/bold red]", title="[bold red]Checkout Failed[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", f"Checkout failed: Insufficient tokens (Have {current_tokens} TC, Need {total_price} TC).")
        return False
        
    buyer_name = None
    while True:
        clear_screen()
        console.print(Panel(
            "[bold #00f3ff]🛍️ Shopping Cart & Checkout[/bold #00f3ff]\n"
            "[dim]Press Enter to return to menu[/dim]",
            title="[bold #00f3ff]Checkout Portal[/bold #00f3ff]",
            border_style="#00f3ff",
            box=ROUNDED,
            expand=False
        ))
        
        buyer_name = questionary.text("Enter License Holder Full Name:", style=CYBERPUNK_STYLE).ask()
        if not buyer_name or not buyer_name.strip():
            return False
        valid, err_msg = is_valid_name(buyer_name)
        if valid:
            break
            
        console.print(Panel(f"[bold red]{err_msg}[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", f"Checkout attempt failed: {err_msg}")
        time.sleep(1.2)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    phone_number = None
    while True:
        clear_screen()
        console.print(Panel(
            "[bold #00f3ff]🛍️ Shopping Cart & Checkout[/bold #00f3ff]\n"
            "[dim]Enter 10-digit mobile number (digits only, no symbols)[/dim]",
            title="[bold #00f3ff]Checkout Portal[/bold #00f3ff]",
            border_style="#00f3ff",
            box=ROUNDED,
            expand=False
        ))
        phone_number = questionary.text("Enter Mobile Number (10 digits):", style=CYBERPUNK_STYLE).ask()
        if not phone_number or not phone_number.strip():
            return False
        phone_number = phone_number.strip()
        if phone_number.isdigit() and len(phone_number) == 10:
            break
        console.print(Panel("[bold red]❌ Invalid Mobile Number! Must be exactly 10 numeric digits (no symbols or letters).[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", "Checkout attempt failed: Invalid mobile number format.")
        time.sleep(1.2)

    card_number = None
    while True:
        clear_screen()
        console.print(Panel(
            "[bold #00f3ff]🛍️ Shopping Cart & Checkout[/bold #00f3ff]\n"
            "[dim]Enter 16-digit bank card number (digits only, no symbols)[/dim]",
            title="[bold #00f3ff]Checkout Portal[/bold #00f3ff]",
            border_style="#00f3ff",
            box=ROUNDED,
            expand=False
        ))
        card_number = questionary.text("Enter Bank Card Number (16 digits):", style=CYBERPUNK_STYLE).ask()
        if not card_number or not card_number.strip():
            return False
        card_number = card_number.strip()
        if card_number.isdigit() and len(card_number) == 16:
            break
        console.print(Panel("[bold red]❌ Invalid Bank Card Number! Must be exactly 16 numeric digits (no symbols or letters).[/bold red]", title="[bold red]Validation Error[/bold red]", border_style="red", box=ROUNDED, expand=False))
        log_action("WARNING", "Checkout attempt failed: Invalid bank card number format.")
        time.sleep(1.2)

    data["tokens"] -= total_price
    for item in cart:
        item_copy = item.copy()
        item_copy["buyer"] = buyer_name.strip()
        item_copy["timestamp"] = timestamp
        data["history"].append(item_copy)
        
    agent_names = ", ".join([a["name"] for a in cart])
    agent_specialties = ", ".join([a.get("specialty", a.get("category", "General AI")) for a in cart])
    data["cart"] = []
    save_data(data)
    
    log_action("TRANSACTION", f"Successful checkout: Purchased [{agent_names}] for {total_price} TC. Holder: {buyer_name.strip()}.")
    
    console.print("\n")
    with console.status("[bold #ffb700]⚡ Processing Quantum Payment & Cluster Allocation...[/bold #ffb700]", spinner="dots"):
        time.sleep(2.0)
    
    display_success_celebration()
    
    with console.status("[bold #00f3ff]🎨 Generating Encrypted ASCII Digital License...[/bold #00f3ff]", spinner="arc"):
        time.sleep(1.5)
        
    cert_text, ref_id = generate_ascii_certificate(buyer_name.strip(), timestamp, agent_names, agent_specialties)
    
    extra_data = {
        "buyer_name": buyer_name.strip(),
        "phone_number": phone_number.strip(),
        "card_number": card_number.strip(),
        "model_name": agent_names,
        "model_type": agent_specialties
    }
    create_encrypted_receipt(ref_id, agent_names, f"{total_price} TC", timestamp, "AGENT PURCHASE", extra_data)
    
    console.print(Panel(
        f"[bold #00f3ff]{cert_text}[/bold #00f3ff]",
        title="[bold #00ff66]🏆 OFFICIAL DIGITAL LICENSE CERTIFICATE[/bold #00ff66]",
        border_style="#00f3ff",
        box=ROUNDED
    ))
    time.sleep(2.0)
    
    save_receipt_to_file(cart, total_price, buyer_name.strip(), timestamp, ref_id, cert_text)
    return True

def display_success_celebration():
    """Display animated success celebration with blinking effect"""
    with console.status("[bold #ffb700]🎆 Launching Cluster Fireworks & Generating License...[/bold #ffb700]", spinner="earth"):
        time.sleep(2.2)
    
    colors = ["#00ff66", "#00f3ff", "#ffb700", "#00ff66", "#00f3ff", "#00ff66"]
    for color in colors:
        console.print(Text("✨ SUCCESS! ALL NODES DEPLOYED & SYNCED ✨", style=f"bold {color}"), justify="center")
        time.sleep(0.35)
        
    time.sleep(0.5)

def generate_ascii_certificate(buyer_name, timestamp, agent_names, agent_specialties):
    """Generate large digital ASCII Art license certificate"""
    ref_id = f"CRN-{uuid.uuid4().hex[:6].upper()}-{random.randint(1000, 9999)}"
    barcode = "█ █║█║█ █║█ █║█║█ █║█ █║█║█ █ █║██"
    
    ascii_cert = f"""
  +------------------------------------------------------------------+
  |                 [AgentOS] CLUSTER LICENSE CERTIFICATE            |
  +------------------------------------------------------------------+
  |  HOLDER NAME  : {buyer_name:<45} |
  |  REFERENCE ID : {ref_id:<45} |
  |  PURCHASE TIME: {timestamp:<45} |
  |  PURCHASED MOD: {agent_names:<45} |
  |  MODEL TYPE   : {agent_specialties:<45} |
  |  STATUS       : [ SECURED & VERIFIED BY QUANTUM CORE ]           |
  |                                                                  |
  |  SECURE BARCODE: {barcode}                 |
  +------------------------------------------------------------------+
    """
    return ascii_cert, ref_id

def save_receipt_to_file(cart, total_price, buyer_name, timestamp, ref_id, cert_text):
    """Save license certificate and receipt cumulatively to receipts log"""
    filename = "receipts_log.txt"
    
    content = f"""{cert_text}
Timestamp: {timestamp}
Holder Name: {buyer_name}
Total Paid: {total_price} TC
--------------------------------------------------
"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content)
        console.print(Panel(f"[bold #00ff66]📄 Digital Certificate & Receipt successfully logged to '{filename}'![/bold #00ff66]", title="[bold #00ff66]Receipt Saved[/bold #00ff66]", border_style="#00ff66", box=ROUNDED, expand=False))
        time.sleep(1.0)
    except Exception as e:
        console.print(Panel(f"[bold red]⚠️ Failed to export certificate file: {e}[/bold red]", title="[bold red]Error[/bold red]", border_style="red", box=ROUNDED, expand=False))

def track_deployment_status():
    """Track deployment status of deployed agents"""
    data = load_data()
    history = data.get("history", [])
    
    if not history:
        console.print(Panel("[bold #ffb700]📦 No active or past deployments found in history.[/bold #ffb700]", title="[bold #ffb700]Deployments[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        log_action("SYSTEM", "Tracked deployment status: No active history found.")
        return
        
    with console.status("[bold #00f3ff]Querying Cluster Deployment Nodes...[/bold #00f3ff]", spinner="dots"):
        time.sleep(1.2)
        
    table = Table(title="[bold #00f3ff]Active AI Cluster Deployments[/bold #00f3ff]", show_header=True, box=ROUNDED, border_style="#00f3ff", header_style="bold #ffb700")
    table.add_column("Agent Name", style="bold #00ff66")
    table.add_column("Specialty", style="bold #ffb700")
    table.add_column("Deployment Status", style="bold #00f3ff")
    
    for item in history:
        table.add_row(item["name"], item["specialty"], "🟢 ONLINE / SYNCED (100%)")
        
    console.print(table)
    log_action("SYSTEM", f"Tracked deployment status for {len(history)} deployed agents.")

def view_purchase_history():
    """Display past purchase history and receipts inside a sleek table"""
    data = load_data()
    history = data.get("history", [])
    
    if not history:
        console.print(Panel("[bold #ffb700]📜 No purchase history or receipts found yet.[/bold #ffb700]", title="[bold #ffb700]History Ledger[/bold #ffb700]", border_style="#ffb700", box=ROUNDED, expand=False))
        log_action("SYSTEM", "Viewed purchase history: Ledger is empty.")
        return
        
    table = Table(title="[bold #00f3ff]📜 Past Purchase History & Deployed Receipts[/bold #00f3ff]", show_header=True, box=ROUNDED, border_style="#00f3ff", header_style="bold #ffb700")
    table.add_column("#", style="dim", width=4)
    table.add_column("Model Name", style="bold #00ff66")
    table.add_column("Model Type", style="bold #ffb700")
    table.add_column("Holder Name", style="bold white")
    table.add_column("Purchase Time", style="bold #00f3ff")
    table.add_column("Price Paid", justify="right", style="bold #ffb700")
    
    for idx, item in enumerate(history, 1):
        table.add_row(
            str(idx),
            item.get("name", "N/A"),
            item.get("specialty", item.get("category", "N/A")),
            item.get("buyer", "Authorized Developer"),
            item.get("timestamp", "N/A"),
            f"{item.get('price', 0)} TC"
        )
    console.print(table)
    console.print("[dim]💡 Tip: Full text receipts are also automatically appended to 'receipts_log.txt'.[/dim]\n")
    log_action("SYSTEM", f"Viewed purchase history ledger containing {len(history)} past receipts.")
    
    display_synergy_report(history)
