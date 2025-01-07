from fastapi import FastAPI
from .db.database import init_db
from .api import endpoints

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(endpoints.router)