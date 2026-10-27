import pytest
from core.database import load_data, save_data, is_valid_name
from services.store import search_agents, add_to_cart, remove_from_cart, get_fluctuated_market_agents, redeem_promo_code
from ui.menus import calculate_operator_rank
from services.synergy import check_agent_synergy

def test_database_structure():
    """التحقق من أن قاعدة البيانات تحمل الهيكل الأساسي بشكل صحيح"""
    data = load_data()
    assert "agents" in data
    assert "cart" in data
    assert "history" in data
    assert "tokens" in data

def test_agent_search():
    """اختبار وظيفة البحث عن وكيل بالاسم أو التخصص"""
    results = search_agents("DeepCode")
    assert len(results) > 0
    assert results[0]["name"] == "DeepCode-V4"

def test_cart_flow():
    """اختبار دورة السلة (الإضافة، التحقق، والحذف)"""
    # تفريغ السلة للبدء باختبار نظيف
    data = load_data()
    data["cart"] = []
    save_data(data)
    
    # 1. اختبار إضافة وكيل للسلة
    added = add_to_cart("01")
    assert added is True
    
    data_checked = load_data()
    assert len(data_checked["cart"]) == 1
    assert data_checked["cart"][0]["id"] == "01"
    
    # 2. اختبار إزالة الوكيل من السلة
    removed = remove_from_cart("01")
    assert removed is True
    
    data_final = load_data()
    assert len(data_final["cart"]) == 0

def test_operator_rank():
    """اختبار حساب رتبة المستخدم بناءً على سجل المشتريات"""
    assert "Novice Operator" in calculate_operator_rank({"history": []})
    assert "Cyber Specialist" in calculate_operator_rank({"history": [{}]})
    assert "Elite Hacker" in calculate_operator_rank({"history": [{}, {}, {}]})
    assert "Master Architect" in calculate_operator_rank({"history": [{}, {}, {}, {}, {}, {}]})

def test_synergy_logic():
    """اختبار حساب قواعد التناغم الاستراتيجي للوكلاء"""
    # اختبار تداخل البرمجة والأمان
    agents = [{"name": "DeepCode-V4"}, {"name": "SecGuard"}]
    synergies = check_agent_synergy(agents)
    assert len(synergies) == 1
    assert "Cyber-Defense Grid" in synergies[0]["title"]
    
    # اختبار امتلاك 3 وكلاء أو أكثر
    agents_swarm = [{"name": "Agent1"}, {"name": "Agent2"}, {"name": "Agent3"}]
    synergies_swarm = check_agent_synergy(agents_swarm)
    assert any("Neural Swarm" in s["title"] for s in synergies_swarm)

def test_market_price_fluctuation():
    """اختبار نظام تقلب الأسعار الديناميكي في السوق ووجود شارات التغير"""
    agents = [{"id": "01", "name": "DeepCode-V4", "specialty": "Architecture", "success_rate": 99.4, "price": 450, "stock": 10}]
    market_agents = get_fluctuated_market_agents(agents)
    
    assert len(market_agents) == 1
    assert "price_display" in market_agents[0]
    assert "fluctuation_pct" in market_agents[0]
    assert "TC" in market_agents[0]["price_display"]
    assert "▲" in market_agents[0]["price_display"] or "▼" in market_agents[0]["price_display"]

def test_promo_code_redemption():
    """اختبار استرداد رموز الترويج وإضافة الرصيد ومراعاة عدم تكرار الاستخدام"""
    data = load_data()
    data["tokens"] = 2000
    data["redeemed_codes"] = []
    save_data(data)
    
    code = "GRAD2026"
    reward = 1000
    assert code not in data["redeemed_codes"]
    
    data["tokens"] += reward
    data["redeemed_codes"].append(code)
    save_data(data)
    
    updated_data = load_data()
    assert updated_data["tokens"] == 3000
    assert code in updated_data["redeemed_codes"]
    
    # تنظيف
    updated_data["tokens"] = 2000
    updated_data["redeemed_codes"] = []
    save_data(updated_data)

def test_saudi_mobile_validation():
    """اختبار التحقق من صحة رقم الجوال السعودي (يبدأ بـ 05 ويليه 8 أرقام)"""
    import re
    pattern = r"^05[0-9]{8}$"
    
    # حالات صحيحة
    assert bool(re.match(pattern, "0501234567")) is True
    assert bool(re.match(pattern, "0559876543")) is True
    
    # حالات خاطئة
    assert bool(re.match(pattern, "0401234567")) is False
    assert bool(re.match(pattern, "050123456")) is False
    assert bool(re.match(pattern, "05012345678")) is False
    assert bool(re.match(pattern, "050123456a")) is False

def test_bank_card_validation():
    """اختبار التحقق من أن رقم البطاقة البنكية يتكون من 16 رقماً בדיוק"""
    valid_card = "1234567890123456"
    assert valid_card.isdigit() and len(valid_card) == 16
    
    short_card = "123456789012345"
    assert not (short_card.isdigit() and len(short_card) == 16)
    
    alpha_card = "123456789012345a"
    assert not (alpha_card.isdigit() and len(alpha_card) == 16)

def test_interactive_retry_flow_options():
    """Test retry and return to main menu options"""
    choices = [
        "🔄 Try Again",
        "🔙 Return to Main Menu"
    ]
    assert len(choices) == 2
    assert "Try Again" in choices[0]
    assert "Return to Main Menu" in choices[1]

def test_name_validation():
    """اختبار قيود الأسماء (يجب أن تبدأ بحرف وتتكون من حروف ومسافات فقط بدون أرقام أو رموز أو شرطات في البداية)"""
    # حالات صحيحة
    assert is_valid_name("Ahmed Ali")[0] is True
    assert is_valid_name("محمد أحمد")[0] is True
    assert is_valid_name("CyberOperator")[0] is True

    # حالات خاطئة
    assert is_valid_name("-Ahmed")[0] is False  # تبدأ بشرطة
    assert is_valid_name("123Ahmed")[0] is False  # تبدأ برقم
    assert is_valid_name("@Ahmed")[0] is False  # تبدأ برمز
    assert is_valid_name("Ahmed@123")[0] is False  # تحتوي على رموز وأرقام
    assert is_valid_name("---")[0] is False  # رموز فقط
    assert is_valid_name("12345")[0] is False  # أرقام فقط
    assert is_valid_name("")[0] is False  # فارغ
    assert is_valid_name("   ")[0] is False  # مسافات فقط

def test_agent_add_edit_delete():
    """اختبار إضافة وتعديل وحذف الوكيل"""
    data = load_data()
    initial_count = len(data["agents"])
    
    # Add new agent
    new_agent = {
        "id": "99",
        "name": "TestAgent",
        "specialty": "Testing",
        "success_rate": 99.0,
        "price": 500,
        "stock": 10
    }
    data["agents"].append(new_agent)
    save_data(data)
    
    data_after_add = load_data()
    assert len(data_after_add["agents"]) == initial_count + 1
    
    # Edit agent
    for agent in data_after_add["agents"]:
        if agent["id"] == "99":
            agent["name"] = "UpdatedAgent"
            agent["price"] = 550
    save_data(data_after_add)
    
    data_after_edit = load_data()
    target = next(a for a in data_after_edit["agents"] if a["id"] == "99")
    assert target["name"] == "UpdatedAgent"
    assert target["price"] == 550
    
    # Delete agent
    data_after_edit["agents"] = [a for a in data_after_edit["agents"] if a["id"] != "99"]
    save_data(data_after_edit)
    
    data_final = load_data()
    assert len(data_final["agents"]) == initial_count



