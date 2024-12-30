from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ..schemas import SearchCriteria, ArticleResponse
from ..pubmed import PubMedAdvancedSearch, PubMedSearchError
from ..llm import summarize_abstract, analyze_abstract

router = APIRouter()

@router.post("/pubmed-search", response_model=list[ArticleResponse])
async def pubmed_search(
    criteria: SearchCriteria,
):
    """PubMed検索エンドポイント"""
    try:
        searcher = PubMedAdvancedSearch()
        results = searcher.search_papers(criteria)
        
        # 必要に応じて各論文の要約と分析を追加
        for article in results:
            if article.abstract:
                article.summary = summarize_abstract(article.abstract)
                article.analysis = analyze_abstract(article.abstract)
        
        return results
    except PubMedSearchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
