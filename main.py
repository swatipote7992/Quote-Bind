from fastapi import FastAPI

from pybackend.app.api.routes.quotes_json import router as quotes_json_router
from pybackend.app.api.routes.quotes_router import router as quotes_api_router
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
app.include_router(quotes_json_router)
app.include_router(quotes_api_router)

# Creates all the tables from quote_models in postgres
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def get_root():
    return {"message": "Hello World!"}
