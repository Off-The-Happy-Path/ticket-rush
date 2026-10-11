"""ticket-rush: a concert-ticketing API for load-testing demos."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.errors import AppError, app_error_handler
from app.routes import admin, events, health, orders, reservations
from app.seed import load_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_seed()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="ticket-rush", version="0.1.0", lifespan=lifespan)
    app.add_exception_handler(AppError, app_error_handler)

    app.include_router(events.router)
    app.include_router(reservations.router)
    app.include_router(orders.router)
    app.include_router(health.router)
    if settings.admin_enabled:
        app.include_router(admin.router, include_in_schema=False)
    return app


app = create_app()
