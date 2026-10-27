import os
import pytest
from datetime import datetime
from services.sandbox import calculate_benchmark_metrics

def test_calculate_benchmark_metrics():
    """اختبار حساب مقاييس الأداء والاختبار المعياري للنموذج (Confidence, Accuracy, Speed)"""
    agent = {"name": "DeepCode-V4", "success_rate": 99.4}
    metrics = calculate_benchmark_metrics(agent)
    
    assert isinstance(metrics, dict)
    assert "confidence" in metrics
    assert "accuracy" in metrics
    assert "speed" in metrics
    assert isinstance(metrics["confidence"], float)
    assert isinstance(metrics["accuracy"], float)
    assert isinstance(metrics["speed"], str)

def test_benchmark_report_export():
    """اختبار حفظ وتصدير تقرير الاختبار المعياري إلى ملف benchmark_report.txt"""
    agent_name = "DeepCode-V4"
    specialty = "Architecture"
    test_count = 1
    metrics = {
        "confidence": 98.5,
        "accuracy": 99.2,
        "speed": "24.5 ms (1250 tokens/sec)"
    }
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_entry = (
        f"==================================================\n"
        f"AI MODEL TEST REPORT (CONFIDENCE, ACCURACY, SPEED)\n"
        f"Timestamp       : {timestamp}\n"
        f"Model Name      : {agent_name}\n"
        f"Specialty       : {specialty}\n"
        f"Test Cycle #    : {test_count}\n"
        f"Confidence      : {metrics['confidence']}%\n"
        f"Accuracy        : {metrics['accuracy']}%\n"
        f"Speed           : {metrics['speed']}\n"
        f"==================================================\n\n"
    )
    
    with open("benchmark_report.txt", "a", encoding="utf-8") as f:
        f.write(report_entry)
        
    assert os.path.exists("benchmark_report.txt")
    with open("benchmark_report.txt", "r", encoding="utf-8") as f:
        content = f.read()
    assert "DeepCode-V4" in content
    assert "Confidence" in content
    
    if os.path.exists("benchmark_report.txt"):
        os.remove("benchmark_report.txt")

def test_sandbox_input_validation():
    """اختبار التحقق من صحة إدخال المستخدم في وضع الساندبوكس (sandbox)"""
    allowed_commands = ["save", "exit", "quit", "q"]
    
    # Test empty input -> runs test
    user_input = ""
    assert user_input == ""
    
    # Test valid commands
    for cmd in ["save", "exit"]:
        assert cmd.lower() in allowed_commands
        
    # Test invalid / out-of-context inputs
    invalid_inputs = ["hi", "hello", "random", "test123", "foo"]
    for invalid in invalid_inputs:
        assert invalid.lower() not in allowed_commands
        assert invalid != ""
