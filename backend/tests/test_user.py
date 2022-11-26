from fastapi import status
from fastapi.testclient import TestClient
from pytest import raises

from sqlalchemy.orm import Session

from main import app
from database import get_db
import models
from tests.util import get_testing_db, db

app.dependency_overrides[get_db] = get_testing_db

client = TestClient(app)

def userwrite_json(id: int, username: str|None = None, email: str|None = None, password: str|None = None, role: str|None = None):
    if not username:
        username = f'user{id}'
    if not email:
        email = f'user{id}@company.com'
    if not password:
        password = 'password'
    if not role:
        role = 'customer'
    if role not in ['customer', 'admin']:
        raise ValueError('Invalid role')
    return {"username":username, "email":email, "password":password, "role":role}

def test_create_user_success(db: Session):
    user_json = userwrite_json(1)
    response = client.post("/user/", json=user_json)
    assert response.status_code == status.HTTP_201_CREATED
    response_dict = response.json()
    assert response_dict['username'] == user_json['username']
    assert response_dict['email'] == user_json['email']
    assert response_dict['role'] == user_json['role']
    assert response_dict['id'] == 1
    assert response_dict['created_at']
    with raises(KeyError): response_dict['password']
    assert db.query(models.User).filter(models.User.username == user_json['username']).first().hashed_password != user_json['password']

def test_create_user_email_constraint(db: Session):
    response = client.post("/user/", json=userwrite_json(1, email='invalid'))
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'value is not a valid email address'

def test_create_user_duplicate_username(db: Session):
    username = 'duplicate'
    client.post("/user/", json=userwrite_json(1, username=username))
    response = client.post("/user/", json=userwrite_json(1, username=username))
    assert response.status_code == 400
    assert response.json()['detail'][0]['loc'] == ['body', 'username']
    assert response.json()['detail'][0]['msg'] == f'Username {username} already taken.'

def test_create_user_duplicate_email(db: Session):
    email = 'duplicate@company.com'
    client.post("/user/", json=userwrite_json(1, email=email))
    response = client.post("/user/", json=userwrite_json(2, email=email))
    assert response.status_code == 400
    assert response.json()['detail'][0]['loc'] == ['body', 'email']
    assert response.json()['detail'][0]['msg'] == f'Email {email} already has an account.'

def test_get_all_users(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=userwrite_json(2))
    response = client.get("/user/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_all_users_unauthenticated(db: Session):
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=userwrite_json(2))
    response = client.get("/user/")
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'

def test_get_all_users_unauthorized(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=userwrite_json(2, role = 'admin'))
    response = client.get("/user/")
    assert response.status_code == 403
    assert response.json()['detail'][0]['msg'] == 'Only admin can access this.'

def test_get_user_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    response = client.get("/user/me", headers = header1)
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['username'] == user_json['username']
    assert response.json()['email'] == user_json['email']
    assert response.json()['role'] == user_json['role']
    assert response.json()['created_at']
    with raises(KeyError): response.json()['password']

def test_get_user_me_unauthenticated(db: Session):
    response = client.get("/user/me")
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'

def test_get_user_by_id_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['username'] == user_json['username']
    assert response.json()['email'] == user_json['email']
    assert response.json()['role'] == user_json['role']
    assert response.json()['created_at']
    with raises(KeyError): response.json()['password']

def test_get_user_by_id_admin(db: Session, header1: dict):
    user_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=user_json)
    response = client.get("/user/2", headers = header1)
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['username'] == user_json['username']
    assert response.json()['email'] == user_json['email']
    assert response.json()['role'] == user_json['role']
    assert response.json()['created_at']
    with raises(KeyError): response.json()['password']

def test_get_user_by_id_unauthenticated(db: Session):
    client.post("/user/", json=userwrite_json(1))
    response = client.get("/user/1")
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'

def test_get_user_by_id_unauthorized(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=userwrite_json(2))
    response = client.get("/user/2", headers = header1)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Not authorized'