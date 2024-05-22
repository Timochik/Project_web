import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base, User, UserRole
from src.database.db import get_db
from src.services.auth import auth_service


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678"
}


@pytest_asyncio.fixture
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    hash_password = auth_service.get_password_hash(password=test_user["password"])
    current_user = User(
        username=test_user["username"],
        email=test_user["email"],
        password=hash_password,
        role=UserRole.user,
    )
    db.add(current_user)
    db.commit()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def comment():
    return {
        "image_id": 1,
        "text": "Test text"
    }