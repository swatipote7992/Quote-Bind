import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "quote_data.json"


class QuoteRepository:

    def readJson(self) -> list[dict]:
        with DATA_FILE.open("r") as f:
            return json.load(f)

    def writeToJson(self, quotes: list[dict]) -> None:
        with DATA_FILE.open("w") as f:
            json.dump(quotes, f, indent=2)

    def get_quotes(self) -> list[dict]:
        if not DATA_FILE.exists() or not DATA_FILE.read_text().strip():
            return []
        return self.readJson()

    def get_by_id(self, quote_id: str) -> dict | None:
        quotes_list = self.get_quotes()
        for q in quotes_list:
            if q["id"] == quote_id:
                return q
        return None

    def save_quote(self, quote_document: dict) -> dict:
        quotes = self.get_quotes()
        quotes.append(quote_document)
        self.writeToJson(quotes)
        return quote_document

    def update_quote(self, quote_id: str, updates: dict) -> dict | None:
        quotes = self.get_quotes()
        existing_quote = self.get_by_id(quote_id)
        if existing_quote:
            existing_index = quotes.index(existing_quote)
            quotes[existing_index] = {**existing_quote, **updates}
            self.writeToJson(quotes)
            return quotes[existing_index]
        return None

    def delete_quote(self, quote_id: str) -> bool:
        quotes = self.get_quotes()
        filtered_quotes = [q for q in quotes if q["id"] != quote_id]
        if len(filtered_quotes) == len(quotes):
            return False
        self.writeToJson(filtered_quotes)
        return True

    def search_quotes(
        self, name: str | None = None, category: str | None = None
    ) -> list[dict]:
        quotes = self.get_quotes()
        if name:
            quotes = [q for q in quotes if name.lower() in q["name"].lower()]
        if category:
            quotes = [q for q in quotes if q["category"].lower() == category.lower()]
        return quotes
