import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.app import app
from src.database import get_db
from src.models import User, Article

@pytest.fixture
def client():
    """テスト用のFastAPIクライアント"""
    return TestClient(app)

@pytest.fixture
def test_db():
    """テスト用のインメモリデータベース"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session

@pytest.fixture
def override_get_db(test_db):
    """データベースの依存性を上書き"""
    def _override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db):
    """テスト用のユーザー"""
    user = User(username="testuser", firebase_uid="test123")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def mock_firebase_auth(monkeypatch):
    """Firebase認証のモック"""
    def mock_verify_token(*args, **kwargs):
        return {"uid": "test123"}
    
    monkeypatch.setattr("firebase_admin.auth.verify_id_token", mock_verify_token)

@pytest.fixture
def sample_article_response():
    """テスト用の論文データ"""
    return {
        "pmid": "12345678",
        "title": "Test Article",
        "abstract": "This is a test abstract for testing purposes.",
        "authors": [
            {
                "last_name": "Smith",
                "fore_name": "John",
                "affiliation": "Test University"
            }
        ],
        "mesh_terms": [
            {
                "descriptor": "Test Term",
                "qualifiers": ["therapy"]
            }
        ],
        "keywords": ["test", "research"],
        "journal": "Test Journal",
        "publication_date": {
            "year": 2024,
            "month": 1,
            "day": 1
        }
    } 