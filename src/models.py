# project/models.py

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=100)
    firebase_uid: str = Field(unique=True, index=True)

    # リレーション: User -> Article
    articles: list["Article"] = Relationship(back_populates="user")


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    content: str | None = None
    summary: str | None = None
    keywords: list[str] | None = None
    source_articles: list[str] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int | None = Field(default=None, foreign_key="users.id")

    # リレーション: Article -> User
    user: User | None = Relationship(back_populates="articles")
