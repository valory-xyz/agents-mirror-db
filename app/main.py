from fastapi import FastAPI
from .db.database import init_db
from .api import endpoints
from .middleware import LogRequestMiddleware
import time

app = FastAPI()

@app.on_event("startup")
def on_startup():
    time.sleep(20)
    init_db()

# app.add_middleware(LogRequestMiddleware)

app.include_router(endpoints.router)