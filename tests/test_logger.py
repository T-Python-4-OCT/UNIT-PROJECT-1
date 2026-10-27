import os
import pytest
from core.logger import log_action, get_audit_logs, AUDIT_LOG_FILE

def test_audit_logging():
    # Clean up before test
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)
        
    log_action("SUCCESS", "Test success message")
    log_action("TRANSACTION", "Test transaction message")
    
    logs = get_audit_logs()
    assert len(logs) == 2
    assert logs[0]["type"] == "SUCCESS"
    assert logs[0]["message"] == "Test success message"
    assert logs[1]["type"] == "TRANSACTION"
    assert logs[1]["message"] == "Test transaction message"
    
    # Clean up after test
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)
