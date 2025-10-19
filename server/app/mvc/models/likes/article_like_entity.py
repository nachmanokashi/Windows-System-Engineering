from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from datetime import datetime
from app.mvc.models.base import Base  # ✅ ייבוא מ-Base מרכזי


class ArticleLike(Base):
    __tablename__ = "article_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys - עכשיו יעבוד כי Article וגם ArticleLike משתמשים באותו Base!
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # True = like, False = dislike
    is_like = Column(Boolean, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        reaction = "👍" if self.is_like else "👎"
        return f"<ArticleLike(id={self.id}, article={self.article_id}, user={self.user_id}, {reaction})>"