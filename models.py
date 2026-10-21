from dataclasses import dataclass
from datetime import datetime, timedelta

import config


@dataclass
class Table:
    id: int
    capacity: int
    location: str  


@dataclass
class Reservation:
    id: int
    table_id: int
    customer_name: str
    phone: str
    guests: int
    start: str                
    status: str = "confirmed"  

    @property
    def start_dt(self) -> datetime:
        return datetime.strptime(self.start, config.DATETIME_FORMAT)

    @property
    def end_dt(self) -> datetime:
        return self.start_dt + timedelta(minutes=config.BOOKING_DURATION_MINUTES)
