import json
import pytest
from src.auth.repository import UserRepository
from src.auth.utils import MailSender, UrlSerializer
from src.db.models import User

def test_create_user(client, monkeypatch, fake_created_user, fake_user_signup_data):
    test_request_payload = fake_user_signup_data
    test_response_payload= {
        "message": "User successfully created. Check your email to verify your account",
        "user":fake_created_user.model_dump()
    }

    def mock_get(self, user_data):
        return (False,False)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)

    def mock_post(self, new_user):
        return fake_created_user
    
    monkeypatch.setattr(UserRepository, "create_user", mock_post)

    def mock_create_message(user_email, subject):
        return {"ok":"Alright"}
    
    monkeypatch.setattr(MailSender,"create_message", mock_create_message)

    response = client.post("/api/v1/auth/signup", content=json.dumps(test_request_payload))
    assert response.status_code == 201
    assert response.json() == test_response_payload

@pytest.mark.parametrize(
    "email_exists, username_exists, err_status_code, err_msg, err_code",
    [
        [True,False,409,"This email is already registered by an other user","user_already_exist"],
        [False,True,409,"This username is already registered by an other user","user_already_exist"]
    ]    
)
def test_create_already_existing_user(client, monkeypatch, email_exists, username_exists, err_status_code, err_msg, err_code, fake_user_signup_data):
    test_request_payload= fake_user_signup_data

    def mock_get(self, user_data):
        return (email_exists,username_exists)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)
    def mock_create_message(self,user_email, subject):
        return {"ok":"Alright"}
    monkeypatch.setattr(MailSender,"create_message", mock_create_message)
    
    response = client.post("/api/v1/auth/signup", content=json.dumps(test_request_payload))

    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

@pytest.mark.parametrize(
    "payload, err_status_code",
    [
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
def test_create_user_with_payload_errors(client, monkeypatch, payload, err_status_code):
    def mock_get(self, user_data):
        return (False,False)
    
    monkeypatch.setattr(UserRepository, "check_if_user_exists", mock_get)
    response = client.post("/api/v1/auth/signup", content=json.dumps(payload))
    assert response.status_code == err_status_code


def test_log_user(client, monkeypatch, verified_fake_user):
    def mock_get(self,user_email):
        return verified_fake_user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)
   
    payload_data= {
        "email": "fake@fake.fake",
        "password":"ffffffff"
    }
    response = client.post("/api/v1/auth/login", content=json.dumps(payload_data))
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
def test_log_user_with_errors(client, monkeypatch, user, password, err_status_code, err_msg, err_code, request):
    if user is not None:
        user = request.getfixturevalue(user)
    def mock_get(self,user_email):
        return user
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get)

    payload_data= {
        "email": "fake@fake.fake",
        "password":password
    }
    response = client.post("/api/v1/auth/login", content=json.dumps(payload_data))
    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

