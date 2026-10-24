class SupplyItem:
    def __init__(self, item_id: str, name: str, category: str, quantity: int, unit_weight_kg: float):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.unit_weight_kg = unit_weight_kg

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "unit_weight_kg": self.unit_weight_kg
        }