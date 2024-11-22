from __future__ import annotations
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import json
from enum import Enum
from pydantic import BaseModel, Field, field_validator, HttpUrl
from pathlib import Path
from typing import Callable

class SearchField(str, Enum):
    ALL = "All Fields"
    TITLE = "Title"
    ABSTRACT = "Abstract"
    AUTHOR = "Author"
    JOURNAL = "Journal"
    MESH_TERMS = "MeSH Terms"
    AFFILIATION = "Affiliation"

class Language(str, Enum):
    ENGLISH = "english"
    JAPANESE = "japanese"
    FRENCH = "french"
    GERMAN = "german"
    CHINESE = "chinese"
    SPANISH = "spanish"

class SortBy(str, Enum):
    RELEVANCE = "relevance"
    DATE = "date"
    JOURNAL = "journal"

class PublicationType(str, Enum):
    META_ANALYSIS = "Meta-Analysis"
    SYSTEMATIC_REVIEW = "Systematic Review"
    CLINICAL_TRIAL = "Clinical Trial"
    CLINICAL_TRIAL_PHASE_1 = "Clinical Trial, Phase I"
    CLINICAL_TRIAL_PHASE_2 = "Clinical Trial, Phase II"
    CLINICAL_TRIAL_PHASE_3 = "Clinical Trial, Phase III"
    CLINICAL_TRIAL_PHASE_4 = "Clinical Trial, Phase IV"
    RANDOMIZED_CONTROLLED_TRIAL = "Randomized Controlled Trial"
    PRACTICE_GUIDELINE = "Practice Guideline"
    REVIEW = "Review"

class Author(BaseModel):
    last_name: str = Field(..., min_length=1)
    fore_name: str | None = None
    affiliation: str | None = None

class PublicationDate(BaseModel):
    year: int | None = Field(None, ge=1800, le=datetime.now().year)
    month: int | None = Field(None, ge=1, le=12)
    day: int | None = Field(None, ge=1, le=31)

class MeshTerm(BaseModel):
    descriptor: str
    qualifiers: list[str] = Field(default_factory=list)

class SearchCriteria(BaseModel):
    keywords: str = Field(..., min_length=2)
    publication_types: list[PublicationType] = Field(default_factory=list)
    mesh_terms: list[str] = Field(default_factory=list)
    start_year: int | None = Field(None, ge=1800, le=datetime.now().year)
    end_year: int | None = Field(None, ge=1800, le=datetime.now().year)
    languages: list[Language] = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    journals: list[str] = Field(default_factory=list)
    search_fields: list[SearchField] = Field(default_factory=list)
    affiliations: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    min_citations: int | None = Field(None, ge=0)
    free_full_text: bool = False
    humans_only: bool = False
    max_results: int = Field(100, gt=0, le=10000)
    sort_by: SortBy = SortBy.RELEVANCE
    include_mesh_subheadings: bool = False

    @field_validator('end_year')
    def end_year_must_be_after_start_year(cls, v: int | None, info) -> int | None:
        if v is not None and info.data.get('start_year') is not None:
            if v < info.data['start_year']:
                raise ValueError('end_year must be greater than or equal to start_year')
        return v

    @field_validator('mesh_terms')
    def mesh_terms_must_be_valid(cls, v: list[str], info) -> list[str]:
        if v:
            for term in v:
                if len(term.strip()) < 2:
                    raise ValueError('MeSH terms must be at least 2 characters long')
        return v

class ArticleResponse(BaseModel):
    pmid: str
    title: str
    abstract: str = Field(default="Abstract not available")
    authors: list[Author]
    mesh_terms: list[MeshTerm] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    doi: str | None = None
    journal: str
    journal_abbrev: str | None = None
    publication_date: PublicationDate
    url: HttpUrl | None = None
    citation_count: int = 0

    @field_validator('pmid')
    def pmid_must_be_numeric(cls, v: str, info) -> str:
        if not v.isdigit():
            raise ValueError('PMID must contain only digits')
        return v

class PubMedSearchError(Exception):
    """PubMed検索に関連するエラー"""
    pass

