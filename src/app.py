from fastapi import FastAPI, HTTPException, Depends
import httpx
import xml.etree.ElementTree as ET
from scheme import SearchRequest, FavoriteArticle
from search import construct_search_query
from llm import summarize_abstract, analyze_abstract
from auth import get_current_user
import json

app = FastAPI()


@app.post("/search")
async def search_pubmed(request: SearchRequest, current_user: str = Depends(get_current_user)):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    query = construct_search_query(request)
    
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={request.max_results}&retmode=xml"
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="PubMed search failed")
    
    root = ET.fromstring(response.text)
    pmids = [id_elem.text for id_elem in root.findall(".//Id")]
    
    results = []
    for pmid in pmids:
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
        async with httpx.AsyncClient() as client:
            response = await client.get(fetch_url)
        
        if response.status_code != 200:
            continue
        
        article = ET.fromstring(response.text).find(".//Article")
        if article is None:
            continue
        
        title = article.find(".//ArticleTitle").text
        abstract = article.find(".//Abstract/AbstractText")
        abstract_text = abstract.text if abstract is not None else "No abstract available"
        
        summary = summarize_abstract(abstract_text)
        
        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract_text,
            "summary": summary
        })
    
    return {"results": results}


@app.post("/analyze")
async def analyze_abstract_endpoint(abstract: str, current_user: str = Depends(get_current_user)):
    analysis = analyze_abstract(abstract)
    return {"analysis": analysis}


@app.post("/save_favorite")
async def save_favorite(article: FavoriteArticle, current_user: str = Depends(get_current_user)):
    # 実際のアプリケーションではデータベースに保存します
    # ここでは簡易的にファイルに保存します
    with open("favorites.json", "a") as f:
        json.dump(article.dict(), f)
        f.write("\n")
    return {"message": "Article saved to favorites"}


@app.get("/favorites")
async def get_favorites(current_user: str = Depends(get_current_user)):
    # 実際のアプリケーションではデータベースから取得します
    favorites = []
    with open("favorites.json", "r") as f:
        for line in f:
            favorites.append(json.loads(line))
    return {"favorites": favorites}