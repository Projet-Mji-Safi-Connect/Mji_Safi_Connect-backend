from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api.v1 import endpoints

app = FastAPI(title="Smart Poubelle Backend", version="1.0.0")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(endpoints.router, prefix="/api/v1", tags=["v1"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Poubelle API"}
