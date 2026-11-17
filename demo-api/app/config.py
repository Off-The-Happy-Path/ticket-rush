"""Settings, read once from environment variables."""
import os
from dataclasses import dataclass


def _flag(name: str) -> bool:
    return os.getenv(name, "false").lower() in ("1", "true", "yes")


@dataclass
class Settings:
    oversell_bug: bool        # True = no seat lock, two fans can buy the same seat
    admin_enabled: bool       # True = mount /admin/reset, /admin/report and /admin/freeze
    hold_seconds: int         # how long a reservation holds a seat
    db_latency_ms: int        # simulated database round trip
    payment_latency_ms: int   # simulated payment provider call
    drop_response_after_commit_pct: int  # 0-100: % of successful POST /reservations and /orders whose response is never sent
    drop_seed: int            # makes the dropped requests reproducible
    drop_hold_seconds: float  # how long a dropped response is held before the server gives up


def load_settings() -> Settings:
    return Settings(
        oversell_bug=_flag("OVERSELL_BUG"),
        admin_enabled=_flag("ADMIN_ENABLED"),
        hold_seconds=int(os.getenv("HOLD_SECONDS", "300")),
        db_latency_ms=int(os.getenv("DB_LATENCY_MS", "50")),
        payment_latency_ms=int(os.getenv("PAYMENT_LATENCY_MS", "200")),
        drop_response_after_commit_pct=max(0, min(100, int(os.getenv("DROP_RESPONSE_AFTER_COMMIT_PCT", "0")))),
        drop_seed=int(os.getenv("DROP_SEED", "0")),
        drop_hold_seconds=float(os.getenv("DROP_HOLD_SECONDS", "5")),
    )


settings = load_settings()
