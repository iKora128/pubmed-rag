from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import init_db
from .routers import pubmed_search, article

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# ルーターを登録
app.include_router(pubmed_search.router, prefix="/api", tags=["PubMed Search"])
app.include_router(article.router, prefix="/api", tags=["Article"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)