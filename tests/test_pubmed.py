import pytest
from src.pubmed import PubMedAdvancedSearch, PubMedSearchError
from src.schemas import SearchCriteria, PublicationType, Language, SearchField, SortBy

def test_search_criteria_validation():
    """検索条件のバリデーションテスト"""
    # 正常系
    criteria = SearchCriteria(
        keywords="COVID-19 treatment",
        publication_types=[PublicationType.META_ANALYSIS],
        start_year=2022,
        languages=[Language.ENGLISH],
        search_fields=[SearchField.TITLE, SearchField.ABSTRACT],
        max_results=10,
        sort_by=SortBy.DATE
    )
    assert criteria.keywords == "COVID-19 treatment"
    assert criteria.start_year == 2022
    assert criteria.max_results == 10

    # 異常系: 不正な年
    with pytest.raises(ValueError):
        SearchCriteria(keywords="test", start_year=3000)

def test_pubmed_search():
    """PubMed検索機能のテスト"""
    searcher = PubMedAdvancedSearch()
    criteria = SearchCriteria(
        keywords="COVID-19",
        publication_types=[PublicationType.META_ANALYSIS],
        start_year=2023,
        languages=[Language.ENGLISH],
        max_results=5
    )
    
    results = searcher.search_papers(criteria)
    assert len(results) <= 5
    for article in results:
        assert article.pmid is not None
        assert article.title is not None
        assert article.publication_date.year >= 2023

def test_pubmed_search_error_handling():
    """PubMed検索のエラーハンドリングテスト"""
    searcher = PubMedAdvancedSearch()
    
    # 空のキーワード
    with pytest.raises(PubMedSearchError):
        criteria = SearchCriteria(keywords="", max_results=5)
        searcher.search_papers(criteria)
    
    # 不正な最大結果数
    with pytest.raises(ValueError):
        criteria = SearchCriteria(keywords="test", max_results=0)
        searcher.search_papers(criteria)

def test_progress_callback():
    """進捗コールバックのテスト"""
    progress_calls = []
    def progress_callback(current: int, total: int):
        progress_calls.append((current, total))
    
    searcher = PubMedAdvancedSearch()
    criteria = SearchCriteria(
        keywords="COVID-19",
        max_results=3
    )
    
    searcher.search_papers(criteria, progress_callback=progress_callback)
    assert len(progress_calls) > 0
    for current, total in progress_calls:
        assert current <= total 