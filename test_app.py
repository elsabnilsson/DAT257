import pytest
from main import app 

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def login_session(client):
    with client.session_transaction() as sess:
        sess["user_uid"] = "mock-user-uid-hugo"


def test_profie_page(client):
    login_session(client)
    response = client.get("/profile")
    assert response.status_code == 200


def test_register_page(client):
    login_session(client)
    response = client.get("/register")
    assert response.status_code == 200

def test_register_form_post(client):
    login_session(client)
    response = client.post("/register", data={
        "age": 25,
        "height": 175,
        "weight": 70,
        "gender": "male",
        "activity": "active"
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_page(client):
    login_session(client)
    response = client.get("/")
    assert response.status_code == 200

def test_status_page(client):
    login_session(client)
    response = client.get("/stats")
    assert response.status_code == 200

def test_recipes_page(client):
    login_session(client)
    response = client.get("/recipes")
    assert response.status_code == 200

def test_workouts_page(client):
    login_session(client)
    response = client.get("/workouts")
    assert response.status_code == 200
