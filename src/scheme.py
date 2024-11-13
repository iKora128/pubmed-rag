from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    journal: str | None = None
    author: str | None = None
    date_range: str | None = None
    evidence_level: str | None = None

class FavoriteArticle(BaseModel):
    pmid: str
    title: str