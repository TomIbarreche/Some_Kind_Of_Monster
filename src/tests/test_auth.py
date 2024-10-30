import json
import pytest
from src.auth.repository import UserRepository
from src.auth.utils import CreateMail

def test_create_user(test_app, monkeypatch, fake_created_user, fake_user_signup_data):
    test_request_payload = fake_user_signup_data
    test_response_payload= {
        "message": "User successfully created. Check your email to verify your account",
        "user":fake_created_user.model_dump()
    }

    async def mock_get(self, user_data):
        return (False,False)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)

    async def mock_post(self, new_user):
        return fake_created_user
    
    monkeypatch.setattr(UserRepository, "create_user", mock_post)

    def mock_create_message(self,user_email, subject):
        return {"ok":"Alright"}
    
    monkeypatch.setattr(CreateMail,"create_message", mock_create_message)

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
def test_create_already_existing_user(test_app, monkeypatch, email_exists, username_exists, err_status_code, err_msg, err_code, fake_user_signup_data):
    test_request_payload= fake_user_signup_data

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


def test_log_user(test_app, monkeypatch, verified_fake_user):
    async def mock_get(self,user_email):
        return verified_fake_user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "fake@fake.fake",
        "password":"ffffffff"
    }
    response = test_app.post("/api/v1/auth/login", content=json.dumps(payload_data))
    assert response.status_code == 200
    assert response.json()["message"] == "Login Successfull"
    assert response.json()["user"] == {"id":3,"username":"Fake","email":"fake@fake.fake"}
        
@pytest.mark.parametrize(
    "user, password, err_status_code, err_msg, err_code",
    [
        [None, "ffffffff", 404, "The user with this email doesnt exists", "user_not_found"],
        ["not_verified_fake_user", "wrongPassword",  404, "Unable to login user with those credentials", "invalid_credentials"],
        ["not_verified_fake_user","ffffffff",403, "The user is trying to login but need to verified his email first", "user_not_verified"]
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

def test_get_all_users(test_app, monkeypatch, log_admin, fake_user_list):
    async def mock_get_all(self, search, limit, offset):
        return fake_user_list
    
    monkeypatch.setattr(UserRepository, "get_all_users", mock_get_all)
    token = log_admin
    response = test_app.get("/api/v1/auth/all",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["username"] == "Admin"

@pytest.mark.parametrize(
    "limit, offset, err_status_code, err_msg,",
    [
        [0, 0, 422, "Input should be greater than 0"],
        [101, 0, 422, "Input should be less than or equal to 100"],
        [1, -1, 422, "Input should be greater than -1"],
        ["e", 0, 422, "Input should be a valid integer, unable to parse string as an integer"]
    ]
)
def test_get_all_users_with_wrong_query_parameters(test_app, monkeypatch, limit, offset, err_status_code, err_msg, fake_user_list, log_admin):
    async def mock_get_all(self, search, limit, offset):
        return fake_user_list
    
    monkeypatch.setattr(UserRepository, "get_all_users", mock_get_all)

    token = log_admin
    response = test_app.get(f"/api/v1/auth/all?limit={limit}&offset={offset}",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == err_status_code
    assert response.json()["detail"][0]["msg"] == err_msg

@pytest.mark.parametrize(
    "token, err_status_code, err_msg, err_code",
    [
        ["log_user", 403, "Roles ['admin'] are required", "insufficient_permission"],
        ["expired_token", 401, "Signature has expired", "token_decode_fail"],
        ["failed_signature_token", 401, "Signature verification failed","token_decode_fail"]
    ]
)
def test_get_all_users_with_errors(test_app, monkeypatch, token, err_status_code, err_msg, err_code, request):
    token = request.getfixturevalue(token)
    response = test_app.get(f"/api/v1/auth/all",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == err_status_code
    assert response.json()["info"]["issue"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code
    