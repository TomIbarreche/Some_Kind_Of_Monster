import pytest
from starlette.testclient import TestClient
from src.auth.utils import Hasher
from src.db.models import User
from src.main import app

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="module")
def test_user():
    fake_user_dict = {
            "id": 3,
            "first_name": "Fake",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "fake@fake.fake",
            "username": "Fake",
            "last_name": "Faky",
            "is_verified": False,
            "role": "user",
            "password_hash": Hasher.hash_password("ffffffff"),
            "updated_at": "2024-10-29T12:06:38.591628"
        }
    return User(**fake_user_dict)