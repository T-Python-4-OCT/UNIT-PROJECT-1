"""Pure display functions: they print tables and panels, nothing else."""
from datetime import datetime

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from agency.config import APP_NAME, CURRENCY, DEFAULT_DAYS
from agency.flags import flag
from agency.services import currency, planner
from agency.ui.console import console

STATUS_STYLE = {
    "pending": "yellow",
    "confirmed": "green",
    "completed": "blue",
    "cancelled": "red",
}
CATEGORY_STYLE = {"city": "cyan", "beach": "yellow", "culture": "magenta", "adventure": "green"}
# One emoji per trip type. Each is a single wide character, so the table borders stay straight.
CATEGORY_ICON = {"city": "🌆", "beach": "🌴", "culture": "🏺", "adventure": "🧭"}


# تعرض قائمة خيارات في جدول ملون.
def show_menu(title: str, items, border_style: str = "cyan") -> None:
    """Draw a numbered menu. `items` is a list of (key, label); key "0" is shown in red."""
    table = Table(title=escape(title), header_style="bold magenta", border_style=border_style)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Action")
    for key, label in items:
        table.add_row(key, f"[red]{label}[/red]" if key == "0" else label)
    console.print(table)
    console.print("[dim]Tip: type b at any question to go back[/dim]")


# ترجع اسم الوجهة مع العلم: 🇹🇷 Istanbul, Turkey.
def place(item) -> str:
    """"🇹🇷 Istanbul, Turkey" for a destination or a booking (anything with a city and a country)."""
    return f"{flag(item.country)} {escape(item.city)}, {escape(item.country)}"


# ترجع نوع الرحلة مع إيموجي (🌆 🌴 🏺 🧭).
def category_label(category: str) -> str:
    """The trip type with its emoji and colour, e.g. "🌴 beach"."""
    color = CATEGORY_STYLE.get(category, "white")
    return f"{CATEGORY_ICON.get(category, '🌍')} [{color}]{category}[/]"


# تنسق المبلغ مع العملة، مثل 1,200 SAR.
def money(value) -> str:
    """Format a number as money, e.g. 1,200 SAR."""
    return f"{value:,.0f} {CURRENCY}"


# ترجع حالة الحجز بلون مناسب.
def status_text(status: str) -> str:
    """A booking status wrapped in its color."""
    return f"[{STATUS_STYLE.get(status, 'white')}]{status}[/]"


# تعرض إطار الترحيب بعد الدخول مع رقم العميل وملاحظاته.
def show_welcome(user, notes) -> None:
    """Welcome panel shown right after login or registration."""
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    intro = "Here is your agency overview." if user.role == "manager" else "Ready to plan your next trip?"
    lines = [f"[bold]{greeting}, {escape(user.full_name)}![/bold]  Welcome to {APP_NAME}.", intro]
    if user.role == "customer":
        lines.append(f"[cyan]Customer ID: #{user.id}[/cyan]  |  {escape(user.username)}  |  {escape(user.email)}")
    lines += [f"• {escape(note)}" for note in notes]
    console.print(Panel("\n".join(lines), title="Welcome ✈️", border_style="green", expand=False))


# تعرض نتيجة الإيميل: أُرسل، أو انحفظ في outbox، أو فشل مع السبب.
def show_mail_result(result) -> None:
    """Tell the user what happened to an email: sent, saved in the outbox, or failed."""
    who = escape(result.recipient) if result.recipient else "the customer"
    if result.status == "sent":
        console.print(f"[green]✉ An email was sent to {who}.[/green]")
        return
    if result.status == "saved":
        console.print(f"[yellow]✉ Email is not set up, so nothing was sent to {who}. "
                      f"A copy was saved in data/outbox/{escape(result.outbox_file)}[/yellow]")
        return
    console.print(f"[yellow]✉ The email to {who} could not be sent: {escape(result.detail)}[/yellow]")
    if result.outbox_file:
        console.print(f"[dim]A copy was saved in data/outbox/{escape(result.outbox_file)}[/dim]")


# تعرض جدول العملاء مع حجوزاتهم وما دفعوه.
def show_customers(rows) -> None:
    """Table of customers with their contact details and booking numbers."""
    table = Table(title="Customers", header_style="bold magenta", border_style="cyan")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Username")
    table.add_column("Email")
    table.add_column("Mobile")
    table.add_column("Bookings", justify="right")
    table.add_column("Active", justify="right")
    table.add_column("Paid", justify="right", style="green")
    for row in rows:
        user = row.user
        table.add_row(str(user.id), escape(user.full_name), f"@{escape(user.username)}", escape(user.email),
                      escape(user.phone) or "[dim]-[/dim]", str(row.bookings), str(row.active),
                      money(row.paid_total))
    console.print(table)


