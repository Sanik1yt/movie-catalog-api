from sqlalchemy import CheckConstraint, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        UniqueConstraint("title", "year", name="uq_movies_title_year"),
        CheckConstraint("length(trim(title)) BETWEEN 1 AND 200", name="ck_movies_title"),
        CheckConstraint("year BETWEEN 1888 AND 2100", name="ck_movies_year"),
        CheckConstraint("length(trim(genre)) BETWEEN 1 AND 50", name="ck_movies_genre"),
        CheckConstraint("rating BETWEEN 0 AND 10", name="ck_movies_rating"),
        CheckConstraint("length(description) <= 2000", name="ck_movies_description"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
