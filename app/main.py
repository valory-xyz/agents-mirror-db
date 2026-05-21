"""FastAPI application entrypoint that mounts the API router and bootstraps the DB."""

import time

from fastapi import FastAPI

from .api import endpoints
from .db.database import init_db

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    """Sleep briefly to let the DB container come up, then create tables."""
    time.sleep(20)
    init_db()


app.include_router(endpoints.router)
