"""Business rules: vehicles, service history and upcoming maintenance."""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable

from garage.plate_reader import PlateCleaner
from garage.storage import StorageError, VehicleStorage
import unicodedata



# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class ValidationError(ValueError):
    """The user typed something that is not valid."""


class DuplicateVehicleError(ValidationError):
    """A vehicle with this plate is already registered."""


class VehicleNotFoundError(ValidationError):
    """No vehicle is registered with this plate."""


# --------------------------------------------------------------------------- #
# Validation of user input
# --------------------------------------------------------------------------- #
class Validator:
    """Turns raw text typed by the user into clean, valid values."""

    MAX_MILEAGE = 2_000_000
    MAX_COST = 1_000_000
    MIN_YEAR = 1950

    @staticmethod
    def _number_text(value: Any) -> str:
        text = PlateCleaner.to_latin_digits(str(value)).strip()
        text = text.replace("\u066c", ",").replace("\u066b", ".")
        return text.replace(",", "").replace(" ", "")

    @staticmethod
    def text(value: Any, label: str, max_length: int = 60) -> str:
        cleaned = " ".join(str(value).split())
        if not cleaned:
            raise ValidationError(f"{label} cannot be empty.")
        if len(cleaned) > max_length:
            raise ValidationError(f"{label} is too long (max {max_length} characters).")
        return cleaned

    @staticmethod
    def optional_text(value: Any, max_length: int = 200) -> str:
        cleaned = " ".join(str(value or "").split())
        if len(cleaned) > max_length:
            raise ValidationError(f"Text is too long (max {max_length} characters).")
        return cleaned

    @staticmethod
    def plate(value: Any) -> str:
        cleaned = PlateCleaner.clean(str(value))
        if not PlateCleaner.is_plausible(cleaned):
            raise ValidationError(
                f"Plate must have {PlateCleaner.MIN_LENGTH}-{PlateCleaner.MAX_LENGTH} "
                "letters/digits, with at least one digit."
            )
        return cleaned
    
    @staticmethod
    def manual_plate(value: Any) -> str:
        """Manual entry: exactly 4 digits then 3 English letters (any case), e.g. 8301UJB."""
        text = str(value).strip()
        if not text:
            raise ValidationError("Enter the plate number. Example: 8301UJB")
        if not text.isascii():
            raise ValidationError("English letters and digits only. Example: 8301UJB")
        if not re.fullmatch(r"[0-9]{4}[A-Za-z]{3}", text):
            raise ValidationError(
                "Plate must be 4 digits then 3 letters, no spaces. Example: 8301UJB"
            )
        return text.upper()
    
    @staticmethod
    def person_name(value: Any, label: str = "Name", max_length: int = 60) -> str:
        """Letters (Arabic/English) and spaces only: digits and symbols are rejected."""
        cleaned = Validator.text(value, label, max_length)
        for ch in cleaned:
            is_mark = unicodedata.category(ch).startswith("M")  
            if not (ch.isalpha() or ch == " " or ch in "-'." or is_mark):
                raise ValidationError(f"{label} must contain letters only (no numbers).")
        if sum(ch.isalpha() for ch in cleaned) < 2:
            raise ValidationError(f"{label} is too short.")
        return cleaned

    @staticmethod
    def phone(value: Any) -> str:
        """Saudi mobile number: exactly 10 digits, starting with 05."""
        text = PlateCleaner.to_latin_digits(str(value)).strip()
        text = re.sub(r"[\s\-().]", "", text)
        if not re.fullmatch(r"05\d{8}", text):
            raise ValidationError("Phone must be exactly 10 digits and start with 05.")
        return text


    @classmethod
    def year(cls, value: Any, today: date | None = None) -> int:
        today = today or date.today()
        text = cls._number_text(value)
        if not re.fullmatch(r"\d{4}", text):
            raise ValidationError("Year must be 4 digits, for example 2018.")
        year = int(text)
        if not cls.MIN_YEAR <= year <= today.year + 1:
            raise ValidationError(f"Year must be between {cls.MIN_YEAR} and {today.year + 1}.")
        return year

    @classmethod
    def mileage(cls, value: Any, minimum: int = 0) -> int:
        """Whole km. ``minimum`` is the lowest allowed value (the car's current mileage)."""
        text = cls._number_text(value)
        if not re.fullmatch(r"\d+", text):
            raise ValidationError("Mileage must be a whole number of km (0 or more).")
        mileage = int(text)
        if mileage > cls.MAX_MILEAGE:
            raise ValidationError(f"Mileage cannot be more than {cls.MAX_MILEAGE:,} km.")
        if mileage < minimum:
            raise ValidationError(
                f"Mileage cannot be lower than the recorded mileage ({minimum:,} km)."
            )
        return mileage


    @classmethod
    def cost(cls, value: Any) -> float:
        text = cls._number_text(value)
        if not re.fullmatch(r"\d+(\.\d{1,2})?", text):
            raise ValidationError("Cost must be a number like 150 or 149.50.")
        cost = float(text)
        if cost > cls.MAX_COST:
            raise ValidationError(f"Cost cannot be more than {cls.MAX_COST:,}.")
        return round(cost, 2)

    @staticmethod
    def service_date(value: Any, today: date | None = None) -> date:
        today = today or date.today()
        text = PlateCleaner.to_latin_digits(str(value)).strip()
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Date must be in YYYY-MM-DD format, e.g. 2026-03-15.") from None
        if parsed > today:
            raise ValidationError("The service date cannot be in the future.")
        return parsed


