import json
import pytest
from sqlmodel import create_engine, SQLModel
from starlette.testclient import TestClient
from src.auth.utils import Hasher, UrlSerializer
from src.db import get_db
from src.db.models import Book, User
from src.main import app
from sqlmodel import create_engine, Session
from src.config import settings

@pytest.fixture(name="session")
def session_fixture():
    from src.auth.service import UserService
    engine = create_engine("postgresql+psycopg2://postgres:The_Bioshock_Within@localhost:5432/Trantor_test")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user_service = UserService(session)
        if user_service.check_if_admin_exists() == False:
            print("No default admin found. Lets create one")
            user_service.create_default_admin()
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")  
def client_fixture(session: Session):  

    def get_db_override(): 
        return session

    app.dependency_overrides[get_db] = get_db_override  
    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  
    

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
            "updated_at": "2024-10-29T12:06:38.591628",
        }
    return User(**fake_user_dict)

@pytest.fixture(scope="module")
def verified_fake_user_with_books(fake_retreive_book):
    from src.auth.schemas import UserOutModelWithBooks

    user = {
        "id": 3,
        "username": "Fake",
        "first_name": "Fake",
        "last_name": "Faky",
        "date_of_birth": "1993-10-12",
        "email": "fake@fake.fake",
        "role": "user",
        "books": [
            fake_retreive_book
        ]
    }
    return UserOutModelWithBooks(**user)

@pytest.fixture(scope="module")
def verified_fake_user_with_new_password():
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
            "password_hash": Hasher.hash_password("aaaaaaaa"),
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
        "email": "fake@fake.fake",
        "password":"ffffffff",
        "first_name":"TomB",
        "last_name":"Ibarreche",
        "date_of_birth":"1993-10-12"
    }

@pytest.fixture(scope="module")
def fake_content_creator_signup_data():
    return {
        "username":"content",
        "email": "content@content.content",
        "password":"ffffffff",
        "first_name":"Sif",
        "last_name":"Bob",
        "date_of_birth":"1993-10-12"
    }
@pytest.fixture(scope="module")
def fake_user_update_data():
    return {
        "username":"Kelso",
        "email": "fake@fake.fake",
        "password":"ffffffff",
        "first_name":"Coin",
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
def log_admin(client,fake_admin, monkeypatch):
    from src.auth.repository import UserRepository

    def mock_get(self,user_email):
        return fake_admin
    

    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "admin@admin.admin",
        "password":"ffffffff"
    }
    response = client.post("/api/v1/auth/login", content=json.dumps(payload_data))
    return response.json()["access_token_bearer"]


@pytest.fixture(scope="function")
def log_user(client,verified_fake_user, monkeypatch):
    from src.auth.repository import UserRepository

    def mock_get(self,user_email):
        return verified_fake_user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "fake@fake.fake",
        "password":"ffffffff"
    }
    response = client.post("/api/v1/auth/login", content=json.dumps(payload_data))
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
            "id": 2,
            "username": "Fake",
            "first_name": "Fake",
            "last_name": "Faky",
            "date_of_birth": "1993-10-12",
            "email": "fake@fake.fake",
            "role": "user",
            "books": []
        },
        {
            "id": 3,
            "username": "ContentDude",
            "first_name": "Fake",
            "last_name": "Faky",
            "date_of_birth": "1993-10-12",
            "email": "content@content.content",
            "role": "content_creator",
            "books": []
        }
    ]

@pytest.fixture(scope="module")
def expired_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImliYXJyZWNoZTY2NkBnbWFpbC5jb20iLCJ1c2VyX2lkIjoxMCwidXNlcl9yb2xlIjoiYWRtaW4iLCJleHAiOjE3Mjk3ODkwNDd9.W0rQkoFG8FV7MXkPyTVdrUG4aEDw513iETocGtTX818"

@pytest.fixture(scope="module")
def failed_signature_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.FpbCI6ImliYXJyZWNoZS50b21AaG90bWFpbC5mciIsInVzZXJfaWQiOjI2LCJ1c2VyX3JvbGUiOiJjb250ZW50X2NyZWF0b3IiLCJleHAiOjE3Mjk3ODU3OTJ9.IC4T_lTwOIva20IHHCsgEF2ypEhZyAzPFdAmap6oKbU"


@pytest.fixture(scope="module")
def verify_token():
    token = UrlSerializer.create_url_safe_token({"email":"fake@fake.fake"})
    return token


@pytest.fixture(scope="module")
def content_creator_verify_token():
    token = UrlSerializer.create_url_safe_token({"email":"content@content.content"})
    return token

