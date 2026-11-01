from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Movie
from .schemas import MovieCreate, MovieRead, MovieUpdate

app = FastAPI(title="Каталог фильмов", version="1.0.0")
DB = Annotated[Session, Depends(get_db)]
MovieID = Annotated[int, Path(gt=0)]


def find_movie(movie_id: int, db: Session) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie


def save_movie(movie: Movie, db: Session) -> Movie:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Фильм с таким названием и годом уже существует")
    db.refresh(movie)
    return movie


@app.get("/", tags=["Сервис"])
def root():
    return {"message": "Каталог фильмов", "docs": "/docs"}


@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED, tags=["Фильмы"])
def create_movie(data: MovieCreate, db: DB):
    movie = Movie(**data.model_dump())
    db.add(movie)
    return save_movie(movie, db)


@app.get("/movies", response_model=list[MovieRead], tags=["Фильмы"])
def list_movies(
    db: DB,
    title: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    genre: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    year: Annotated[int | None, Query(ge=1888, le=2100)] = None,
    min_rating: Annotated[float | None, Query(ge=0, le=10)] = None,
    sort_by: Literal["id", "title", "year", "rating"] = "id",
    order: Literal["asc", "desc"] = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    query = select(Movie)
    if title is not None:
        query = query.where(Movie.title.contains(title.strip(), autoescape=True))
    if genre is not None:
        query = query.where(Movie.genre == genre.strip())
    if year is not None:
        query = query.where(Movie.year == year)
    if min_rating is not None:
        query = query.where(Movie.rating >= min_rating)
    column = getattr(Movie, sort_by)  # sort_by ограничен Literal, не произвольный SQL.
    sorting = column.desc() if order == "desc" else column.asc()
    return db.scalars(query.order_by(sorting, Movie.id).offset(offset).limit(limit)).all()


@app.get("/movies/{movie_id}", response_model=MovieRead, tags=["Фильмы"])
def read_movie(movie_id: MovieID, db: DB):
    return find_movie(movie_id, db)


@app.put("/movies/{movie_id}", response_model=MovieRead, tags=["Фильмы"])
def replace_movie(movie_id: MovieID, data: MovieCreate, db: DB):
    movie = find_movie(movie_id, db)
    for key, value in data.model_dump().items():
        setattr(movie, key, value)
    return save_movie(movie, db)


@app.patch("/movies/{movie_id}", response_model=MovieRead, tags=["Фильмы"])
def update_movie(movie_id: MovieID, data: MovieUpdate, db: DB):
    movie = find_movie(movie_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(movie, key, value)
    return save_movie(movie, db)


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Фильмы"])
def delete_movie(movie_id: MovieID, db: DB):
    movie = find_movie(movie_id, db)
    db.delete(movie)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