# --------------------------------------------------------------------------- #
# Maintenance rules
# --------------------------------------------------------------------------- #
class Status(Enum):
    OK = "OK"
    SOON = "SOON"
    OVERDUE = "OVERDUE"
    NO_RECORD = "NO RECORD"


@dataclass(frozen=True)
class ServiceRule:
    """A service that must be repeated every N km and/or every N months."""

    name: str
    every_km: int | None = None
    every_months: int | None = None


# Edit these to change the maintenance rules.
SERVICE_RULES: tuple[ServiceRule, ...] = (
    ServiceRule("Oil change", every_km=5_000, every_months=6),
    ServiceRule("Filters", every_km=10_000, every_months=12),
    ServiceRule("Brakes", every_km=50_000),
    ServiceRule("Tires", every_km=40_000),
)
OTHER_SERVICE = "Other"
SOON_KM = 500
SOON_DAYS = 30


def add_months(start: date, months: int) -> date:
    """``start`` plus ``months`` calendar months (day is clamped to the month end)."""
    index = start.month - 1 + months
    year = start.year + index // 12
    month = index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
@dataclass
class Owner:
    name: str
    phone: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "phone": self.phone}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Owner":
        return cls(name=str(data["name"]), phone=str(data["phone"]))


@dataclass
class ServiceRecord:
    service_type: str
    date: date
    mileage: int
    cost: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.service_type,
            "date": self.date.isoformat(),
            "mileage": self.mileage,
            "cost": self.cost,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceRecord":
        return cls(
            service_type=str(data["type"]),
            date=date.fromisoformat(str(data["date"])),
            mileage=int(data["mileage"]),
            cost=float(data.get("cost", 0)),
            notes=str(data.get("notes", "")),
        )