@pytest.fixture(scope="module")
def valid_password_data():
    return {
        "new_password":"aaaaaaaa",
        "confirm_password":"aaaaaaaa"
    }

@pytest.fixture(scope="module")
def invalid_password_data():
    return {
        "new_password":"aaaaaaaa",
        "confirm_password":"bbbbbbbb"
    }

@pytest.fixture(scope="module")
def signup_data():
    return {
        "email":"fake@fake.fake",
        "password":"ffffffff"
    }

@pytest.fixture(scope="module")
def content_creator_sign_up_data():
    return {
        "email":"content@content.content",
        "password":"ffffffff"
    }

@pytest.fixture(scope="function")
def create_verify_connect_standard_user(client,fake_user_signup_data, signup_data, verify_token):
    client.post("/api/v1/auth/signup", json=fake_user_signup_data)
    token = verify_token
    client.get(f"/api/v1/auth/verify/{token}")
    log_user = client.post("/api/v1/auth/login", json=signup_data)
    access_token = log_user.json()["access_token_bearer"]
    return access_token

@pytest.fixture(scope="function")
def connect_admin(client):
    log_admin = client.post("/api/v1/auth/login", json={"email":settings.default_admin_email, "password": settings.default_admin_password})
    admin_access_token = log_admin.json()["access_token_bearer"]
    return admin_access_token

@pytest.fixture(scope="function")
def create_verify_connect_content_creator_user(client, fake_content_creator_signup_data, content_creator_sign_up_data, content_creator_verify_token, connect_admin):
    client.post("/api/v1/auth/signup", json=fake_content_creator_signup_data)
    token = content_creator_verify_token
    client.get(f"/api/v1/auth/verify/{token}")
    admin_token = connect_admin
    client.patch(f"/api/v1/auth/profile/2/role_attribution", json={"role": "content_creator"},headers={"Authorization":f"Bearer {admin_token}"})
    log_user = client.post("/api/v1/auth/login", json=content_creator_sign_up_data)
    access_token = log_user.json()["access_token_bearer"]
    return access_token

@pytest.fixture(scope="function")
def create_verify_connect_content_creator_user_2(client, fake_user_signup_data, signup_data, verify_token, connect_admin):
    client.post("/api/v1/auth/signup", json=fake_user_signup_data)
    token = verify_token
    
    client.get(f"/api/v1/auth/verify/{token}")
    admin_token = connect_admin
    client.patch(f"/api/v1/auth/profile/3/role_attribution", json={"role": "content_creator"},headers={"Authorization":f"Bearer {admin_token}"})
    log_user = client.post("/api/v1/auth/login", json=signup_data)
    access_token = log_user.json()["access_token_bearer"]
    return access_token

@pytest.fixture(scope="module")
def fake_create_book_data():
    return {
        "name":"Fake v1",
        "published_date":"2020-12-02",
        "author":"Fake Author 1",
        "editor": "Fake Editor 1",
        "is_omnibus": False
    }

@pytest.fixture(scope="module")
def fake_create_book_data_2():
    return {
        "name":"Coin",
        "published_date":"2020-12-02",
        "author":"Hello",
        "editor": "World",
        "is_omnibus": False
    }

@pytest.fixture(scope="module")
def fake_retreive_book():
    book =  {
        "id": 1,
        "name": "NAme v1",
        "published_date": "2020-12-02",
        "author": "Author 1",
        "editor": "editor 1",
        "is_omnibus": False,
        "users": [
            {
                "id": 3,
                "username": "Adminn",
                "first_name": "Coin coin",
                "last_name": "Irbaddrreche",
                "date_of_birth": "1993-10-12",
                "email": "aa@aa.aa",
                "role": "content_creator"
            }
        ],
        "creator_id": 2
    }

    return Book(**book)
@pytest.fixture(scope="function")
def create_book(client, create_verify_connect_content_creator_user, fake_create_book_data):
    content_creator_token = create_verify_connect_content_creator_user
    client.post("/api/v1/books", json=fake_create_book_data,headers={"Authorization":f"Bearer {content_creator_token}"})
    return content_creator_token

@pytest.fixture(scope="function")
def create_books(client, create_verify_connect_content_creator_user, fake_create_book_data, fake_create_book_data_2):
    content_creator_token = create_verify_connect_content_creator_user
    client.post("/api/v1/books", json=fake_create_book_data,headers={"Authorization":f"Bearer {content_creator_token}"})
    client.post("/api/v1/books", json=fake_create_book_data_2,headers={"Authorization":f"Bearer {content_creator_token}"})

    return content_creator_token