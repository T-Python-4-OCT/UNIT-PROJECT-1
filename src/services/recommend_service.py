from src.utils.json_handler import load_json

SUPPLIES_FILE = "data/supplies.json"

def get_smart_recommendations(crisis_category: str):
    """Recommend supply items based on the crisis category (e.g., Medical, Food, Shelter)"""
    supplies_list = load_json(SUPPLIES_FILE)
    recommendations = []
    
    # Filter supplies that match or complement the crisis category
    for item in supplies_list:
        if item.get("category", "").lower() == crisis_category.lower():
            recommendations.append(item)
            
    # If no exact match, fallback to general items
    if not recommendations and supplies_list:
        recommendations = supplies_list[:3]  # Return top 3 items as general recommendation
        
    return recommendations