# تعرض جدول الوجهات، والموقوفة بخط عليها.
def show_countries(items, title="Destinations") -> None:
    """Table of destinations. Suspended ones are struck through."""
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Country", style="bold", no_wrap=True)
    table.add_column("City")
    table.add_column("Type", no_wrap=True)
    table.add_column("Flight", justify="right", style="green", no_wrap=True)
    table.add_column("Hotel/night", justify="right", style="green", no_wrap=True)
    table.add_column("Best season")
    for destination in items:
        city = escape(destination.city) + (" [red](suspended)[/]" if destination.suspended else "")
        table.add_row(str(destination.id), f"{flag(destination.country)} {escape(destination.country)}", city,
                      category_label(destination.category), money(destination.flight), money(destination.hotel),
                      escape(destination.best_season), style="strike dim" if destination.suspended else None)
    console.print(table)


# تعرض تفاصيل وجهة: المعالم وأفضل موسم والتكاليف اليومية ومثال سعر.
def show_country_detail(destination, days: int = DEFAULT_DAYS,
                        travelers: int = None, style: str = "standard") -> None:
    """Panel with a destination's highlights and costs."""
    count = travelers or 1
    total = planner.estimate(destination, days, count, style)["Total"]
    if travelers is None:
        price_line = f"Example: {days} days, 1 traveler, standard style = [bold green]{money(total)}[/]"
    else:
        noun = "traveler" if count == 1 else "travelers"
        price_line = f"Your trip: {days} days, {count} {noun}, {style} style = [bold green]{money(total)}[/]"
        if count > 1:
            price_line += f"\n  {money(round(total / count))} per person"
    lines = [
        f"[bold]{place(destination)}[/bold]  "
        f"({category_label(destination.category)})",
        f"Best season: [yellow]{escape(destination.best_season)}[/yellow]",
        "",
        "[bold]Highlights[/bold]",
        *[f"  • {escape(h)}" for h in destination.highlights],
        "",
        "[bold]Daily costs per person[/bold]",
        f"  Hotel {money(destination.hotel)}/night  |  Food {money(destination.food)}  |  "
        f"Transport {money(destination.transport)}  |  Activities {money(destination.activities)}",
        "",
        price_line,
    ]
    if destination.suspended:
        lines += ["", "[bold red]This trip is suspended until further notice and cannot be booked.[/]"]
    console.print(Panel("\n".join(lines), title=f"Destination #{destination.id}",
                        border_style="cyan", expand=False))


# ترجع لون درجة الحرارة: أحمر حار، أصفر دافي، أخضر معتدل، سماوي بارد.
def temperature_style(celsius: float) -> str:
    """Color for a temperature: hot is red, warm yellow, mild green, cold cyan."""
    if celsius >= 35:
        return "bold red"
    if celsius >= 25:
        return "yellow"
    if celsius >= 15:
        return "green"
    return "cyan"


# تعرض الطقس الحالي وجدول توقعات الأيام الجاية.
def show_weather(report: dict) -> None:
    """Show live conditions plus the forecast table."""
    temp = report["temperature"]
    header = (f"[bold]Now in {escape(report['city'])}:[/bold] "
              f"[{temperature_style(temp)}]{temp}°C[/]  |  {report['condition']}  |  "
              f"wind {report['wind']} km/h")
    table = Table(title="Forecast", header_style="bold magenta", border_style="cyan")
    table.add_column("Date")
    table.add_column("Conditions")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")
    for day in report["days"]:
        table.add_row(day["date"], day["condition"],
                      f"[{temperature_style(day['min'])}]{day['min']}°C[/]",
                      f"[{temperature_style(day['max'])}]{day['max']}°C[/]")
    console.print(Panel(header, title="Live weather", border_style="green", expand=False))
    console.print(table)


