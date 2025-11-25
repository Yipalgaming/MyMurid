from datetime import datetime, timezone, timedelta

# Centralized Malaysia time zone (GMT+8) helpers to avoid duplicated literals
MYT = timezone(timedelta(hours=8))


def now_myt():
    """Return the current timezone-aware datetime in GMT+8."""
    return datetime.now(MYT)

