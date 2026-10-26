"""Console interface: input prompts (questionary) and colored tables (rich)."""

from __future__ import annotations

from datetime import date
from typing import Any, Callable

from rich import box
import questionary
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from garage.plate_reader import PlateCleaner



from garage.service import MaintenanceItem, Status, ValidationError, Validator, Vehicle


class CancelledByUser(Exception):
    """The user pressed Ctrl+C / Esc in a prompt."""


class ConsoleUI:
    """Everything the user sees and types."""

    CURRENCY = "SAR"
    KEEP = "__keep__"
    BACK = "__back__"
    STATUS_STYLES = {
        Status.OK: "bold green",
        Status.SOON: "bold yellow",
        Status.OVERDUE: "bold red",
        Status.NO_RECORD: "bold cyan",
    }

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    # ------------------------------------------------------------------ #
    # Messages
    # ------------------------------------------------------------------ #
    def banner(self) -> None:
        self.console.print()
        self.console.print()
        self.console.print()
        self.console.print()

        self.console.print(
            Panel.fit(
                "\n[bold yellow]   GARAGE CONTROL CENTER[/bold yellow]\nSystem is active and ready...\n",
                title=" Garage System",
                subtitle="Plate reading = History = Maintenance  ",
                box=box.DOUBLE,
                border_style="green",
                padding=(0, 16),
            )
        )
        self.console.print("🚗")






    def info(self, message: str) -> None:
        self.console.print(f"[cyan]ℹ[/cyan] {escape(message)}")

    def success(self, message: str) -> None:
        self.console.print(f"[green]✔[/green] {escape(message)}")

    def warning(self, message: str) -> None:
        self.console.print(f"[yellow]⚠[/yellow] {escape(message)}")

    def error(self, message: str) -> None:
        self.console.print(f"[red]✘[/red] {escape(message)}")

    def pause(self) -> None:
        try:
            self.console.input("\n[dim]Press Enter to continue...[/dim]")
        except (EOFError, KeyboardInterrupt):
            pass

    # ------------------------------------------------------------------ #
    # Prompt helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _ask(question: Any) -> Any:
        """Run a questionary question; Ctrl+C (None) becomes CancelledByUser."""
        answer = question.ask()
        if answer is None:
            raise CancelledByUser()
        return answer

    @staticmethod
    def _validator(parser: Callable[[str], Any]) -> Callable[[str], bool | str]:
        """Wrap a parser so questionary shows its error message while typing."""

        def check(value: str) -> bool | str:
            try:
                parser(value)
            except ValidationError as exc:
                return str(exc)
            return True

        return check

    def _text(self, message: str, parser: Callable[[str], Any], default: str = "") -> str:
        return self._ask(
            questionary.text(message, default=default, validate=self._validator(parser))
        ).strip()

    def confirm(self, message: str, default: bool = True) -> bool:
        return bool(self._ask(questionary.confirm(message, default=default)))

    # ------------------------------------------------------------------ #
    # Menus and questions
    # ------------------------------------------------------------------ #
    def main_menu(self, scan_available: bool) -> str:
        choices = []
        if scan_available:
            choices.append(questionary.Choice("Scan plate with camera", "scan"))
        choices += [
            questionary.Choice("Enter plate manually", "manual"),
            questionary.Choice("List all vehicles", "list"),
            questionary.Choice("Exit", "exit"),
        ]
        return self._ask(questionary.select("What would you like to do?", choices=choices))

    def vehicle_menu(self) -> str:
        return self._ask(
            questionary.select(
                "Vehicle actions:",
                choices=[
                    questionary.Choice("Add a service record", "service"),
                    questionary.Choice("Back to main menu", "back"),
                ],
            )
        )

    def ask_plate(self, default: str = "") -> str:
        text = self._text(
            "Plate number (4 digits then 3 letters, example: 8301UJB):",
            Validator.manual_plate,
            default,
        )
        return Validator.manual_plate(text)


    
    def show_plate(self, plate: str) -> None:
        """Show the plate like a real one: white rectangle, black digits."""
        self.console.print(
            Panel.fit(
                Text(PlateCleaner.display(plate), style="bold black", justify="center"),
                style="on white",
                border_style="black",
                padding=(0, 4),
            )
        )


    def confirm_plate(self, plate: str) -> bool:
        return self.confirm(f"Detected plate: {plate}. Is it correct?")

    def choose_suggestion(self, plate: str, suggestions: list[str]) -> str | None:
        """Ask 'Did you mean...?' and return the chosen plate (None = keep as typed)."""
        self.warning(f"Plate {plate} is not registered, but similar plates are.")
        choices = [questionary.Choice(f"Did you mean {item}?", item) for item in suggestions]
        choices.append(questionary.Choice(f"No, keep {plate}", self.KEEP))
        answer = self._ask(questionary.select("Choose:", choices=choices))
        return None if answer == self.KEEP else answer

    def choose_vehicle(self, vehicles: list[Vehicle]) -> str | None:
        choices = [
            questionary.Choice(f"{v.plate}  -  {v.make} {v.model} ({v.owner.name})", v.plate)
            for v in vehicles
        ]
        choices.append(questionary.Choice("Back", self.BACK))
        answer = self._ask(questionary.select("Open a vehicle:", choices=choices))
        return None if answer == self.BACK else answer

    def ask_vehicle_details(self, today: date) -> dict[str, str]:
        return {
            "owner_name": self._text("Owner name:", lambda v: Validator.person_name(v, "Owner name")),
            "phone": self._text("Owner phone (05XXXXXXXX):", Validator.phone),
            "make": self._text("Car make (e.g. Toyota):", lambda v: Validator.text(v, "Make")),
            "model": self._text("Car model (e.g. Camry):", lambda v: Validator.text(v, "Model")),
            "year": self._text("Year:", lambda v: Validator.year(v, today)),
            "mileage": self._text("Current mileage (km):", Validator.mileage),
        }
    def ask_service(
        self, vehicle: Vehicle, service_types: list[str], today: date
    ) -> dict[str, str]:
        service_type = self._ask(questionary.select("Service type:", choices=service_types))
        return {
            "service_type": service_type,
            "service_date": self._text(
                "Date (YYYY-MM-DD):",
                lambda v: Validator.service_date(v, today),
                today.isoformat(),
            ),
            "mileage": self._text(
                "Mileage at service (km):",
                lambda v: Validator.mileage(v, minimum=vehicle.mileage),
                str(vehicle.mileage),
            ),
            "cost": self._text(f"Cost ({self.CURRENCY}):", Validator.cost, "0"),
            "notes": self._ask(questionary.text("Notes (optional):")).strip(),
        }


    # ------------------------------------------------------------------ #
    # Tables
    # ------------------------------------------------------------------ #
    def show_vehicle_report(self, vehicle: Vehicle, items: list[MaintenanceItem]) -> None:
        self.show_vehicle(vehicle)
        self.show_history(vehicle)
        self.show_maintenance(items)

    def show_vehicle(self, vehicle: Vehicle) -> None:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold cyan")
        grid.add_column()
        grid.add_row("Plate", escape(vehicle.plate))
        grid.add_row("Vehicle", escape(f"{vehicle.make} {vehicle.model} ({vehicle.year})"))
        grid.add_row("Owner", escape(vehicle.owner.name))
        grid.add_row("Phone", escape(vehicle.owner.phone))
        grid.add_row("Mileage", f"{vehicle.mileage:,} km")
        grid.add_row("Services", str(len(vehicle.services)))
        grid.add_row("Total cost", self._money(vehicle.total_cost))
        self.console.print(Panel(grid, title="Vehicle", border_style="cyan", expand=False))

    def show_history(self, vehicle: Vehicle) -> None:
        if not vehicle.services:
            self.console.print("[dim]No service history yet.[/dim]")
            return
        table = Table(title="Service history", header_style="bold magenta")
        table.add_column("Date")
        table.add_column("Service")
        table.add_column("Mileage", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Notes")
        for record in vehicle.services:
            table.add_row(
                record.date.isoformat(),
                escape(record.service_type),
                f"{record.mileage:,} km",
                self._money(record.cost),
                escape(record.notes),
            )
        table.caption = f"Total: {self._money(vehicle.total_cost)}"
        self.console.print(table)

    def show_maintenance(self, items: list[MaintenanceItem]) -> None:
        table = Table(title="Upcoming maintenance", header_style="bold magenta")
        table.add_column("Service")
        table.add_column("Last done")
        table.add_column("Next at", justify="right")
        table.add_column("Next date")
        table.add_column("Status")
        for item in items:
            style = self.STATUS_STYLES[item.status]
            table.add_row(
                escape(item.rule.name),
                item.last_service.date.isoformat() if item.last_service else "-",
                self._remaining(item.due_km, item.km_left, "km"),
                self._remaining(item.due_date, item.days_left, "days"),
                f"[{style}]{item.status.value}[/{style}]",
            )
        self.console.print(table)

    def show_vehicle_list(self, vehicles: list[Vehicle]) -> None:
        if not vehicles:
            self.console.print("[dim]No vehicles registered yet.[/dim]")
            return
        table = Table(title="Registered vehicles", header_style="bold magenta")
        for column in ("Plate", "Vehicle", "Owner", "Phone"):
            table.add_column(column)
        table.add_column("Mileage", justify="right")
        table.add_column("Services", justify="right")
        for v in vehicles:
            table.add_row(
                escape(v.plate),
                escape(f"{v.make} {v.model} ({v.year})"),
                escape(v.owner.name),
                escape(v.owner.phone),
                f"{v.mileage:,} km",
                str(len(v.services)),
            )
        self.console.print(table)

    # ------------------------------------------------------------------ #
    # Formatting helpers
    # ------------------------------------------------------------------ #
    def _money(self, amount: float) -> str:
        return f"{amount:,.2f} {self.CURRENCY}"

    @staticmethod
    def _remaining(due: Any, left: int | None, unit: str) -> str:
        """'55,000 km (2,700 left)' / '2026-07-10 (106 days overdue)' / '-'."""
        if due is None or left is None:
            return "-"
        shown = f"{due:,}" if isinstance(due, int) else due.isoformat()
        if isinstance(due, int):
            shown += f" {unit}"
        if left < 0:
            return f"{shown} ({abs(left):,} {unit} overdue)"
        return f"{shown} ({left:,} {unit} left)"
