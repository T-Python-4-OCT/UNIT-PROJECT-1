import os
import json
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import DOUBLE, ROUNDED
from core.logger import log_action

console = Console()
ENV_FILE = ".env"
RECEIPTS_FILE = "receipts.json"

def get_or_create_secret_key() -> bytes:
    """Read RECEIPT_SECRET_KEY from .env or generate a new Fernet key if missing."""
    key = None
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("RECEIPT_SECRET_KEY="):
                        key = line.strip().split("=", 1)[1].strip()
                        break
        except Exception:
            pass
            
    if not key:
        key = Fernet.generate_key().decode("utf-8")
        try:
            mode = "a" if os.path.exists(ENV_FILE) else "w"
            with open(ENV_FILE, mode, encoding="utf-8") as f:
                f.write(f"\nRECEIPT_SECRET_KEY={key}\n")
        except Exception:
            pass
            
    return key.encode("utf-8") if isinstance(key, str) else key

def create_encrypted_receipt(transaction_id: str, item_name: str, amount: str, timestamp: str = None, receipt_type: str = "TRANSACTION", extra_data: dict = None):
    """Build a receipt dictionary, encrypt it using Fernet, and append to receipts.json."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    receipt_data = {
        "transaction_id": transaction_id,
        "item_name": item_name,
        "amount": amount,
        "timestamp": timestamp,
        "type": receipt_type
    }
    if extra_data:
        receipt_data.update(extra_data)
    
    try:
        secret_key = get_or_create_secret_key()
        f = Fernet(secret_key)
        json_bytes = json.dumps(receipt_data, ensure_ascii=False).encode("utf-8")
        cipher_token = f.encrypt(json_bytes).decode("utf-8")
        
        receipts = []
        if os.path.exists(RECEIPTS_FILE):
            try:
                with open(RECEIPTS_FILE, "r", encoding="utf-8") as rf:
                    receipts = json.load(rf)
            except Exception:
                receipts = []
                
        receipts.append(cipher_token)
        
        with open(RECEIPTS_FILE, "w", encoding="utf-8") as wf:
            json.dump(receipts, wf, indent=4, ensure_ascii=False)
            
        log_action("SUCCESS", f"Encrypted receipt generated & securely stored for {item_id_or_name(item_name)} ({transaction_id})")
    except Exception as e:
        log_action("WARNING", f"Failed to generate encrypted receipt: {e}")

def item_id_or_name(name):
    return name

def decrypt_all_receipts():
    """Load receipts.json and decrypt each payload on-the-fly, handling tampering gracefully."""
    if not os.path.exists(RECEIPTS_FILE):
        return []
        
    secret_key = get_or_create_secret_key()
    fernet = Fernet(secret_key)
    
    try:
        with open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except Exception:
        return []
        
    decoded_results = []
    for token in tokens:
        try:
            decrypted_bytes = fernet.decrypt(token.encode("utf-8"))
            data = json.loads(decrypted_bytes.decode("utf-8"))
            decoded_results.append({
                "status": "VALID",
                "data": data
            })
        except (InvalidToken, Exception):
            decoded_results.append({
                "status": "TAMPERED",
                "raw": token[:30] + "..."
            })
            
    return decoded_results

def display_encrypted_receipts():
    """Render encrypted transaction ledger in Deep Matrix Green security layout with clearance badges & Fernet encryption status."""
    shield_panel = Panel(
        "[bold #00ff66]🛡️ FERNET ENCRYPTION: ACTIVE (128-BIT) │ DEEP MATRIX GOVERNANCE: SECURE[/bold #00ff66]\n"
        "[dim]Security Clearance: ALPHA-1 // Immutable Receipt Verification Active[/dim]",
        title="[bold #00ff66][AgentOS] // CRYPTOGRAPHIC GOVERNANCE VAULT[/bold #00ff66]",
        border_style="#00ff66",
        box=DOUBLE,
        expand=False
    )
    console.print(shield_panel)
    console.print()

    results = decrypt_all_receipts()
    
    if not results:
        console.print(Panel(
            "[bold #ffb700]📜 No encrypted purchase receipts found in 'receipts.json'.[/bold #ffb700]",
            title="[bold #ffb700]Encrypted Receipts Ledger[/bold #ffb700]",
            border_style="#00ff66",
            box=ROUNDED,
            expand=False
        ))
        return
        
    table = Table(
        title="[bold #00ff66]📜 [AgentOS] ENCRYPTED SECURE RECEIPTS LEDGER[/bold #00ff66]",
        show_header=True,
        box=DOUBLE,
        border_style="#00ff66",
        header_style="bold #ffb700"
    )
    table.add_column("Badge", width=14)
    table.add_column("Tx ID", style="bold #00ff66", width=14)
    table.add_column("Type", style="bold #ffb700", width=14)
    table.add_column("Name", style="bold white", width=14)
    table.add_column("Mobile", style="bold #00f3ff", width=12)
    table.add_column("Bank Card", style="dim", width=18)
    table.add_column("Details", style="bold white", width=18)
    table.add_column("Amount", justify="right", style="bold #ffb700", width=10)
    table.add_column("Timestamp", style="dim", width=19)
    
    for res in results:
        if res["status"] == "VALID":
            d = res["data"]
            badge = "[bold #00ff66]🟢 [VALID][/bold #00ff66]"
            name = d.get("full_name", d.get("buyer_name", "N/A"))
            mobile = d.get("saudi_mobile", d.get("phone_number", "N/A"))
            card = d.get("card_number", d.get("card_masked", "N/A"))
            table.add_row(
                badge,
                d.get("transaction_id", "N/A"),
                d.get("type", "TRANSACTION"),
                name,
                mobile,
                card,
                d.get("item_name", "N/A"),
                str(d.get("amount", "0")),
                d.get("timestamp", "N/A")
            )
        else:
            badge = "[bold red]🚨 [BREACH][/bold red]"
            table.add_row(
                badge,
                "CORRUPT",
                "UNKNOWN",
                "N/A",
                "N/A",
                "N/A",
                f"Raw: {res['raw']}",
                "N/A",
                "N/A"
            )
            
    console.print(table)
    console.print("[dim]💡 Tip: All receipts are cryptographically protected via Fernet symmetric encryption in .env.[/dim]\n")
