from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.repositories.quote_repository import QuoteRepository, UnknownProductIdError
from app.schemas.quote import QuoteCreate, Status


class QuoteService:
    def __init__(self):
        self.quote_repository = QuoteRepository()

    def get_quotes(self):
        return self.quote_repository.get_quotes()

    def get_by_page(self, after: str | None, limit: int):
        items, has_more = self.quote_repository.get_by_cursor(after, limit)
        next_cursor = items[-1]["id"] if has_more else None

        return {
            "data": items,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }

    def get_by_id(self, quote_id: str):
        quote = self.quote_repository.get_by_id(quote_id)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found"
            )
        return quote

    def create_quote(self, quote: QuoteCreate):
        existing_quotes = self.quote_repository.get_quotes()
        now = datetime.now(timezone.utc)
        quote_document = {
            "id": f"Q{len(existing_quotes) + 1:03d}",
            "status": Status.new.value,
            "product_id": quote.product_id,
            "applicant": quote.applicant.model_dump(mode="json"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            return self.quote_repository.save_quote(quote_document)
        except UnknownProductIdError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown product_id: {exc.product_id}",
            ) from exc

    def update_quote(self, quote_id: str, quote: QuoteCreate):
        try:
            updated_quote = self.quote_repository.update_quote(
                quote_id, quote.model_dump(mode="json")
            )
        except UnknownProductIdError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown product_id: {exc.product_id}",
            ) from exc
        if not updated_quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found"
            )
        return updated_quote

    def delete_quote(self, quote_id: str) -> None:
        if not self.quote_repository.delete_quote(quote_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found"
            )

    def search_quotes(self, name: str | None = None, category: str | None = None):
        return self.quote_repository.search_quotes(name=name, category=category)
