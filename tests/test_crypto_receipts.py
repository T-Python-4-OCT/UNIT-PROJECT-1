import os
import json
import pytest
from core.crypto_receipts import get_or_create_secret_key, create_encrypted_receipt, decrypt_all_receipts, RECEIPTS_FILE, ENV_FILE
from cryptography.fernet import Fernet

def test_crypto_receipts_workflow():
    # Clean up test files
    if os.path.exists(RECEIPTS_FILE):
        os.remove(RECEIPTS_FILE)
        
    # 1. Test key generation / retrieval
    key = get_or_create_secret_key()
    assert isinstance(key, bytes)
    assert len(key) > 0
    assert os.path.exists(ENV_FILE)
    
    # 2. Create encrypted receipt
    create_encrypted_receipt("TX-9999", "Test Agent", "450 TC", "2026-10-25 12:00:00", "AGENT PURCHASE")
    assert os.path.exists(RECEIPTS_FILE)
    
    # 3. Decrypt receipts and verify valid status
    results = decrypt_all_receipts()
    assert len(results) == 1
    assert results[0]["status"] == "VALID"
    assert results[0]["data"]["transaction_id"] == "TX-9999"
    assert results[0]["data"]["item_name"] == "Test Agent"
    assert results[0]["data"]["amount"] == "450 TC"
    
    # 4. Test tampering / corruption handling
    with open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)
    tokens.append("gAAAAABcorruptedTokenStringInvalidForFernetEncryption123456789")
    with open(RECEIPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f)
        
    results = decrypt_all_receipts()
    assert len(results) == 2
    assert results[0]["status"] == "VALID"
    assert results[1]["status"] == "TAMPERED"
    
    # Clean up after test
    if os.path.exists(RECEIPTS_FILE):
        os.remove(RECEIPTS_FILE)
