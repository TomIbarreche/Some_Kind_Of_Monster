from src.auth.utils import MailSender, UrlSerializer


def test_create_user(client, fake_user_signup_data, monkeypatch):
    def mock_create_message(user_email, subject):
        return {"ok":"Alright"}
    
    monkeypatch.setattr(MailSender,"create_message", mock_create_message)

    response = client.post("/api/v1/auth/signup", json=fake_user_signup_data)
    data = response.json()
    assert response.status_code == 201
    assert data["message"] == "User successfully created. Check your email to verify your account"
    assert data["user"]["email"] == "fake@fake.fake"
    assert data["user"]["id"] == 2

def test_update_user_profile(client,fake_user_update_data, create_verify_connect_standard_user):
    cli = client.post("/api/v1/auth/login", json={"email": "ibarreche666@gmail.com", "password":"Admin123"})
    access_token = create_verify_connect_standard_user
    update_response = client.patch("/api/v1/auth/profile/2", json=fake_user_update_data, headers={"Authorization":f"Bearer {access_token}"})
    data = update_response.json()
    assert update_response.status_code == 200
    assert data["first_name"] == fake_user_update_data["first_name"]
    assert data["username"] == fake_user_update_data["username"]

def test_get_all_users(client, connect_admin, create_verify_connect_standard_user):
    user_token = create_verify_connect_standard_user
    token = connect_admin
    response  = client.get("/api/v1/auth/all", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()[0]["first_name"] == "Admin"
    assert response.json()[1]["email"] == "fake@fake.fake"
    assert len(response.json()) == 2

def test_get_user_by_id(client, create_verify_connect_standard_user):
    user_token = create_verify_connect_standard_user
    response = client.get("/api/v1/auth/profile/2")
    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["email"] == "fake@fake.fake"