def test_get_all_users(client, monkeypatch, log_admin, fake_user_list):
    def mock_get_all(self, search, limit, offset):
        return fake_user_list
    
    monkeypatch.setattr(UserRepository, "get_all_users", mock_get_all)
    token = log_admin
    response = client.get("/api/v1/auth/all",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 3
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
def test_get_all_users_with_wrong_query_parameters(client, monkeypatch, limit, offset, err_status_code, err_msg, fake_user_list, log_admin):
    def mock_get_all(self, search, limit, offset):
        return fake_user_list
    
    monkeypatch.setattr(UserRepository, "get_all_users", mock_get_all)

    token = log_admin
    response = client.get(f"/api/v1/auth/all?limit={limit}&offset={offset}",headers={"Authorization":f"Bearer {token}"})
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
def test_get_all_users_with_errors(client, token, err_status_code, err_msg, err_code, request):
    token = request.getfixturevalue(token)
    response = client.get(f"/api/v1/auth/all",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

def test_get_user_profile(client, monkeypatch, fake_user_list):
    def mock_get(self, user_id):
        return fake_user_list[0]
    
    monkeypatch.setattr(UserRepository, "get_user_by_id", mock_get)
    response = client.get("/api/v1/auth/profile/1")
    assert response.status_code == 200
    assert response.json()["id"] == fake_user_list[0]["id"]

def test_get_non_existent_user_profile(client, monkeypatch):
    def mock_get(self, user_id):
        return None
    
    monkeypatch.setattr(UserRepository, "get_user_by_id", mock_get)

    response = client.get("/api/v1/auth/profile/100")
    assert response.status_code == 404
    assert response.json()["initial_details"]["error_code"] == "user_not_found"
    assert response.json()["info"]["error"] == "No user with this id exists"

def test_update_user_profile(client, monkeypatch, fake_user_list, log_user, log_admin):
    def mock_get_by_email(self, user_email):
        return User(**fake_user_list[1])
    
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get_by_email)

    token = log_user
    fake_update_data ={
        "username":"Fake",
        "email": "fake@fake.fake",
        "first_name":"dalsil",
        "last_name":"Irbaddrreche",
        "date_of_birth":"1993-10-12"
    }
    def mock_patch(self,user_to_update, user_data):
        return {
            "id":2,
            "username":"Fake",
            "email": "fake@fake.fake",
            "first_name":"dalsil",
            "last_name":"Irbaddrreche",
            "date_of_birth":"1993-10-12",
            "role": "user"
        }
    monkeypatch.setattr(UserRepository, "update_user", mock_patch)
    response = client.patch("/api/v1/auth/profile/2",content=json.dumps(fake_update_data), headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["first_name"] != fake_user_list[1]["first_name"]
    assert response.json()["date_of_birth"] == fake_user_list[1]["date_of_birth"]
    assert response.json()["id"] == fake_user_list[1]["id"]

@pytest.mark.parametrize(
        "id, username_exists, username, email, email_exists, err_status_code, err_msg, err_code",
        [
            [9999, False,"Fake", "fake@fake.fake", True,403, "You cant update a profile that is not yours", "update_not_allowed"],
            [2, False,"Fake", "coin@coin.xoin", True,409, "This email is already registered by an other user", "user_already_exist"],
            [2, True,"Kelso", "fake@fake.fake", None,409, "This username is already registered by an other user", "user_already_exist"]
        ]
)
def test_update_with_payload_error(client, monkeypatch, fake_user_list, log_user, id, username_exists, username, email, email_exists, err_status_code, err_msg, err_code, mocker):

    mocker.patch("src.auth.repository.UserRepository.get_user_by_email", side_effect=[User(**fake_user_list[1]), email_exists])

    def mock_check_username_exist(self, username):
        return username_exists
    
    monkeypatch.setattr(UserRepository, "is_username_already_taken", mock_check_username_exist)

    token = log_user
    fake_update_data ={
        "username":username,
        "email": email,
        "first_name":"dalsil",
        "last_name":"Irbaddrreche",
        "date_of_birth":"1993-10-12"
    }
    response = client.patch(f"/api/v1/auth/profile/{id}",content=json.dumps(fake_update_data), headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

def test_update_user_role(client, monkeypatch, log_admin, fake_user_list):
    token = log_admin
    def mock_get_by_id(self, user_id):
        return fake_user_list[2]
    
    monkeypatch.setattr(UserRepository, "get_user_by_id", mock_get_by_id)

    def mock_update(self, user_to_update, user_data):
        return fake_user_list[2]
    
    
    monkeypatch.setattr(UserRepository, "update_user", mock_update)

    response = client.patch("/api/v1/auth/profile/3/role_attribution",content= json.dumps({"role": "content_creator"}), headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200

@pytest.mark.parametrize(
    "id, token, role, err_status_code, err_msg, err_code",
    [
        [0,"log_admin", "wrong_role",422, "This role doesnt exists", "role_not_found"],
        [1,"log_user","content_creator",403,"Roles ['admin'] are required","insufficient_permission"],
        [0, "log_admin", "content_creator", 404, "No user with this id exists", "user_not_found"]
    ]
)
def test_update_user_role_with_errors(client, monkeypatch, fake_user_list, token, id, role, err_status_code, err_msg, err_code, request):
    token = request.getfixturevalue(token)

    def mock_get_current_user_by_email(self, user_email):
        return User(**fake_user_list[id])
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get_current_user_by_email)
    
    def mock_get_user_to_update_by_id(self, user_id):
        return None
    
    monkeypatch.setattr(UserRepository, "get_user_by_id",mock_get_user_to_update_by_id)
    response = client.patch("/api/v1/auth/profile/300000/role_attribution",content= json.dumps({"role": role}), headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == err_status_code
    assert response.json()["initial_details"]["error_code"] == err_code
    assert response.json()["info"]["error"] == err_msg

def test_verify_user(client, monkeypatch, verify_token, not_verified_fake_user, verified_fake_user):
    def mock_get_user_by_email(self, user_email):
        return not_verified_fake_user
    
    monkeypatch.setattr(UserRepository,"get_user_by_email", mock_get_user_by_email)

    def mock_update_user(self, user_to_update, user_data):
        return verified_fake_user
    monkeypatch.setattr(UserRepository,"update_user", mock_update_user)
    
    token = verify_token
    response = client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 202
    assert response.json()["message"] == "User successfully verified"
    token_data = UrlSerializer.decode_url_safe_token(token)
    assert token_data.get("email") == verified_fake_user.email
    assert verified_fake_user.is_verified == True

@pytest.mark.parametrize(
        "token, user, err_status_code, err_msg, err_code",
        [
            ["A", "not_verified_fake_user", 417, "Can't access user email from token verification", "user_verification_failed"],
            ["verify_token",None, 404, "The user with this email doesnt exists", "user_not_found"]
        ]
)
def test_verify_user_with_error(client, monkeypatch, token, user, err_status_code, err_msg, err_code, request):
    if len(token) > 1:
        token = request.getfixturevalue(token)

    if user is not None:
        user = request.getfixturevalue(user)

    def mock_get_user_by_email(self, user_email):
        return user
    monkeypatch.setattr(UserRepository,"get_user_by_email", mock_get_user_by_email)
    
    response = client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == err_status_code
    assert response.json()["info"]["error"] == err_msg
    assert response.json()["initial_details"]["error_code"] == err_code

def test_password_reset_request(client, monkeypatch, verify_token, verified_fake_user):
    def mock_create_message(user_email, subject):
        return {"ok":"Alright"}
    
    monkeypatch.setattr(MailSender,"create_message", mock_create_message)

    token = verify_token

    response = client.post("/api/v1/auth/password_reset_request", content=json.dumps({"email": verified_fake_user.email}))
    token_data = UrlSerializer.decode_url_safe_token(token)
    assert token_data.get("email")== verified_fake_user.email
    assert response.status_code == 200
    assert response.json()["message"] == "Check your emails to reset your password"


def test_password_reset_confirm(client, monkeypatch, verify_token, verified_fake_user, valid_password_data, verified_fake_user_with_new_password):
    token = verify_token
    def mock_get_user_by_email(self, user_email):
        return verified_fake_user
    monkeypatch.setattr(UserRepository, "get_user_by_email", mock_get_user_by_email)

    def mock_update_user(self, user_to_update, user_data):
        return verified_fake_user_with_new_password
    monkeypatch.setattr(UserRepository, "update_user", mock_update_user)

    response = client.post(f"/api/v1/auth/password_reset_confirm/{token}", content=json.dumps(valid_password_data))

    token_data = UrlSerializer.decode_url_safe_token(token)

    assert response.status_code == 200
    assert response.json()["message"] == "Password successfully reset"
    assert token_data.get("email") == verified_fake_user_with_new_password.email
    assert verified_fake_user_with_new_password.password_hash != verified_fake_user.password_hash

@pytest.mark.parametrize(
    "token,password_data, user, err_status_code, err_msg, err_code",
    [
        ["A", "valid_password_data", "not_verified_fake_user", 417, "Can't access user email from token verification", "user_verification_failed"],
        ["verify_token", "invalid_password_data", "not_verified_fake_user", 400, "Wrong credentials", "password_reset_dont_match"],
        ["verify_token","valid_password_data", None, 404, "The user with this email doesnt exists", "user_not_found"]
    ]
)
def test_password_reset_confrim_with_errors(client, monkeypatch, token, user, err_status_code, err_msg, err_code, request, password_data):
    if len(token) > 1:
        token = request.getfixturevalue(token)

    if user is not None:
        user = request.getfixturevalue(user)

    password_data = request.getfixturevalue(password_data)

    def mock_get_user_by_email(self, user_email):
        return user
    monkeypatch.setattr(UserRepository,"get_user_by_email", mock_get_user_by_email)

    response = client.post(f"/api/v1/auth/password_reset_confirm/{token}", content=json.dumps(password_data))
    assert response.status_code == err_status_code 
    assert response.json()["info"]["error"]== err_msg
    assert response.json()["initial_details"]["error_code"] == err_code