@dataclass
class Vehicle:
    plate: str
    owner: Owner
    make: str
    model: str
    year: int
    mileage: int
    services: list[ServiceRecord] = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return round(sum(record.cost for record in self.services), 2)

    def add_service(self, record: ServiceRecord) -> None:
        self.services.append(record)
        self.services.sort(key=lambda r: (r.date, r.mileage))

    def last_service(self, service_type: str) -> ServiceRecord | None:
        matching = [r for r in self.services if r.service_type == service_type]
        return max(matching, key=lambda r: (r.date, r.mileage), default=None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plate": self.plate,
            "owner": self.owner.to_dict(),
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "mileage": self.mileage,
            "services": [record.to_dict() for record in self.services],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Vehicle":
        plate = PlateCleaner.clean(str(data["plate"]))
        if not plate:
            raise ValueError("empty plate")
        vehicle = cls(
            plate=plate,
            owner=Owner.from_dict(data["owner"]),
            make=str(data["make"]),
            model=str(data["model"]),
            year=int(data["year"]),
            mileage=int(data["mileage"]),
        )
        for item in data.get("services", []):
            vehicle.add_service(ServiceRecord.from_dict(item))
        return vehicle


@dataclass(frozen=True)
class MaintenanceItem:
    """The state of one maintenance rule for one vehicle."""

    rule: ServiceRule
    status: Status
    last_service: ServiceRecord | None = None
    due_km: int | None = None
    due_date: date | None = None
    km_left: int | None = None
    days_left: int | None = None


class MaintenancePlanner:
    """Works out what maintenance is due, soon, overdue or never recorded."""

    def __init__(
        self,
        rules: tuple[ServiceRule, ...] = SERVICE_RULES,
        today_func: Callable[[], date] = date.today,
    ) -> None:
        self.rules = rules
        self._today_func = today_func

    @property
    def today(self) -> date:
        return self._today_func()

    def plan(self, vehicle: Vehicle) -> list[MaintenanceItem]:
        return [self._evaluate(vehicle, rule) for rule in self.rules]

    def _evaluate(self, vehicle: Vehicle, rule: ServiceRule) -> MaintenanceItem:
        last = vehicle.last_service(rule.name)
        if last is None:
            return MaintenanceItem(rule, Status.NO_RECORD)

        due_km = last.mileage + rule.every_km if rule.every_km else None
        due_date = add_months(last.date, rule.every_months) if rule.every_months else None
        km_left = due_km - vehicle.mileage if due_km is not None else None
        days_left = (due_date - self.today).days if due_date is not None else None

        return MaintenanceItem(
            rule=rule,
            status=self._status(km_left, days_left),
            last_service=last,
            due_km=due_km,
            due_date=due_date,
            km_left=km_left,
            days_left=days_left,
        )

    @staticmethod
    def _status(km_left: int | None, days_left: int | None) -> Status:
        if (km_left is not None and km_left < 0) or (days_left is not None and days_left < 0):
            return Status.OVERDUE
        if (km_left is not None and km_left < SOON_KM) or (
            days_left is not None and days_left < SOON_DAYS
        ):
            return Status.SOON
        return Status.OK


# --------------------------------------------------------------------------- #
# The service used by the application
# --------------------------------------------------------------------------- #
class GarageService:
    """Vehicles and services, kept in memory and saved through ``VehicleStorage``."""

    def __init__(
        self, storage: VehicleStorage, planner: MaintenancePlanner | None = None
    ) -> None:
        self.storage = storage
        self.planner = planner or MaintenancePlanner()
        self._vehicles: dict[str, Vehicle] = {}
        self._load()

    # -- loading / saving -------------------------------------------------- #
    def _load(self) -> None:
        vehicles: dict[str, Vehicle] = {}
        for number, raw in enumerate(self.storage.load_vehicles(), start=1):
            try:
                vehicle = Vehicle.from_dict(raw)
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise StorageError(
                    f"{self.storage.path.name} is corrupted: invalid vehicle #{number} ({exc!r})."
                ) from exc
            vehicles[vehicle.plate] = vehicle
        self._vehicles = vehicles

    def _save(self) -> None:
        self.storage.save_vehicles([v.to_dict() for v in self._vehicles.values()])

    # -- queries ----------------------------------------------------------- #
    @property
    def service_types(self) -> list[str]:
        return [rule.name for rule in self.planner.rules] + [OTHER_SERVICE]

    def find_vehicle(self, plate: str) -> Vehicle | None:
        return self._vehicles.get(PlateCleaner.clean(plate))

    def all_vehicles(self) -> list[Vehicle]:
        return sorted(self._vehicles.values(), key=lambda v: v.plate)

    def maintenance_for(self, vehicle: Vehicle) -> list[MaintenanceItem]:
        return self.planner.plan(vehicle)

    def similar_plates(self, plate: str) -> list[str]:
        """Registered plates that look like ``plate`` (possible OCR mistakes)."""
        key = PlateCleaner.clean(plate)
        return sorted(p for p in self._vehicles if PlateCleaner.is_similar(key, p))

    # -- commands ---------------------------------------------------------- #
    def register_vehicle(
        self,
        plate: str,
        owner_name: str,
        phone: str,
        make: str,
        model: str,
        year: Any,
        mileage: Any,
    ) -> Vehicle:
        plate = Validator.plate(plate)
        if plate in self._vehicles:
            raise DuplicateVehicleError(f"Plate {plate} is already registered.")
        vehicle = Vehicle(
            plate=plate,
            owner=Owner(
                name=Validator.person_name(owner_name, "Owner name"),   
                phone=Validator.phone(phone),
            ),

            make=Validator.text(make, "Make"),
            model=Validator.text(model, "Model"),
            year=Validator.year(year, self.planner.today),
            mileage=Validator.mileage(mileage),
        )
        self._vehicles[plate] = vehicle
        try:
            self._save()
        except StorageError:
            del self._vehicles[plate]
            raise
        return vehicle

    def add_service(
        self,
        plate: str,
        service_type: str,
        service_date: Any,
        mileage: Any,
        cost: Any,
        notes: str = "",
    ) -> ServiceRecord:
        vehicle = self.find_vehicle(plate)
        if vehicle is None:
            raise VehicleNotFoundError(f"Plate {plate} is not registered.")
        if service_type not in self.service_types:
            raise ValidationError(f"Unknown service type: {service_type}")

        record = ServiceRecord(
            service_type=service_type,
            date=Validator.service_date(service_date, self.planner.today),
            mileage=Validator.mileage(mileage, minimum=vehicle.mileage), 
            cost=Validator.cost(cost),
            notes=Validator.optional_text(notes),
        )
        old_mileage = vehicle.mileage
        vehicle.add_service(record)
        vehicle.mileage = record.mileage                                  

        try:
            self._save()
        except StorageError:
            vehicle.services.remove(record)
            vehicle.mileage = old_mileage
            raise
        return record
