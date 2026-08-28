from fastapi import APIRouter, Query, status

from app.schemas.quote import QuoteCreate, QuoteCursorPage, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["Quotes"])

# Get ALL Quotes
@router.get("/", response_model=list[QuoteResponse])
async def get_quotes():
    return QuoteService().get_quotes()

# Search Quotes
@router.get("/search", response_model=list[QuoteResponse])
async def search_quotes(name: str | None = None, category: str | None = None):
    return QuoteService().search_quotes(name=name, category=category)

# Implementing Keyset (Cursor) Pagination
@router.get("/page", response_model=QuoteCursorPage)
async def get_by_page(
    after: str | None = Query(None), limit: int = Query(10, ge=1, le=50)
):
    return QuoteService().get_by_page(after, limit)

# Get Quote by ID
@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_by_id(quote_id: str):
    return QuoteService().get_by_id(quote_id)

# Create a new Quote
@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(quote: QuoteCreate):
    return QuoteService().create_quote(quote)

# Update an existing Quote
@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(quote_id: str, quote: QuoteCreate):
    return QuoteService().update_quote(quote_id, quote)

# Delete a Quote
@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(quote_id: str):
    QuoteService().delete_quote(quote_id)
