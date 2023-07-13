from sqlalchemy import Column, String, Boolean, Integer
from db.session import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50), unique=True, nullable=False)
    email: str = Column(String, unique=True, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)

