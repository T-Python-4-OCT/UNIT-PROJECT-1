from typing import List, Dict

class Shipment:
    def __init__(self, shipment_id: str, destination_crisis: str, transport_type: str):
        self.shipment_id = shipment_id
        self.destination_crisis = destination_crisis
        self.transport_type = transport_type  
        self.status = "Pending"  
        self.items: List[Dict] = []  


    def add_item(self, item_id: str, item_name: str, quantity: int, unit_weight_kg: float):
        self.items.append({
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity,
            "total_weight_kg": quantity * unit_weight_kg
        })



    def get_total_weight(self) -> float:
        return sum(item["total_weight_kg"] for item in self.items)


    def update_status(self, new_status: str):
        self.status = new_status


    def to_dict(self) -> dict:
        return {
            "shipment_id": self.shipment_id,
            "destination_crisis": self.destination_crisis,
            "transport_type": self.transport_type,
            "status": self.status,
            "total_weight_kg": self.get_total_weight(),
            "items": self.items
        }