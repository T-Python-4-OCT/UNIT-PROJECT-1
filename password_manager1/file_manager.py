import json
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from models import VaultItem

load_dotenv()
FILENAME = os.getenv("DATA_FILENAME", "passwords_data.json")
KEY_FILENAME = "secret.key"

def load_or_create_key():
   
    if os.path.exists(KEY_FILENAME):
        with open(KEY_FILENAME, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILENAME, "wb") as key_file:
            key_file.write(key)
        return key


ENCRYPTION_KEY = load_or_create_key()
cipher = Fernet(ENCRYPTION_KEY)


def save_vault(items_list):
    
    try:
        data = [item.to_dict() for item in items_list]
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        
        
        encrypted_data = cipher.encrypt(json_data.encode('utf-8'))
        
        with open(FILENAME, "wb") as f:
            f.write(encrypted_data)
    except Exception as e:
        print(f"❌ Error saving encrypted data: {e}")


def load_vault():
    
    if not os.path.exists(FILENAME):
        return []
    
    try:
        with open(FILENAME, "rb") as f:
            encrypted_data = f.read()
            if not encrypted_data:
                return []
            
            
            decrypted_data = cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode('utf-8'))
            
            return [VaultItem.from_dict(item) for item in data]
    except Exception as e:
        print(f"❌ Error loading or decrypting data: {e}")
        return [] 