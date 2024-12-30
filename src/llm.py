from openai import OpenAI
import os
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
from pydantic_settings import BaseSettings

# OpenAI クライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLMError(Exception):
    """LLM関連のカスタムエラー"""
    pass

class AbstractAnalysisError(LLMError):
    """アブストラクト分析時のエラー"""
    pass

class AbstractSummaryError(LLMError):
    """アブストラクト要約時のエラー"""
    pass

class LLMSettings(BaseSettings):
    model_name: str = "gpt-4"
    temperature: float = 0.3
    max_tokens_summary: int = 150
    max_tokens_analysis: int = 300
    
    class Config:
        env_prefix = "LLM_"

@lru_cache()
def get_llm_settings() -> LLMSettings:
    return LLMSettings()

@retry(
    stop=stop_after_attempt(3),  # 3回まで再試行
    wait=wait_exponential(multiplier=1, min=4, max=10)  # 指数関数的なバックオフ
)
def summarize_abstract(abstract_text: str) -> str:
    """
    論文アブストラクトを要約する
    
    Args:
        abstract_text (str): 要約対象のアブストラクト
        
    Returns:
        str: 要約されたテキスト
        
    Raises:
        AbstractSummaryError: 要約生成に失敗した場合
    """
    if not abstract_text:
        raise AbstractSummaryError("アブストラクトが空です")

    settings = get_llm_settings()
    
    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                    医学論文のアブストラクトを要約してください。
                    - 重要な知見を1-2文で簡潔に
                    - 専門用語は必要に応じて平易な表現に
                    - 結論を中心に要約
                    """
                },
                {"role": "user", "content": f"以下のアブストラクトを要約してください：\n\n{abstract_text}"}
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens_summary
        )
        
        if not response.choices:
            raise AbstractSummaryError("APIからの応答が不正です")
            
        return response.choices[0].message.content or "要約を生成できませんでした"
        
    except Exception as e:
        raise AbstractSummaryError(f"要約生成中にエラーが発生しました: {str(e)}")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def analyze_abstract(abstract_text: str) -> str:
    """
    論文アブストラクトを分析する
    
    Args:
        abstract_text (str): 分析対象のアブストラクト
        
    Returns:
        str: 分析結果のテキスト
        
    Raises:
        AbstractAnalysisError: 分析に失敗した場合
    """
    if not abstract_text:
        raise AbstractAnalysisError("アブストラクトが空です")

    settings = get_llm_settings()
    
    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                    医学論文のアブストラクトを以下の観点で分析してください：
                    1. 研究目的
                    2. 研究手法
                    3. 主要な結果
                    4. 臨床的意義
                    5. 限界点
                    
                    箇条書きで簡潔にまとめてください。
                    """
                },
                {"role": "user", "content": f"以下のアブストラクトを分析してください：\n\n{abstract_text}"}
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens_analysis
        )
        
        if not response.choices:
            raise AbstractAnalysisError("APIからの応答が不正です")
            
        return response.choices[0].message.content or "分析を生成できませんでした"
        
    except Exception as e:
        raise AbstractAnalysisError(f"分析生成中にエラーが発生しました: {str(e)}")

# エラーハンドリングのテスト用関数
def test_error_handling():
    """エラーハンドリングのテスト"""
    try:
        # 空のアブストラクトでテスト
        summarize_abstract("")
    except AbstractSummaryError as e:
        print(f"Expected error caught: {e}")

    try:
        # 不正なAPIキーでテスト
        os.environ["OPENAI_API_KEY"] = "invalid_key"
        analyze_abstract("テストアブストラクト")
    except AbstractAnalysisError as e:
        print(f"Expected error caught: {e}")

if __name__ == "__main__":
    test_error_handling()