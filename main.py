from fastapi import FastAPI

from app.api.routes.questions_router import router as answers_api_router
from app.api.routes.quotes_router import router as quotes_api_router
from app.database.database import Base, engine
from app.models import quote_model  # noqa: F401 - registers models on Base

app = FastAPI()
app.include_router(quotes_api_router)
app.include_router(answers_api_router)

# Creates all the tables from quote_model in postgres
Base.metadata.create_all(bind=engine)

@app.get("/")
def get_root():
    return {"message": "Hello World!"}
