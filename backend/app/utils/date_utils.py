from datetime import datetime, timedelta, timezone
import re


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _next_weekday(target_weekday: int, now: datetime) -> datetime:
    days_ahead = target_weekday - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return now + timedelta(days=days_ahead)


def parse_deadline(deadline: str | None, now: datetime | None = None) -> datetime | None:
    if not deadline:
        return None

    now = now or datetime.now(timezone.utc)
    text = deadline.strip().lower()

    if text in {"today"}:
        return now.replace(hour=23, minute=59, second=59, microsecond=0)
    if text in {"tomorrow"}:
        dt = now + timedelta(days=1)
        return dt.replace(hour=23, minute=59, second=59, microsecond=0)
    if text in WEEKDAYS:
        dt = _next_weekday(WEEKDAYS[text], now)
        return dt.replace(hour=23, minute=59, second=59, microsecond=0)
    if text.startswith("next ") and text.split("next ", 1)[1] in WEEKDAYS:
        dt = _next_weekday(WEEKDAYS[text.split('next ', 1)[1]], now) + timedelta(days=7)
        return dt.replace(hour=23, minute=59, second=59, microsecond=0)

    iso_candidate = text.replace("z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_candidate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass

    numeric_match = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?$", text)
    if numeric_match:
        day, month, year = numeric_match.groups()
        day = int(day)
        month = int(month)
        year = int(year) if year else now.year
        if year < 100:
            year += 2000
        return datetime(year, month, day, 23, 59, 59, tzinfo=timezone.utc)

    month_match = re.match(r"^(\d{1,2})\s+([a-zA-Z]+)(?:\s+(\d{2,4}))?$", text)
    if month_match:
        day, month_name, year = month_match.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            year = int(year) if year else now.year
            if year < 100:
                year += 2000
            return datetime(year, month, int(day), 23, 59, 59, tzinfo=timezone.utc)

    return None


def compute_action_status(deadline: str | None, current_status: str, now: datetime | None = None) -> str:
    if current_status == "completed":
        return "completed"
    parsed = parse_deadline(deadline, now=now)
    if parsed and parsed < (now or datetime.now(timezone.utc)):
        return "overdue"
    return "pending"
