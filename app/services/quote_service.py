from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.repositories.quote_repository import QuoteRepository
from app.schemas.quote import QuoteCreate, Status


class QuoteService:
    def __init__(self):
        self.quote_repository = QuoteRepository()

    def get_quotes(self):
        return self.quote_repository.get_quotes()

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
            "product_type": quote.product_type.value,
            "applicant": quote.applicant.model_dump(mode="json"),
            "answers": [answer.model_dump() for answer in quote.answers],
            "premium": None,
            "policy_id": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        return self.quote_repository.save_quote(quote_document)

    def update_quote(self, quote_id: str, quote: QuoteCreate):
        updated_quote = self.quote_repository.update_quote(
            quote_id, quote.model_dump(mode="json")
        )
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