# تعرض وجهة مرشحة مع سبب الترشيح وطقسها وخطتها.
def show_recommendation(destination, reason: str, report, days: int = DEFAULT_DAYS) -> None:
    """One recommended trip: city, type, why, weather (None = unavailable) and the day-by-day plan."""
    if report:
        forecast = "  |  ".join(f"{day['date'][5:]} {day['condition']} {day['min']}-{day['max']}°C"
                                for day in report["days"][:3])
        weather_line = (f"[bold]Weather now:[/bold] [{temperature_style(report['temperature'])}]"
                        f"{report['temperature']}°C[/], {report['condition']}\n[dim]{forecast}[/dim]")
    else:
        weather_line = "[bold]Weather:[/bold] [yellow]not available right now[/yellow]"
    plan = [f"  [cyan]Day {i}[/cyan]: {escape(step)}"
            for i, step in enumerate(planner.build_itinerary(destination, days), start=1)]
    total = planner.estimate(destination, days, 1, "standard")["Total"]
    lines = [f"[bold]Type:[/bold] {category_label(destination.category)}   "
             f"[bold]Best season:[/bold] {escape(destination.best_season)}",
             f"[bold]Why:[/bold] [cyan]{escape(reason)}[/cyan]",
             weather_line, "", f"[bold]{days}-day plan[/bold]", *plan, "",
             f"About [bold green]{money(total)}[/] for {days} days, 1 traveler, standard style"]
    console.print(Panel("\n".join(lines), title=place(destination),
                        border_style="cyan", expand=False))


# تعرض الرحلات اللي تكفيها الميزانية مع تفاصيل المدن والمتبقي.
def show_plan_options(matches, budget: int) -> None:
    """Budget planner results with the key details of each city."""
    table = Table(title=f"Trips within {money(budget)}", header_style="bold magenta", border_style="cyan")
    for column, style in [("#", "cyan"), ("City details", ""), ("Type", ""), ("Total", "green"), ("Left", "yellow")]:
        table.add_column(column, style=style, no_wrap=column in ("Total", "Left"))
    for number, (destination, cost) in enumerate(matches, start=1):
        details = (f"{flag(destination.country)} [bold]{escape(destination.city)}[/bold], {escape(destination.country)}\n"
                   f"[dim]Best season: {escape(destination.best_season)}\n"
                   f"Highlights: {escape(', '.join(destination.highlights[:3]))}[/dim]")
        table.add_row(str(number), details, category_label(destination.category),
                      money(cost["Total"]), money(budget - cost["Total"]), end_section=True)
    console.print(table)


# تعرض جدول تفاصيل التكلفة، والخصومات بالأخضر.
def show_breakdown(cost: dict, budget=None, title="Cost breakdown") -> None:
    """Table with the cost breakdown (and the remaining budget)."""
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("Item")
    table.add_column("Cost", justify="right")
    for item, value in cost.items():
        if item == "Total":
            table.add_section()
            table.add_row("[bold]Total[/bold]", f"[bold green]{money(value)}[/]")
        elif value < 0:                      # a discount line
            table.add_row(f"[green]{escape(item)}[/green]", f"[green]{money(value)}[/green]")
        else:
            table.add_row(item, money(value))
    if budget is not None:
        left = budget - cost["Total"]
        style = "green" if left >= 0 else "red"
        table.add_row("Remaining budget", f"[{style}]{money(left)}[/]")
    console.print(table)


# تعرض الخطة اليومية للرحلة في إطار.
def show_itinerary(destination, days: int) -> None:
    """Day-by-day plan panel."""
    lines = [f"[cyan]Day {i}[/cyan]: {escape(step)}"
             for i, step in enumerate(planner.build_itinerary(destination, days), start=1)]
    title = f"{place(destination)} - {days} days"
    console.print(Panel("\n".join(lines), title=title, border_style="cyan", expand=False))


# تجهز خلايا اسم العميل وتواصله في جدول الحجوزات (أو 'عميل محذوف').
def _customer_cells(booking, customers: dict) -> tuple:
    """(customer cell, contact cell) for the manager's booking list."""
    user = customers.get(booking.user_id)
    if user is None:
        return f"[dim]Deleted customer #{booking.user_id}[/dim]", ""
    return (f"[bold]{escape(user.full_name)}[/bold]\n[dim]@{escape(user.username)} | ID #{user.id}[/dim]",
            f"{escape(user.email)}\n{escape(user.phone) or '[dim]no phone[/dim]'}")


