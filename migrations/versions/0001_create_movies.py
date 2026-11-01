"""Создание таблицы каталога фильмов."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("genre", sa.String(50), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("title", "year", name="uq_movies_title_year"),
        sa.CheckConstraint("length(trim(title)) BETWEEN 1 AND 200", name="ck_movies_title"),
        sa.CheckConstraint("year BETWEEN 1888 AND 2100", name="ck_movies_year"),
        sa.CheckConstraint("length(trim(genre)) BETWEEN 1 AND 50", name="ck_movies_genre"),
        sa.CheckConstraint("rating BETWEEN 0 AND 10", name="ck_movies_rating"),
        sa.CheckConstraint("length(description) <= 2000", name="ck_movies_description"),
    )
    for name in ("title", "year", "genre"):
        op.create_index(f"ix_movies_{name}", "movies", [name])


def downgrade():
    op.drop_table("movies")
