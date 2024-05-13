from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
import pytest
from app.oauth2 import create_access_token
from app import models


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:r00tr00t@localhost:5432/fastapi_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    # below codelines run before we run our tests - e.g. first it will delete the existing table and then create new tables in database
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)

    yield TestClient(app)

    # below codeline run after our tests finishes execution - e.g. delete tables in database
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test123@test.com", "password": "test123"}
    response = client.post("/users", json=user_data)

    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    # print(new_user)
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "sid@test.com", "password": "test123"}
    response = client.post("/users", json=user_data)

    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    # print(new_user)
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    post_data = [
        {
            "title": "1st title",
            "content": "1st post content",
            "owner_id": test_user["id"],
        },
        {
            "title": "2nd title",
            "content": "2nd post content",
            "owner_id": test_user["id"],
        },
        {
            "title": "3rd title",
            "content": "3rd post content",
            "owner_id": test_user["id"],
        },
        {
            "title": "4th title",
            "content": "4th post content",
            "owner_id": test_user2["id"],
        },
    ]

    def create_post_model(post: dict):
        return models.Post(**post)

    posts_map = map(create_post_model, post_data)
    posts = list(posts_map)

    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()

    return posts
