import json
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
def not_verified_fake_user():
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

@pytest.fixture(scope="module")
def verified_fake_user():
    fake_user_dict = {
            "id": 3,
            "first_name": "Fake",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "fake@fake.fake",
            "username": "Fake",
            "last_name": "Faky",
            "is_verified": True,
            "role": "user",
            "password_hash": Hasher.hash_password("ffffffff"),
            "updated_at": "2024-10-29T12:06:38.591628"
        }
    return User(**fake_user_dict)

@pytest.fixture(scope="module")
def fake_created_user():
    fake_created_user_dict = {
            "id": 3,
            "first_name": "TomB",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "ibarreche.tom@hotmail.fr",
            "username": "hotmail",
            "last_name": "Ibarreche",
            "is_verified": False,
            "role": "user",
            "updated_at": "2024-10-29T12:06:38.591628"
        }
    return User(**fake_created_user_dict)

@pytest.fixture(scope="module")
def fake_user_signup_data():
    return {
        "username":"hotmail",
        "email": "ibarreche.tom@hotmail.fr",
        "password":"ffffffff",
        "first_name":"TomB",
        "last_name":"Ibarreche",
        "date_of_birth":"1993-10-12"
    }

@pytest.fixture(scope="module")
def fake_admin():
    fake_user_dict = {
            "id": 3,
            "first_name": "admin",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "admin@admin.admin",
            "username": "Fake",
            "last_name": "Admin",
            "is_verified": True,
            "role": "admin",
            "password_hash": Hasher.hash_password("ffffffff"),
            "updated_at": "2024-10-29T12:06:38.591628"
        }
    return User(**fake_user_dict)

@pytest.fixture(scope="function")
def log_admin(test_app,fake_admin, monkeypatch):
    from src.auth.repository import UserRepository

    async def mock_get(self,user_email):
        return fake_admin
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "admin@admin.admin",
        "password":"ffffffff"
    }
    response = test_app.post("/api/v1/auth/login", content=json.dumps(payload_data))
    return response.json()["access_token_bearer"]


@pytest.fixture(scope="function")
def log_user(test_app,verified_fake_user, monkeypatch):
    from src.auth.repository import UserRepository

    async def mock_get(self,user_email):
        return verified_fake_user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "fake@fake.fake",
        "password":"ffffffff"
    }
    response = test_app.post("/api/v1/auth/login", content=json.dumps(payload_data))
    return response.json()["access_token_bearer"]

@pytest.fixture(scope="function")
def fake_user_list():
    return [
        {
            "id": 1,
            "username": "Admin",
            "first_name": "Admin",
            "last_name": "Admin",
            "date_of_birth": "2020-01-01",
            "email": "ibarreche666@gmail.com",
            "role": "admin",
            "books": []
        },
        {
            "id": 6,
            "username": "bbb",
            "first_name": "TomB",
            "last_name": "Ibarreche",
            "date_of_birth": "1993-10-12",
            "email": "de@hotmail.fr",
            "role": "user",
            "books": []
        }
    ]

@pytest.fixture(scope="module")
def expired_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImliYXJyZWNoZTY2NkBnbWFpbC5jb20iLCJ1c2VyX2lkIjoxMCwidXNlcl9yb2xlIjoiYWRtaW4iLCJleHAiOjE3Mjk3ODkwNDd9.W0rQkoFG8FV7MXkPyTVdrUG4aEDw513iETocGtTX818"

@pytest.fixture(scope="module")
def failed_signature_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.FpbCI6ImliYXJyZWNoZS50b21AaG90bWFpbC5mciIsInVzZXJfaWQiOjI2LCJ1c2VyX3JvbGUiOiJjb250ZW50X2NyZWF0b3IiLCJleHAiOjE3Mjk3ODU3OTJ9.IC4T_lTwOIva20IHHCsgEF2ypEhZyAzPFdAmap6oKbU"
