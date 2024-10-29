import json
import pytest
from src.auth.repository import UserRepository
from src.auth.service import UserService
from src.db.models import User
from src.auth.utils import Hasher

# fake_user_dict = {
#             "id": 3,
#             "first_name": "Fake",
#             "date_of_birth": "1993-10-12",
#             "created_at": "2024-10-29T12:06:38.591628",
#             "email": "fake@fake.fake",
#             "username": "Fake",
#             "last_name": "Faky",
#             "is_verified": False,
#             "role": "user",
#             "password_hash": Hasher.hash_password("ffffffff"),
#             "updated_at": "2024-10-29T12:06:38.591628"
#         }
# fake_user = User(**fake_user_dict)

def test_create_user(test_app, monkeypatch):
    test_request_payload= { 
        "username":"hotmail",
        "email": "ibarreche.tom@hotmail.fr",
        "password":"ffffffff",
        "first_name":"TomB",
        "last_name":"Ibarreche",
        "date_of_birth":"1993-10-12"
    }
    test_response_payload= {
        "message": "User successfully created. Check your email to verify your account",
        "user": {
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
    }

    async def mock_get(self, user_data):
        return (False,False)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)

    async def mock_post(self, new_user):
        return_data =  {
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
        new_user = User(**return_data)
        return new_user
    
    monkeypatch.setattr(UserRepository, "create_user", mock_post)

    response = test_app.post("/api/v1/auth/signup", content=json.dumps(test_request_payload))
    assert response.status_code == 201
    assert response.json() == test_response_payload

@pytest.mark.parametrize(
    "email_exists, username_exists, err_status_code, err_msg, err_code",
    [
        [True,False,409,"This email is already registered by an other user","user_already_exist"],
        [False,True,409,"This username is already registered by an other user","user_already_exist"]
    ]    
)
def test_create_already_existing_user(test_app, monkeypatch, email_exists, username_exists, err_status_code, err_msg, err_code):
    test_request_payload= { 
        "username":"hotmail",
        "email": "ibarreche.tom@hotmail.fr",
        "password":"ffffffff",
        "first_name":"TomB",
        "last_name":"Ibarreche",
        "date_of_birth":"1993-10-12"
    }
    async def mock_get(self, user_data):
        return (email_exists,username_exists)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)

    response = test_app.post("/api/v1/auth/signup", content=json.dumps(test_request_payload))

    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

@pytest.mark.parametrize(
    "payload, err_status_code",
    [
        #Incorrect email - no @
        [
            { 
                "username":"hotmail",
                "email": "ibarreche.tom",
                "password":"ffffffff",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":"1993-10-12"
            },
            422
        ],
        #Incorrect email - nothing before @
        [
            { 
                "username":"hotmail",
                "email": "@ibarreche.tom",
                "password":"ffffffff",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":"1993-10-12"
            },
            422
        ],
        #username too short
        [
            { 
                "username":"1",
                "email": "ibarreche.tom@hotmail.fr",
                "password":"ffffffff",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":"1993-10-12"
            },
            422
        ],
        #Username too long
        [
            { 
                "username":"1111111111111",
                "email": "ibarreche.tom@hotmail.fr",
                "password":"ffffffff",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":"1993-10-12"
            },
            422
        ],
        #Password too short
        [
            { 
                "username":"111",
                "email": "ibarreche.tom@hotmail.fr",
                "password":"1",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":"1993-10-12"
            },
            422
        ],
        #No DOB
        [
            { 
                "username":"111",
                "email": "ibarreche.tom@hotmail.fr",
                "password":"ffffffff",
                "first_name":"TomB",
                "last_name":"Ibarreche",
                "date_of_birth":""
            },
            422
        ]
    ]
)
def test_create_user_with_payload_errors(test_app, monkeypatch, payload, err_status_code):
    async def mock_get(self, user_data):
        return (False,False)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)
    response = test_app.post("/api/v1/auth/signup", content=json.dumps(payload))
    assert response.status_code == err_status_code


def test_log_user(test_app, monkeypatch):
    async def mock_get(self,user_email):
        return_data = {
            "id": 3,
            "first_name": "Fake",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "fake@fake.fake",
            "username": "Fake",
            "last_name": "Faky",
            "is_verified": True,
            "role": "admin",
            "password_hash": Hasher.hash_password("ffffffff"),
            "updated_at": "2024-10-29T12:06:38.591628"
        }
        user = User(**return_data)
        return user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "fake@fake.fake",
        "password":"ffffffff"
    }
    response = test_app.post("/api/v1/auth/login", content=json.dumps(payload_data))
    assert response.status_code == 200
    assert response.json()["message"] == "Login Successfull"
    assert response.json()["user"] == {"id":3,"username":"Fake","email":"fake@fake.fake"}
    return response.json()["access_token_bearer"]
        
@pytest.mark.parametrize(
    "user, password, err_status_code, err_msg, err_code",
    [
        [None, "ffffffff", 404, "The user with this email doesnt exists", "user_not_found"],
        ["test_user", "wrongPassword",  404, "Unable to login user with those credentials", "invalid_credentials"],
        ["test_user","ffffffff",403, "The user is trying to login but need to verified his email first", "user_not_verified"]
    ]
)
def test_log_user_with_errors(test_app, monkeypatch, user, password, err_status_code, err_msg, err_code, request):
    if user is not None:
        user = request.getfixturevalue(user)
    async def mock_get(self,user_email):
        return user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)

    payload_data= {
        "email": "fake@fake.fake",
        "password":password
    }
    response = test_app.post("/api/v1/auth/login", content=json.dumps(payload_data))
    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

def test_get_all_user(test_app, monkeypatch):
    test_data = [
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

    fake_admin_dict = {
            "id": 3,
            "first_name": "Fake",
            "date_of_birth": "1993-10-12",
            "created_at": "2024-10-29T12:06:38.591628",
            "email": "fa@fa.fa",
            "username": "Fake",
            "last_name": "Faky",
            "is_verified": False,
            "role": "admin",
            "password_hash": Hasher.hash_password("ffffffff"),
            "updated_at": "2024-10-29T12:06:38.591628"
        }
    fake_admin = User(**fake_admin_dict)

    async def mock_get(self,user_email):
        return fake_admin
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)

    async def mock_get_all(self, search, limit, offset):
        return test_data
    
    monkeypatch.setattr(UserRepository, "get_all_users", mock_get_all)
    token = test_log_user(test_app, monkeypatch)
    response = test_app.get("/api/v1/auth/all",headers={"Authorization":f"Bearer {token}"})
    print(response.content)
    assert response.status_code == 200
    


