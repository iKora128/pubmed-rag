from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ..schemas import ArticleResponse, ArticleCreateResponse
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..services import ArticleGenerator

router = APIRouter()

@router.post("/generate-article", response_model=ArticleCreateResponse)
async def generate_article(
    search_results: list[ArticleResponse],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """検索結果から記事を生成"""
    try:
        generator = ArticleGenerator()
        article = generator.generate_article(search_results)
        
        # Firebase UIDをDBのuser_idに変換
        user = db.exec(db.select(User).where(User.firebase_uid == current_user)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        article.user_id = user.id
        
        # DBに保存
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 