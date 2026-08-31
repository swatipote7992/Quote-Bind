import logging

from fastapi import FastAPI
from app.api.routes.products_router import router as products_api_router
from app.api.routes.questions_router import router as questions_api_router
from app.api.routes.quotes_router import router as quotes_api_router

from app.database.database import Base, engine
from app.models import quote_model  # noqa: F401 - registers models on Base
from app.api.exception_handlers import register_exception_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI()

# Register exception handler
register_exception_handler(app)

# Register Routers
app.include_router(quotes_api_router)
app.include_router(questions_api_router)
app.include_router(products_api_router)

# Creates all the tables from quote_model in postgres
Base.metadata.create_all(bind=engine)

# Root Endpoints for testing
@app.get("/")
def get_root():
    return {"message": "Get Successful!"}


@app.post("/")
def post_root():
    return {"message": "Post Successful!"}


@app.put("/")
def put_root():
    return {"message": "Put Successful!"}

@app.delete("/")
def delete_root():
    return {"message": "Delete Successful!"}