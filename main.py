from fastapi import Depends, FastAPI

from pybackend.app.api.routes.quotes_router import router as quotes_api_router
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

app = FastAPI()
app.include_router(quotes_api_router)

# Creates all the tables from quote_models in postgres
models.Base.metadata.create_all(bind=engine)

# Initialize the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency Injection
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
def get_root():
    return {"message": "Hello World!"}
