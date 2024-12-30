# project/schemas.py

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field

# Enum類の例。必要に応じてどこまで再現するか調整
from enum import Enum

class SearchField(str, Enum):
    TITLE = "ti"                    # タイトル
    ABSTRACT = "ab"                 # アブストラクト
    MESH_TERMS = "mh"              # MeSH用語
    AUTHOR = "au"                  # 著者
    JOURNAL = "ta"                 # ジャーナル名
    AFFILIATION = "ad"             # 所属機関
    ALL_FIELDS = "all"             # 全フィールド
    PUBLICATION_DATE = "dp"        # 出版日
    DOI = "doi"                    # DOI
    ISBN = "isbn"                  # ISBN
    VOLUME = "vi"                  # 巻
    ISSUE = "ip"                   # 号
    PAGINATION = "pg"              # ページ
    TEXT_WORD = "tw"              # テキストワード

class PublicationType(str, Enum):
    META_ANALYSIS = "Meta-Analysis"
    SYSTEMATIC_REVIEW = "Systematic Review"
    RANDOMIZED_CONTROLLED_TRIAL = "Randomized Controlled Trial"
    CLINICAL_TRIAL = "Clinical Trial"
    OBSERVATIONAL_STUDY = "Observational Study"
    REVIEW = "Review"
    CASE_REPORTS = "Case Reports"
    COMPARATIVE_STUDY = "Comparative Study"
    PRACTICE_GUIDELINE = "Practice Guideline"
    JOURNAL_ARTICLE = "Journal Article"
    EDITORIAL = "Editorial"
    LETTER = "Letter"
    COMMENT = "Comment"

class Language(str, Enum):
    ENGLISH = "eng"
    JAPANESE = "jpn"
    FRENCH = "fre"
    GERMAN = "ger"
    CHINESE = "chi"
    SPANISH = "spa"
    ITALIAN = "ita"
    RUSSIAN = "rus"
    KOREAN = "kor"
    PORTUGUESE = "por"

class SortBy(str, Enum):
    RELEVANCE = "relevance"        # 関連性
    DATE = "date"                  # 日付
    AUTHOR = "author"              # 著者
    JOURNAL = "journal"            # ジャーナル
    TITLE = "title"               # タイトル
    MOST_RECENT = "most_recent"    # 最新
    MOST_CITED = "most_cited"      # 被引用数

class StudyType(str, Enum):
    HUMAN = "humans"
    ANIMAL = "animals"
    MALE = "male"
    FEMALE = "female"
    INFANT = "infant"
    CHILD = "child"
    ADULT = "adult"
    AGED = "aged"

class SubsetType(str, Enum):
    MEDLINE = "medline"
    PUBMED_NOT_MEDLINE = "pubmed not medline"
    FREE_FULL_TEXT = "free full text"
    AHEAD_OF_PRINT = "ahead of print"
    IN_PROCESS = "in process"

# PubMed用の検索条件
class SearchCriteria(BaseModel):
    keywords: str
    search_fields: list[SearchField] | None = None
    exclude_keywords: list[str] | None = None
    mesh_terms: list[str] | None = None
    include_mesh_subheadings: bool = False
    publication_types: list[PublicationType] | None = None
    authors: list[str] | None = None
    journals: list[str] | None = None
    affiliations: list[str] | None = None
    languages: list[Language] | None = None
    start_year: int | None = None
    end_year: int | None = None
    free_full_text: bool = False
    humans_only: bool = False
    max_results: int = 100
    sort_by: SortBy = SortBy.RELEVANCE
    min_citations: int | None = None

# PubMedの検索結果を表すレスポンスモデル
class ArticleAuthor(BaseModel):
    last_name: str | None = None
    fore_name: str | None = None
    affiliation: str | None = None

class ArticleMeshTerm(BaseModel):
    descriptor: str | None = None
    qualifiers: list[str] | None = None

class PublicationDate(BaseModel):
    year: int | None = None
    month: int | None = None
    day: int | None = None

class ArticleResponse(BaseModel):
    pmid: str
    title: str
    abstract: str
    authors: list[ArticleAuthor] = []
    mesh_terms: list[ArticleMeshTerm] = []
    keywords: list[str] = []
    doi: str | None = None
    journal: str | None = None
    journal_abbrev: str | None = None
    publication_date: PublicationDate = PublicationDate()
    url: str | None = None
    citation_count: int = 0
    summary: str | None = None
    analysis: str | None = None

    # ほか必要ならフィールド追加

# 例: 記事生成後のレスポンスなど
class ArticleCreateResponse(BaseModel):
    id: int
    title: str
    content: str | None = None
    summary: str | None = None
    keywords: list[str] | None = None
    source_articles: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    user_id: int | None = None

    class Config:
        orm_mode = True