class PubMedAdvancedSearch:
    def __init__(self, api_key: str | None = None):
        """
        PubMed検索クラスの初期化
        
        Parameters:
        -----------
        api_key : str | None
            NCBI E-utilities API key
            - リクエスト制限: APIキーあり=10req/sec, なし=3req/sec
            - 取得方法: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.api_key = api_key
        self._last_request_time = 0
        self._rate_limit = 0.1 if api_key else 0.34  # 10 req/sec or 3 req/sec

    def _wait_for_rate_limit(self):
        """リクエスト制限を遵守するための待機"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self._rate_limit:
            time.sleep(self._rate_limit - time_since_last_request)
        self._last_request_time = time.time()

    def _make_request(self, endpoint: str, params: dict) -> requests.Response:
        """レート制限を考慮したリクエスト実行"""
        self._wait_for_rate_limit()
        url = f"{self.base_url}/{endpoint}"
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise PubMedSearchError(f"API request failed: {str(e)}")

    def _build_search_query(self, criteria: SearchCriteria) -> str:
        """検索クエリの構築"""
        query_parts = []
        
        # キーワード検索（フィールド指定あり）
        if criteria.search_fields:
            field_queries = []
            for field in criteria.search_fields:
                if field == SearchField.MESH_TERMS:
                    continue
                field_queries.append(f"{criteria.keywords}[{field.value}]")
            query_parts.append(f"({' OR '.join(field_queries)})")
        else:
            query_parts.append(f"({criteria.keywords})")
        
        # 除外キーワード
        if criteria.exclude_keywords:
            exclude_query = " OR ".join([f'"{keyword}"' for keyword in criteria.exclude_keywords])
            query_parts.append(f"NOT ({exclude_query})")
        
        # MeSH用語
        if criteria.mesh_terms:
            mesh_queries = []
            for term in criteria.mesh_terms:
                if criteria.include_mesh_subheadings:
                    mesh_queries.append(f'"{term}"[MeSH Terms:noexp]')
                else:
                    mesh_queries.append(f'"{term}"[MeSH Terms]')
            query_parts.append(f"({' OR '.join(mesh_queries)})")
        
        # Publication type
        if criteria.publication_types:
            pub_types = [f'"{pt.value}"[Publication Type]' for pt in criteria.publication_types]
            query_parts.append(f"({' OR '.join(pub_types)})")
        
        # 著者
        if criteria.authors:
            authors = [f'"{author}"[Author]' for author in criteria.authors]
            query_parts.append(f"({' OR '.join(authors)})")
        
        # ジャーナル
        if criteria.journals:
            journals = [f'"{journal}"[Journal]' for journal in criteria.journals]
            query_parts.append(f"({' OR '.join(journals)})")
        
        # 所属機関
        if criteria.affiliations:
            affiliations = [f'"{affiliation}"[Affiliation]' for affiliation in criteria.affiliations]
            query_parts.append(f"({' OR '.join(affiliations)})")
        
        # 言語
        if criteria.languages:
            languages = [f"{lang.value}[Language]" for lang in criteria.languages]
            query_parts.append(f"({' OR '.join(languages)})")
        
        # 年範囲
        if criteria.start_year or criteria.end_year:
            current_year = datetime.now().year
            start = criteria.start_year if criteria.start_year else 1800
            end = criteria.end_year if criteria.end_year else current_year
            query_parts.append(f"({start}:{end}[Date - Publication])")
        
        # フリーフルテキスト
        if criteria.free_full_text:
            query_parts.append("free full text[sb]")
        
        # ヒト研究のみ
        if criteria.humans_only:
            query_parts.append("\"Humans\"[MeSH Terms]")
        
        return " AND ".join(query_parts)

    def search_papers(
        self, 
        criteria: SearchCriteria,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> list[ArticleResponse]:
        """
        論文検索の実行
        
        Parameters:
        -----------
        criteria : SearchCriteria
            検索条件
        progress_callback : Callable[[int, int], None] | None
            進捗コールバック関数 (current, total) -> None
            
        Returns:
        --------
        list[ArticleResponse]
            検索結果の論文リスト
        """
        search_query = self._build_search_query(criteria)
        
        # 検索実行（PMIDの取得）
        search_params = {
            "db": "pubmed",
            "term": search_query,
            "retmax": criteria.max_results,
            "retmode": "xml",
            "usehistory": "y",
            "sort": criteria.sort_by
        }
        
        try:
            response = self._make_request("esearch.fcgi", search_params)
            search_tree = ET.fromstring(response.content)
            
            # 検索結果件数の確認
            count_elem = search_tree.find(".//Count")
            if count_elem is None or count_elem.text == "0":
                return []
                
            total_results = min(int(count_elem.text), criteria.max_results)
            
            pmids = [id_elem.text for id_elem in search_tree.findall(".//Id")]
            if not pmids:
                return []

            # 論文詳細の取得
            results: list[ArticleResponse] = []
            batch_size = 100
            
            for i in range(0, len(pmids), batch_size):
                if progress_callback:
                    progress_callback(i, total_results)
                    
                batch_pmids = pmids[i:i + batch_size]
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(batch_pmids),
                    "retmode": "xml"
                }
                
                response = self._make_request("efetch.fcgi", fetch_params)
                batch_results = self._parse_articles(response.content)
                
                # 被引用数の取得（もし必要な場合）
                if criteria.min_citations is not None:
                    for article in batch_results:
                        article.citation_count = self._get_citation_count(article.pmid)
                        if article.citation_count < criteria.min_citations:
                            continue
                        results.append(article)
                else:
                    results.extend(batch_results)

            if progress_callback:
                progress_callback(total_results, total_results)

            return results
            
        except ET.ParseError as e:
            raise PubMedSearchError(f"Failed to parse XML response: {str(e)}")
        except Exception as e:
            raise PubMedSearchError(f"Search failed: {str(e)}")

    def _get_citation_count(self, pmid: str) -> int:
        """PMIDに基づいて論文の被引用数を取得"""
        try:
            params = {
                "db": "pubmed",
                "id": pmid,
                "cmd": "citedby",
                "retmode": "json"
            }
            response = self._make_request("elink.fcgi", params)
            data = response.json()
            return len(data.get("linksets", [{}])[0].get("linksetdbs", [{}])[0].get("links", []))
        except Exception:
            return 0

    def _parse_articles(self, content: bytes) -> list[ArticleResponse]:
        """XMLレスポンスからArticleResponseオブジェクトのリストを生成"""
        tree = ET.fromstring(content)
        articles: list[ArticleResponse] = []
        
        for article_elem in tree.findall(".//PubmedArticle"):
            try:
                article_data = self._extract_article_data(article_elem)
                article = ArticleResponse(**article_data)
                articles.append(article)
            except Exception as e:
                pmid = article_elem.find(".//PMID")
                pmid_text = pmid.text if pmid is not None else "unknown"
                print(f"Error processing article {pmid_text}: {str(e)}")
                
        return articles

    def _extract_article_data(self, article: ET.Element) -> dict:
        """論文要素から詳細データを抽出"""
        # PMID
        pmid = article.find(".//PMID").text
        
        # タイトル
        title_elem = article.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "Title not available"
        
        # アブストラクト
        abstract = self._extract_abstract(article)
        
        # 著者リスト
        authors = self._extract_authors(article)
        
        # MeSH用語
        mesh_terms = self._extract_mesh_terms(article)
        
        # キーワード
        keywords = [keyword.text for keyword in article.findall(".//Keyword") if keyword.text]
        
        # DOI
        doi_elem = article.find(".//ArticleId[@IdType='doi']")
        doi = doi_elem.text if doi_elem is not None else None
        
        # ジャーナル情報
        journal_elem = article.find(".//Journal")
        if journal_elem is not None:
            journal_title = journal_elem.find("Title")
            journal_abbrev = journal_elem.find("ISOAbbreviation")
            journal = journal_title.text if journal_title is not None else "Journal not available"
            journal_abbrev_text = journal_abbrev.text if journal_abbrev is not None else None
        else:
            journal = "Journal not available"
            journal_abbrev_text = None
        
        # 出版日
        publication_date = self._extract_publication_date(article)
        
        # PubMed URL
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
        
        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "mesh_terms": mesh_terms,
            "keywords": keywords,
            "doi": doi,
            "journal": journal,
            "journal_abbrev": journal_abbrev_text,
            "publication_date": publication_date,
            "url": url
        }

    def _extract_abstract(self, article: ET.Element) -> str:
        """構造化アブストラクトを含むアブストラクトを抽出"""
        abstract_texts = []
        
        for abstract_elem in article.findall(".//Abstract/AbstractText"):
            label = abstract_elem.get("Label", "")
            text = abstract_elem.text or ""
            
            if label:
                abstract_texts.append(f"{label}: {text}")
            else:
                abstract_texts.append(text)
        
        if not abstract_texts:
            return "Abstract not available"
            
        return "\n".join(abstract_texts)

    def _extract_authors(self, article: ET.Element) -> list[dict]:
        """著者情報を抽出"""
        authors = []
        
        for author_elem in article.findall(".//Author"):
            last_name = author_elem.find("LastName")
            fore_name = author_elem.find("ForeName")
            affiliation = author_elem.find(".//Affiliation")
            
            if last_name is not None:
                author_data = {
                    "last_name": last_name.text,
                    "fore_name": fore_name.text if fore_name is not None else None,
                    "affiliation": affiliation.text if affiliation is not None else None
                }
                authors.append(author_data)
        
        return authors

    def _extract_mesh_terms(self, article: ET.Element) -> list[dict]:
        """MeSH用語を抽出"""
        mesh_terms = []
        
        for mesh_elem in article.findall(".//MeshHeading"):
            descriptor = mesh_elem.find("DescriptorName")
            qualifiers = [q.text for q in mesh_elem.findall("QualifierName")]
            
            if descriptor is not None:
                mesh_terms.append({
                    "descriptor": descriptor.text,
                    "qualifiers": qualifiers
                })
        
        return mesh_terms

    def _extract_publication_date(self, article: ET.Element) -> dict:
        """出版日情報を抽出"""
        pub_date = article.find(".//PubDate")
        if pub_date is None:
            return {"year": None, "month": None, "day": None}
        
        date_dict = {}
        
        # 年の取得
        year = pub_date.find("Year")
        date_dict["year"] = int(year.text) if year is not None else None
        
        # 月の取得
        month = pub_date.find("Month")
        if month is not None:
            try:
                # 月名を数値に変換（例: "Jan" → 1）
                month_text = month.text.lower()
                month_map = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                    "may": 5, "jun": 6, "jul": 7, "aug": 8,
                    "sep": 9, "oct": 10, "nov": 11, "dec": 12
                }
                date_dict["month"] = month_map.get(month_text[:3], int(month_text))
            except (ValueError, AttributeError):
                date_dict["month"] = None
        else:
            date_dict["month"] = None
        
        # 日の取得
        day = pub_date.find("Day")
        date_dict["day"] = int(day.text) if day is not None else None
        
        return date_dict

    def save_results(self, results: list[ArticleResponse], file_path: str | Path):
        """検索結果をJSONファイルとして保存"""
        if not results:
            return
            
        file_path = Path(file_path)
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(
                [article.dict() for article in results],
                f,
                ensure_ascii=False,
                indent=2
            )

