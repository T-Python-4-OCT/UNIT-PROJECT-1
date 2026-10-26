from src import config


class Shipment:
    """One shipment record, exactly as stored in data/shipments.json."""

    def __init__(self, shipment_id: str, item_name: str, quantity: int, destination: str,
                 total_weight_kg=None, request_id=None, status: str = config.SHIP_PENDING, vehicle=None):
        self.shipment_id = shipment_id
        self.item_name = item_name
        self.quantity = quantity
        self.destination = destination
        self.total_weight_kg = total_weight_kg
        self.request_id = request_id          # the field request this shipment answers (optional)
        self.status = status
        self.vehicle = vehicle

    def assign(self, vehicle_name: str):
        self.vehicle = vehicle_name
        self.status = config.SHIP_IN_TRANSIT

    def deliver(self):
        self.status = config.SHIP_DONE

    def to_dict(self) -> dict:
        return {
            "shipment_id": self.shipment_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "destination": self.destination,
            "total_weight_kg": self.total_weight_kg,
            "request_id": self.request_id,
            "status": self.status,
            "vehicle": self.vehicle,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Shipment":
        return cls(d["shipment_id"], d.get("item_name", ""), d.get("quantity", 0), d.get("destination", ""),
                   d.get("total_weight_kg"), d.get("request_id"),
                   d.get("status", config.SHIP_PENDING), d.get("vehicle"))