import pytest
from fastapi import HTTPException
from src.auth import verify_firebase_token, get_current_user

def test_verify_firebase_token(client, mock_firebase_auth):
    """Firebase認証トークンの検証テスト"""
    # 正常系: 有効なトークン
    response = client.get(
        "/api/generate-article",
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code != 401  # 認証エラーではない

    # 異常系: 無効なトークン
    response = client.get(
        "/api/generate-article",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

    # 異常系: トークンなし
    response = client.get("/api/generate-article")
    assert response.status_code == 401

def test_get_current_user(mock_firebase_auth):
    """現在のユーザー取得テスト"""
    # モックトークンを使用
    token = {"uid": "test123"}
    user_id = get_current_user(token)
    assert user_id == "test123"

    # 無効なトークン
    with pytest.raises(HTTPException) as exc_info:
        invalid_token = {}
        get_current_user(invalid_token)
    assert exc_info.value.status_code == 401

def test_protected_endpoints(client, mock_firebase_auth, override_get_db, test_user):
    """保護されたエンドポイントのテスト"""
    # 認証ありの正常系
    response = client.post(
        "/api/generate-article",
        headers={"Authorization": "Bearer valid_token"},
        json={"search_results": []}
    )
    assert response.status_code != 401

    # 認証なしの異常系
    response = client.post(
        "/api/generate-article",
        json={"search_results": []}
    )
    assert response.status_code == 401

def test_user_association(client, mock_firebase_auth, override_get_db, test_user, sample_article_response):
    """ユーザーと記事の関連付けテスト"""
    # 記事生成APIを呼び出し
    response = client.post(
        "/api/generate-article",
        headers={"Authorization": "Bearer valid_token"},
        json={"search_results": [sample_article_response]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id  # 生成された記事が正しいユーザーに関連付けられている 