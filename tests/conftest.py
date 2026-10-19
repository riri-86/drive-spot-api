import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL が設定されていません。.env を確認してください")

testing_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testing_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=testing_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=testing_engine)
