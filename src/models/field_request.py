from src import config


class FieldRequest:
    """An urgent request a field supervisor sends to the dispatcher."""

    def __init__(self, request_id: str, item_name: str, quantity: int, zone: str,
                 priority: str = "Medium", status: str = config.REQ_PENDING):
        self.request_id = request_id
        self.item_name = item_name
        self.quantity = quantity
        self.zone = zone
        self.priority = priority
        self.status = status

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "zone": self.zone,
            "priority": self.priority,
            "status": self.status,
        }