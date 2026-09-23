from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
