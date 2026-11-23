from app.models import Sex


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def to_int_or_none(value: str | None) -> int | None:
    stripped = blank_to_none(value)
    if stripped is None:
        return None
    try:
        return int(stripped)
    except ValueError:
        return None


def to_sex_or_none(value: str | None) -> Sex | None:
    stripped = blank_to_none(value)
    if stripped is None:
        return None
    try:
        return Sex(stripped.upper())
    except ValueError:
        return None
