from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(32), default="user", index=True)
