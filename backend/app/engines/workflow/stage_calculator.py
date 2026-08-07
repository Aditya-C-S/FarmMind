"""
Stage Calculator
----------------
Pure date arithmetic: converts a sowing date + a reference date into
Days After Sowing (DAS).

Deliberately knows nothing about crops, stages, or JSON structure —
that separation is what lets it be tested in isolation before anything
else in the engine exists.
"""

from datetime import date, datetime
from typing import Union

DateLike = Union[date, datetime, str]


def _to_date(value: DateLike) -> date:
    """Normalize a date, datetime, or ISO-format string ('YYYY-MM-DD') into a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError as e:
            raise ValueError(
                f"Could not parse date string '{value}'. Expected ISO format, e.g. '2026-06-15'."
            ) from e
    raise TypeError(f"Unsupported date type: {type(value)!r}")


def calculate_das(sowing_date: DateLike, today: DateLike = None) -> int:
    """
    Calculate Days After Sowing (DAS).

    Args:
        sowing_date: date the crop was sown/planted (date, datetime, or ISO string)
        today: reference date to calculate against. Defaults to the actual
               current date if not provided.

    Returns:
        Integer days elapsed since sowing. 0 on the sowing day itself.
        Clamped to 0 if `today` is somehow before `sowing_date` (e.g. bad
        data entry) rather than returning a negative number, since a
        negative DAS has no valid stage to resolve to.

    Examples:
        >>> calculate_das("2026-06-01", "2026-07-18")
        47
    """
    sowing = _to_date(sowing_date)
    reference = _to_date(today) if today is not None else date.today()

    delta_days = (reference - sowing).days
    return max(delta_days, 0)