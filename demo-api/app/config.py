"""Settings, read once from environment variables."""
import os
from dataclasses import dataclass


def _flag(name: str) -> bool:
    return os.getenv(name, "false").lower() in ("1", "true", "yes")


@dataclass
class Settings:
    oversell_bug: bool        # True = no seat lock, two fans can buy the same seat
    admin_enabled: bool       # True = mount /admin/reset and /admin/report
    hold_seconds: int         # how long a reservation holds a seat
    db_latency_ms: int        # simulated database round trip
    payment_latency_ms: int   # simulated payment provider call


def load_settings() -> Settings:
    return Settings(
        oversell_bug=_flag("OVERSELL_BUG"),
        admin_enabled=_flag("ADMIN_ENABLED"),
        hold_seconds=int(os.getenv("HOLD_SECONDS", "300")),
        db_latency_ms=int(os.getenv("DB_LATENCY_MS", "50")),
        payment_latency_ms=int(os.getenv("PAYMENT_LATENCY_MS", "200")),
    )


settings = load_settings()
