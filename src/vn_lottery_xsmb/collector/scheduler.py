from __future__ import annotations

from datetime import date, timedelta


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def iter_dates(start_date: date, end_date: date) -> list[date]:
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")
    return [start_date + timedelta(days=offset) for offset in range((end_date - start_date).days + 1)]


def resolve_collection_dates(
    date_value: str | None,
    start_date: str | None,
    end_date: str | None,
) -> list[date]:
    if date_value:
        return [parse_date(date_value)]
    if not start_date or not end_date:
        raise ValueError("provide --date or both --start-date and --end-date")
    return iter_dates(parse_date(start_date), parse_date(end_date))