# تعرض جدول الحجوزات (وللمدير مع بيانات الحاجز).
def show_bookings(items, title="Bookings", customers=None) -> None:
    """Table of bookings. Pass `customers` ({user id: User}) to also show who booked."""
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("ID", style="cyan", justify="right")
    if customers is not None:
        table.add_column("Customer")
        table.add_column("Contact")
    table.add_column("Destination", style="bold")
    table.add_column("Date")
    table.add_column("Days", justify="right")
    table.add_column("People", justify="right")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Paid")
    table.add_column("Status")
    for booking in items:
        row = [str(booking.id)]
        if customers is not None:
            row += _customer_cells(booking, customers)
        row += [place(booking), booking.travel_date, str(booking.days),
                str(booking.travelers), money(booking.total_price),
                "[green]yes[/]" if booking.paid else "[red]no[/]", status_text(booking.status)]
        table.add_row(*row, end_section=customers is not None)
    console.print(table)


# تعرض جدول أكواد الخصم وحالتها.
def show_promos(promos) -> None:
    """Table of discount codes (manager)."""
    table = Table(title="Discount codes", header_style="bold magenta", border_style="cyan")
    table.add_column("Code", style="bold cyan")
    table.add_column("Occasion")
    table.add_column("Discount", justify="right")
    table.add_column("Status")
    for promo in promos:
        table.add_row(promo.code, escape(promo.occasion), f"{promo.percent}%",
                      "[green]active[/]" if promo.active else "[red]off[/]")
    console.print(table)


# تعرض إيصال حجز مدفوع في إطار.
def show_receipt(booking, customer_name: str, destination=None, day_weather=None,
                 weather_note: str = "") -> None:
    """Receipt panel for a paid booking, with the trip plan and the weather on the travel day."""
    lines = [
        f"[bold]Reference:[/bold] {booking.reference}",
        f"[bold]Customer:[/bold]  {escape(customer_name)}",
        f"[bold]Trip:[/bold]      {place(booking)}",
        f"[bold]Date:[/bold]      {booking.travel_date}  "
        f"({booking.days} days, {booking.travelers} traveler(s), {booking.style})",
        f"[bold]Payment:[/bold]   {booking.payment_method.replace('_', ' ')}",
        f"[bold]Status:[/bold]    {status_text(booking.status)}",
        "",
    ]
    for item, value in booking.breakdown.items():
        if item != "Total":
            lines.append(f"  {item:<22}{money(value):>16}")
    lines.append(f"  {'-' * 38}")
    lines.append(f"  [bold green]{'TOTAL PAID':<22}{money(booking.total_price):>16}[/]")
    money_lines = currency.describe(booking.country, booking.total_price)
    if money_lines:
        lines += ["", f"[bold]Currency:[/bold] {escape(money_lines[0])}", f"  {escape(money_lines[1])}"]
    if destination is not None:
        if day_weather:
            weather_line = (f"{day_weather['condition']}, {day_weather['min']}-{day_weather['max']}°C")
        else:
            weather_line = f"[yellow]{escape(weather_note or 'not available')}[/yellow]"
        lines += ["", f"[bold]Weather on {booking.travel_date}:[/bold] {weather_line}",
                  f"[bold]Best season:[/bold] {escape(destination.best_season)}",
                  "", f"[bold]What you will visit ({booking.days} days)[/bold]"]
        lines += [f"  [cyan]Day {i}[/cyan]: {escape(step)}" for i, step in
                  enumerate(planner.build_itinerary(destination, booking.days), start=1)]
    console.print(Panel("\n".join(lines), title=f"{APP_NAME} Receipt",
                        border_style="green", expand=False))


# تعرض تقرير الوكالة: الإيرادات والحجوزات حسب الحالة وأكثر الوجهات.
def show_report(report: dict) -> None:
    """Dashboard tables for the manager."""
    head = Table(title="Agency overview", header_style="bold magenta", border_style="cyan")
    head.add_column("Metric")
    head.add_column("Value", justify="right", style="bold")
    head.add_row("Total revenue (paid)", f"[green]{money(report['revenue'])}[/]")
    head.add_row("Total bookings", str(report["total_bookings"]))
    head.add_row("Average paid booking", money(report["average_booking"]))
    head.add_row("Registered customers", str(report["customers"]))
    console.print(head)

    status = Table(title="Bookings by status", header_style="bold magenta", border_style="cyan")
    status.add_column("Status")
    status.add_column("Count", justify="right")
    for name, count in report["by_status"].items():
        status.add_row(status_text(name), str(count))
    console.print(status)

    if report["top_destinations"]:
        top = Table(title="Top destinations", header_style="bold magenta", border_style="cyan")
        top.add_column("Destination", style="bold")
        top.add_column("Bookings", justify="right")
        top.add_column("Paid revenue", justify="right", style="green")
        for name, (count, rev) in report["top_destinations"]:
            top.add_row(escape(name), str(count), money(rev))
        console.print(top)
