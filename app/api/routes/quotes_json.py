from fastapi import APIRouter, status

from app.schemas.quote import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotesJson", tags=["Quotes"])

@router.get("/", response_model=list[QuoteResponse])
async def get_quotes():
    return QuoteService().get_quotes()


@router.get("/search", response_model=list[QuoteResponse])
async def search_quotes(name: str | None = None, category: str | None = None):
    return QuoteService().search_quotes(name=name, category=category)


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_by_id(quote_id: str):
    return QuoteService().get_by_id(quote_id)


@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(quote: QuoteCreate):
    return QuoteService().create_quote(quote)


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(quote_id: str, quote: QuoteCreate):
    return QuoteService().update_quote(quote_id, quote)


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(quote_id: str):
    QuoteService().delete_quote(quote_id)