def example_usage():
    """使用例"""
    try:
        searcher = PubMedAdvancedSearch()

        criteria = SearchCriteria(
            keywords="COVID-19 treatment",
            publication_types=[
                PublicationType.META_ANALYSIS,
                PublicationType.SYSTEMATIC_REVIEW
            ],
            start_year=2022,
            languages=[Language.ENGLISH],
            search_fields=[SearchField.TITLE, SearchField.ABSTRACT],
            journals=[
                "Lancet",
                "N Engl J Med",
                "JAMA",
                "Nat Med",
                "BMJ"
            ],
            max_results=10,
            sort_by=SortBy.DATE
        )

        def show_progress(current: int, total: int):
            print(f"Searching... {current}/{total}")

        results = searcher.search_papers(criteria, progress_callback=show_progress)

        print(f"\nFound {len(results)} papers")
        
        for article in results:
            print("\n" + "="*100)
            print(f"Title: {article.title}")
            print(f"Authors: {', '.join([f'{a.fore_name} {a.last_name}' for a in article.authors])}")
            print(f"Journal: {article.journal}")
            print(f"Publication Date: {article.publication_date.year}-{article.publication_date.month}")
            print(f"PMID: {article.pmid}")
            print(f"URL: {article.url}")
            print(f"Citations: {article.citation_count}")
            print("\nAbstract:")
            print(f"{article.abstract}")
            print("\nMeSH Terms:")
            for term in article.mesh_terms:
                print(f"- {term.descriptor}")
            print("="*100 + "\n")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    example_usage()