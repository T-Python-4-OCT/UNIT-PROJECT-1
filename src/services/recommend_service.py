from src.utils.json_handler import load_json

SUPPLIES_FILE = "data/supplies.json"

def get_smart_recommendations(crisis_category: str):
    """Recommend supply items based on the crisis category ( Medical, Food, Shelter)"""
    supplies_list = load_json(SUPPLIES_FILE)
    recommendations = []
    
    for item in supplies_list:
        if item.get("category", "").lower() == crisis_category.lower():
            recommendations.append(item)
            
    if not recommendations and supplies_list:
        recommendations = supplies_list[:3]  
        
    return recommendations