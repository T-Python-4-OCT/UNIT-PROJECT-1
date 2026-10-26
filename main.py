"""Garage system: entry point, menu loop and application flows."""

from __future__ import annotations

import sys
from pathlib import Path

from garage.camera import CameraScanner, CameraSettings, ScanStatus
from garage.plate_reader import create_reader
from garage.service import GarageService, ValidationError, Vehicle
from garage.storage import StorageError, VehicleStorage
from garage.ui import CancelledByUser, ConsoleUI


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VEHICLES_FILE = DATA_DIR / "vehicles.json"
CAMERA_FILE = DATA_DIR / "camera.json"


class GarageApp:
    """Connects the menu, the camera and the garage service."""

    def __init__(
        self, service: GarageService, ui: ConsoleUI, scanner: CameraScanner | None = None
    ) -> None:
        self.service = service
        self.ui = ui
        self.scanner = scanner

    # ------------------------------------------------------------------ #
    # Menu loop
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self.ui.banner()
        if self.scanner is None:
            self.ui.warning(
                "Camera scan is not available here (needs macOS, OpenCV and pyobjc Vision). "
                "You can still type the plate manually."
            )

        actions = {
            "scan": self.scan_plate,
            "manual": self.enter_plate,
            "list": self.list_vehicles,
        }
        while True:
            try:
                choice = self.ui.main_menu(scan_available=self.scanner is not None)
            except CancelledByUser:
                break
            if choice == "exit":
                break
            try:
                actions[choice]()
            except CancelledByUser:
                self.ui.warning("Cancelled.")
            except (StorageError, ValidationError) as exc:
                self.ui.error(str(exc))
        self.ui.info("Goodbye!")

    # ------------------------------------------------------------------ #
    # Getting the plate
    # ------------------------------------------------------------------ #
    def scan_plate(self) -> None:
        if self.scanner is None:
            self.enter_plate()
            return

        self.ui.info("Opening the camera... (click the camera window so it receives the keys)")
        result = self.scanner.scan()

        if result.status is ScanStatus.CAPTURED and result.plate:
            self.handle_plate(self._confirm_plate(result.plate))
        elif result.status is ScanStatus.MANUAL:
            self.enter_plate()
        elif result.status is ScanStatus.ERROR:
            self.ui.error(result.message)
            if self.ui.confirm("Enter the plate manually instead?"):
                self.enter_plate()
        else:
            self.ui.warning("Scan cancelled.")

    def enter_plate(self) -> None:
        self.handle_plate(self.ui.ask_plate())

    def _confirm_plate(self, plate: str) -> str:
        """OCR can make mistakes, so the staff always checks the number."""
        self.ui.show_plate(plate)                 
        if self.ui.confirm_plate(plate):
            return plate
        return self.ui.ask_plate(default=plate)


    # ------------------------------------------------------------------ #
    # What to do with a plate
    # ------------------------------------------------------------------ #
    def handle_plate(self, plate: str) -> None:
        vehicle = self.service.find_vehicle(plate)

        if vehicle is None:  # maybe OCR misread a character: "Did you mean...?"
            suggestions = self.service.similar_plates(plate)
            if suggestions:
                chosen = self.ui.choose_suggestion(plate, suggestions)
                if chosen:
                    plate = chosen
                    vehicle = self.service.find_vehicle(chosen)

        if vehicle is None:
            vehicle = self._register(plate)
        if vehicle is not None:
            self._vehicle_session(vehicle)

    def _register(self, plate: str) -> Vehicle | None:
        self.ui.warning(f"Plate {plate} is not registered.")
        if not self.ui.confirm("Register this vehicle now?"):
            return None
        details = self.ui.ask_vehicle_details(self.service.planner.today)
        vehicle = self.service.register_vehicle(plate=plate, **details)
        self.ui.success(f"Vehicle {vehicle.plate} registered.")
        return vehicle

    def _vehicle_session(self, vehicle: Vehicle) -> None:
        """Show the vehicle, then let the staff add services until they go back."""
        while True:
            self.ui.show_vehicle_report(vehicle, self.service.maintenance_for(vehicle))
            if self.ui.vehicle_menu() == "back":
                return
            self._add_service(vehicle)

    def _add_service(self, vehicle: Vehicle) -> None:
        details = self.ui.ask_service(
            vehicle, self.service.service_types, self.service.planner.today
        )
        record = self.service.add_service(vehicle.plate, **details)
        self.ui.success(f"{record.service_type} saved for {vehicle.plate}.")

    def list_vehicles(self) -> None:
        vehicles = self.service.all_vehicles()
        self.ui.show_vehicle_list(vehicles)
        if not vehicles:
            return
        plate = self.ui.choose_vehicle(vehicles)
        if plate:
            vehicle = self.service.find_vehicle(plate)
            if vehicle is not None:
                self._vehicle_session(vehicle)


# --------------------------------------------------------------------------- #
# Start-up
# --------------------------------------------------------------------------- #
def load_service(ui: ConsoleUI, storage: VehicleStorage) -> GarageService | None:
    """Load the data; if the file is corrupted, offer to back it up and start fresh."""
    try:
        return GarageService(storage)
    except StorageError as exc:
        ui.error(str(exc))
    try:
        if not ui.confirm("Back up the damaged file and start with an empty database?", False):
            return None
        backup = storage.backup_corrupted()
        if backup is not None:
            ui.info(f"Damaged file saved as {backup.name}")
        return GarageService(storage)
    except (CancelledByUser, StorageError) as exc:
        if isinstance(exc, StorageError):
            ui.error(str(exc))
        return None


def build_scanner() -> CameraScanner | None:
    """A camera scanner if this machine can do it, otherwise None (manual entry)."""
    reader = create_reader()
    if reader is None or not CameraScanner.is_available():
        return None
    return CameraScanner(reader, CameraSettings(CAMERA_FILE))


def main() -> int:
    ui = ConsoleUI()
    service = load_service(ui, VehicleStorage(VEHICLES_FILE))
    if service is None:
        return 1
    try:
        GarageApp(service, ui, build_scanner()).run()
    except KeyboardInterrupt:
        ui.info("Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
