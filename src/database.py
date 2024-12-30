# project/database.py

from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./app.db"  # 例: sqliteファイル。実際には好みのDB接続URLに置き換え

engine = create_engine(
    DATABASE_URL,
    echo=True  # SQL文をログ出力する。開発時のみTrueにすると良い
)

def init_db():
    """
    アプリ起動時に呼び出してテーブルを作成する処理。
    """
    from .models import SQLModel  # 循環インポート回避のためここで
    SQLModel.metadata.create_all(engine)

def get_db():
    """
    FastAPIの依存関数として利用し、セッションをyieldする。
    """
    with Session(engine) as session:
        yield session
