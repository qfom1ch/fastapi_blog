from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, String
from sqlalchemy.sql.schema import Column, ForeignKey

from db.session import Base


class Post(Base):
    __tablename__: str = "posts"

    id: int = Column(Integer, primary_key=True)
    author_id: int = Column(ForeignKey('users.id'), nullable=False)
    slug: str = Column(String, index=True)
    title: str = Column(String(100), index=True, nullable=False)
    text: str = Column(String, nullable=False)
    short_description: str = Column(String(240), nullable=False)
    published_at: datetime = Column(
        TIMESTAMP(timezone=True), default=datetime.now()
    )
