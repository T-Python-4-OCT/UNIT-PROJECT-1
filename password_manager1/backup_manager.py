import os
from datetime import datetime
from activity_logger import log_activity
from colorama import Fore, Style
from cryptography.fernet import Fernet

BACKUP_DIR = "backups"

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_encrypted_backup():
    ensure_backup_dir()
    
    data_file = "passwords_data.json"
    if not os.path.exists(data_file):
        print(Fore.RED + "❌ No password data file found to backup!")
        return

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"backup_{timestamp}.enc"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists("secret.key"):
            print(Fore.RED + "❌ Encryption key (secret.key) missing!")
            return
            
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
            
        fernet = Fernet(key)
        
        with open(data_file, "rb") as f:
            original_data = f.read()
            
        encrypted_data = fernet.encrypt(original_data)
        
        with open(backup_path, "wb") as backup_file:
            backup_file.write(encrypted_data)
        log_activity("BACKUP_CREATED")    
        print(Fore.GREEN + f"✅ Encrypted backup created successfully: {backup_filename}")
        
    except Exception as e:
        print(Fore.RED + f"❌ Error creating backup: {e}")

def list_backups():
    ensure_backup_dir()
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".enc")]
    return backups

def restore_backup():
    ensure_backup_dir()
    backups = list_backups()
    
    if not backups:
        print(Fore.YELLOW + "⚠️ No backups available to restore.")
        return

    print(Fore.CYAN + "\n📂 AVAILABLE BACKUPS:")
    for i, b_file in enumerate(backups, start=1):
        print(f"{Fore.YELLOW} {i}. {Fore.WHITE}{b_file}")
    print(f"{Fore.YELLOW} b. {Fore.RED}Cancel")
    
    choice = input(Fore.GREEN + "Choose backup to restore (number) or 'b': " + Style.RESET_ALL).strip()
    if choice.lower() == 'b':
        return
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            selected_backup = os.path.join(BACKUP_DIR, backups[idx])
            
            confirm = input(Fore.RED + "⚠️ WARNING: Restoring will overwrite current data! Are you sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
              
                if not os.path.exists("secret.key"):
                    print(Fore.RED + "❌ Encryption key (secret.key) missing!")
                    return
                    
                with open("secret.key", "rb") as key_file:
                    key = key_file.read()
                fernet = Fernet(key)
                
               
                with open(selected_backup, "rb") as f:
                    encrypted_data = f.read()
                
             
                decrypted_data = fernet.decrypt(encrypted_data)
                
                
                with open("passwords_data.json", "wb") as f:
                    f.write(decrypted_data)
                log_activity("RESTORE_BACKUP")
                print(Fore.GREEN + f"✨ Successfully restored data from {backups[idx]}!")
            else:
                print(Fore.YELLOW + "❌ Restore cancelled.")
        else:
            print(Fore.RED + "❌ Invalid selection.")
    except Exception as e:
        print(Fore.RED + f"❌ Error restoring backup: {e}")