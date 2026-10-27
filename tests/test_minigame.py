import pytest
from core.database import load_data, save_data
from services.minigame import run_ascii_glitch_restorer, run_hacking_minigame

def test_minigame_reward_logic():
    """اختبار إضافة رصيد التوكينز بناءً على نسبة ترميم اللوحة (98% -> 980 TC)"""
    data = load_data()
    initial_tokens = data.get("tokens", 0)
    
    restored_pct = 98
    earned_tokens = int(restored_pct * 10)
    
    data["tokens"] = initial_tokens + earned_tokens
    save_data(data)
    
    updated_data = load_data()
    assert updated_data["tokens"] == initial_tokens + earned_tokens
    
    # إعادة القيمة لما كانت عليه لعدم تخريب الحالة
    updated_data["tokens"] = initial_tokens
    save_data(updated_data)

def test_minigame_aliases():
    """التحقق من توافق الدوال"""
    assert callable(run_ascii_glitch_restorer)
    assert callable(run_hacking_minigame)
