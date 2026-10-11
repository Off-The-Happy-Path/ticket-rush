from datetime import datetime, timezone


def now() -> datetime:
    """Current UTC time, rounded to whole seconds so JSON stays readable."""
    return datetime.now(timezone.utc).replace(microsecond=0)
