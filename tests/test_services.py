import pytest
from src.services import ArticleGenerator, ArticleGenerationError
from src.schemas import ArticleResponse, PublicationDate, ArticleAuthor, ArticleMeshTerm

def test_article_generation(sample_article_response):
    """記事生成機能のテスト"""
    generator = ArticleGenerator()
    
    # テスト用の検索結果を作成
    article = ArticleResponse(**sample_article_response)
    search_results = [article]
    
    # 記事生成
    generated_article = generator.generate_article(search_results)
    
    # 生成された記事の検証
    assert generated_article.title is not None
    assert generated_article.content is not None
    assert generated_article.summary is not None
    assert len(generated_article.keywords) > 0
    assert len(generated_article.source_articles) == 1
    assert generated_article.source_articles[0] == sample_article_response["pmid"]

def test_article_generation_error_handling():
    """記事生成のエラーハンドリングテスト"""
    generator = ArticleGenerator()
    
    # 空の検索結果
    with pytest.raises(ArticleGenerationError):
        generator.generate_article([])
    
    # アブストラクトのない論文
    article_without_abstract = ArticleResponse(
        pmid="12345",
        title="Test",
        abstract="",
        authors=[],
        mesh_terms=[],
        keywords=[],
        publication_date=PublicationDate()
    )
    
    # アブストラクトがない場合でもエラーにはならないが、要約は空になる
    article = generator.generate_article([article_without_abstract])
    assert article.summary == ""

def test_content_formatting():
    """コンテンツフォーマットのテスト"""
    generator = ArticleGenerator()
    
    # テスト用の検索結果を作成
    article = ArticleResponse(
        pmid="12345",
        title="Test Article",
        abstract="Test abstract",
        authors=[
            ArticleAuthor(
                last_name="Smith",
                fore_name="John"
            )
        ],
        mesh_terms=[
            ArticleMeshTerm(
                descriptor="Test Term"
            )
        ],
        keywords=["test"],
        journal="Test Journal",
        publication_date=PublicationDate(year=2024, month=1, day=1)
    )
    
    # 記事生成
    generated = generator.generate_article([article])
    
    # Markdownフォーマットの検証
    assert "# Literature Review" in generated.content
    assert "## 1. Test Article" in generated.content
    assert "**Authors**: John Smith" in generated.content
    assert "**Journal**: Test Journal (2024)" in generated.content
    assert "**PMID**: 12345" in generated.content 