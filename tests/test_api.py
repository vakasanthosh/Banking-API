from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    print(response.json())
    assert response.status_code == 200
    #assert response.json() == {
    #    "message": "Welcome to Banking API"
    #}

def test_register():
    response = client.post(
        "/register",
        json={
            "username": "pytestuser7",
            "mobile": "9876543217",
            "password": "Test@123"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Registration Successful"
    }

def test_login():
    response = client.post(
        "/login",
        data={
            "username": "pytestuser7",
            "password": "Test@123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_balance():
    #login getjwt token
    login_response = client.post(
        "/login",
        data = {
            "username":"pytestuser7",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/balance",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "pytestuser7"
    assert "balance" in data

def test_deposit():
    #Login and get JWT token
    login_response = client.post(
        "/login",
        data={
            "username": "pytestuser7",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    #Deposit money
    response = client.post(
        "/deposit",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "card_holder_name": "Py Test User",
            "card_number": "1234567812345678",
            "cvv": "123",
            "expiry_date": "12/30",
            "amount": 1000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "balance" in data

def test_withdraw():
    #Login and get JWT token
    login_response = client.post(
        "/login",
        data={
            "username": "pytestuser7",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    #withdraw money
    response = client.post(
        "/withdraw",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "amount": 500
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "balance" in data

def test_transfer():
    #Login and get JWT token
    login_response = client.post(
        "/login",
        data={
            "username": "pytestuser7",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    #transfer money
    response = client.post(
        "/transfer",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "receiver_mobile": "9876543220",
            "amount": 200
        }
    )
    print(response.status_code)
    print(response.json())

def test_transactions():
    #Login and get JWT token
    login_response = client.post(
        "/login",
        data={
            "username": "pytestuser7",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    #transfer money
    response = client.get(
        "/transactions",
        headers={
            "Authorization": f"Bearer {token}"
        },
        
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_unauthorized_balance():
    response = client.get("/balance")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_invalid_login():
    response = client.post(
        "/login",
        data={
            "username": "wronguser",
            "password": "WrongPassword123"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"