import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def film(**changes):
    return {"title": "Arrival", "year": 2016, "genre": "Sci-Fi", "rating": 8.0, "description": "First contact", **changes}


def test_full_crud(client):
    created = client.post("/movies", json=film())
    assert created.status_code == 201
    movie_id = created.json()["id"]
    assert client.get(f"/movies/{movie_id}").json()["title"] == "Arrival"
    assert client.patch(f"/movies/{movie_id}", json={"rating": 9}).json()["rating"] == 9
    assert client.put(f"/movies/{movie_id}", json=film(title="Contact")).json()["title"] == "Contact"
    assert client.delete(f"/movies/{movie_id}").status_code == 204
    assert client.get(f"/movies/{movie_id}").status_code == 404


@pytest.mark.parametrize("change", [{"title": " "}, {"year": 1800}, {"rating": 11}, {"genre": ""}, {"extra": 1}])
def test_validation(client, change):
    assert client.post("/movies", json=film(**change)).status_code == 422


def test_duplicate_and_rollback(client):
    assert client.post("/movies", json=film()).status_code == 201
    assert client.post("/movies", json=film()).status_code == 409
    assert client.post("/movies", json=film(title="Contact")).status_code == 201


def test_filters_sorting_and_pagination(client):
    for data in [film(), film(title="Contact", year=1997, rating=7.5), film(title="Other", genre="Drama", year=2016, rating=9)]:
        assert client.post("/movies", json=data).status_code == 201
    assert [x["title"] for x in client.get("/movies?genre=Sci-Fi&sort_by=rating&order=desc").json()] == ["Arrival", "Contact"]
    assert len(client.get("/movies?year=2016&min_rating=8.5").json()) == 1
    assert len(client.get("/movies?title=rr").json()) == 1
    assert len(client.get("/movies?offset=1&limit=1").json()) == 1
    assert client.get("/movies?sort_by=invalid").status_code == 422


def test_patch_null_and_missing(client):
    movie_id = client.post("/movies", json=film()).json()["id"]
    assert client.patch(f"/movies/{movie_id}", json={"title": None}).status_code == 422
    assert client.patch(f"/movies/{movie_id}", json={}).json()["title"] == "Arrival"
    assert client.delete("/movies/999").status_code == 404
    assert client.get("/movies/0").status_code == 422
