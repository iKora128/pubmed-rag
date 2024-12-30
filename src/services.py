# project/services.py

from .schemas import ArticleResponse
from .models import Article
from openai import OpenAI
from .llm import summarize_abstract, analyze_abstract
import os

class ArticleGenerationError(Exception):
    """記事生成に関連するエラー"""
    pass

class ArticleGenerator:
    """PubMed検索結果から記事を生成するクラス"""
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_article(self, search_results: list[ArticleResponse]) -> Article:
        """検索結果から記事を生成"""
        if not search_results:
            raise ArticleGenerationError("検索結果が空です")
        
        try:
            # 記事のメタデータを準備
            source_articles = [result.pmid for result in search_results]
            keywords = set()
            for result in search_results:
                keywords.update(result.keywords or [])

            # 各論文の要約と分析を生成
            summaries = []
            analyses = []
            for result in search_results:
                if result.abstract:
                    summary = summarize_abstract(result.abstract)
                    analysis = analyze_abstract(result.abstract)
                    summaries.append(summary)
                    analyses.append(analysis)

            # 記事を生成
            article = Article(
                title=f"Literature Review: {search_results[0].mesh_terms[0].descriptor if search_results[0].mesh_terms else 'Medical Research'}",
                content=self._format_content(search_results, summaries, analyses),
                summary="\n\n".join(summaries),
                keywords=list(keywords),
                source_articles=source_articles
            )
            
            return article
            
        except Exception as e:
            raise ArticleGenerationError(f"記事生成中にエラーが発生しました: {str(e)}")

    def _format_content(self, results: list[ArticleResponse], summaries: list[str], analyses: list[str]) -> str:
        """記事コンテンツをフォーマット"""
        content_parts = ["# Literature Review\n\n"]
        
        for i, (result, summary, analysis) in enumerate(zip(results, summaries, analyses)):
            content_parts.extend([
                f"## {i+1}. {result.title}\n",
                f"**Authors**: {', '.join([f'{a.fore_name} {a.last_name}' for a in result.authors])}\n",
                f"**Journal**: {result.journal} ({result.publication_date.year})\n",
                f"**PMID**: {result.pmid}\n\n",
                "### Summary\n",
                f"{summary}\n\n",
                "### Analysis\n",
                f"{analysis}\n\n"
            ])
        
        return "\n".join(content_parts)
