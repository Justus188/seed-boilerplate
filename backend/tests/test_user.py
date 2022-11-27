from fastapi import status
from fastapi.testclient import TestClient
from pytest import raises
from typing import List

from sqlalchemy.orm import Session

from main import app
from database import get_db
import models
from tests.fixtures import get_testing_db, db, header1
from tests.seed import userwrite_json

app.dependency_overrides[get_db] = get_testing_db

client = TestClient(app)

def asserts_schema_UserRead(response_dict: dict, input_dict: dict, id: int):
    assert response_dict['username'] == input_dict['username']
    assert response_dict['email'] == input_dict['email']
    assert response_dict['role'] == input_dict['role']
    assert response_dict['id'] == id
    assert response_dict['created_at']
    with raises(KeyError): response_dict['password']

def asserts_db_user(dbuser: models.User, input_dict: dict):
    assert dbuser
    assert dbuser.username == input_dict['username']
    assert dbuser.email == input_dict['email']
    assert dbuser.role == input_dict['role']
    assert dbuser.hashed_password != input_dict['password']

def asserts_exception_duplicate_username(response, username: str):
    assert response.status_code == 400
    assert response.json()['detail'][0]['loc'] == ['body', 'username']
    assert response.json()['detail'][0]['msg'] == f'Username {username} already taken.'

def asserts_exception_duplicate_email(response, email: str):
    assert response.status_code == 400
    assert response.json()['detail'][0]['loc'] == ['body', 'email']
    assert response.json()['detail'][0]['msg'] == f'Email {email} already has an account.'

def asserts_execption_user_not_found(response):
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found.'

def asserts_exception_unauthenticated(response):
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'

def asserts_exception_unauthorized(response, allow_me: bool = False):
    if allow_me:
        assert response.status_code == 403
        assert response.json()['detail'][0]['msg'] == 'Only admin or target user can access this.'
    else:
        assert response.status_code == 403
        assert response.json()['detail'][0]['msg'] == 'Only admin can access this.'

def test_create_user_success(db: Session):
    user_json = userwrite_json(1)
    response = client.post("/user/", json=user_json)
    assert response.status_code == status.HTTP_201_CREATED
    asserts_schema_UserRead(response.json(), user_json, 1)
    asserts_db_user(db.query(models.User).get(1), user_json)

def test_create_user_email_constraint(db: Session):
    response = client.post("/user/", json=userwrite_json(1, email='invalid'))
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'value is not a valid email address'

def test_create_user_duplicate_username(db: Session):
    username = 'duplicate'
    client.post("/user/", json=userwrite_json(1, username=username))
    response = client.post("/user/", json=userwrite_json(1, username=username))
    asserts_exception_duplicate_username(response, username)

def test_create_user_duplicate_email(db: Session):
    email = 'duplicate@company.com'
    client.post("/user/", json=userwrite_json(1, email=email))
    response = client.post("/user/", json=userwrite_json(2, email=email))
    asserts_exception_duplicate_email(response, email)

def test_get_all_users(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=userwrite_json(2))
    response = client.get("/user/", headers = header1)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_all_users_unauthenticated(db: Session):
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=userwrite_json(2))
    response = client.get("/user/")
    asserts_exception_unauthenticated(response)

def test_get_all_users_unauthorized(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    client.post("/user/", json=userwrite_json(2, role = 'admin'))
    response = client.get("/user/", headers = header1)
    asserts_exception_unauthorized(response)

def test_get_user_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    response = client.get("/user/me", headers = header1)
    assert response.status_code == 200
    asserts_schema_UserRead(response.json(), user_json, 1)

def test_get_user_me_unauthenticated(db: Session):
    response = client.get("/user/me")
    asserts_exception_unauthenticated(response)

def test_get_user_by_id_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    response = client.get("/user/1", headers = header1)
    assert response.status_code == 200
    asserts_schema_UserRead(response.json(), user_json, 1)

def test_get_user_by_id_admin(db: Session, header1: dict):
    user_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=user_json)
    response = client.get("/user/2", headers = header1)
    asserts_schema_UserRead(response.json(), user_json, 2)

def test_get_user_by_id_unauthenticated(db: Session):
    client.post("/user/", json=userwrite_json(1))
    response = client.get("/user/1")
    asserts_exception_unauthenticated(response)

def test_get_user_by_id_unauthorized(db: Session, header1: dict):
    target_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=target_json)
    response = client.get("/user/2", headers = header1)
    asserts_exception_unauthorized(response, allow_me = True)

def test_update_user_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    update_json = userwrite_json(2)
    response = client.put("/user/1", json=update_json, headers = header1)
    assert response.status_code == 200
    asserts_schema_UserRead(response.json(), update_json, 1)
    asserts_db_user(db.query(models.User).get(1), update_json)

def test_update_user_admin(db: Session, header1: dict):
    user_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=user_json)
    update_json = userwrite_json(3)
    response = client.put("/user/2", json=update_json, headers = header1)
    assert response.status_code == 200
    asserts_schema_UserRead(response.json(), update_json, 2)
    asserts_db_user(db.query(models.User).get(2), update_json)

def test_update_user_unauthenticated(db: Session):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    update_json = userwrite_json(2)
    response = client.put("/user/1", json=update_json)
    asserts_exception_unauthenticated(response)

def test_update_user_unauthorized(db: Session, header1: dict):
    target_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=target_json)
    update_json = userwrite_json(3)
    response = client.put("/user/2", json=update_json, headers = header1)
    asserts_exception_unauthorized(response, allow_me = True)

def test_update_user_me_duplicate_username(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=userwrite_json(2, username = 'duplicate'))
    update_json = userwrite_json(3, username = 'duplicate')
    response = client.put("/user/1", json=update_json, headers = header1)
    asserts_exception_duplicate_username(response, update_json['username'])

def test_update_user_me_duplicate_email(db: Session, header1: dict):
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=userwrite_json(2, email = 'duplicate@company.com'))
    update_json = userwrite_json(3, email = 'duplicate@company.com')
    response = client.put("/user/1", json=update_json, headers = header1)
    asserts_exception_duplicate_email(response, update_json['email'])

def test_delete_user_me(db: Session, header1: dict):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json, headers = header1)
    response = client.delete("/user/1", headers = header1)
    assert response.status_code == 204
    assert db.query(models.User).get(1) == None

def test_delete_user_admin(db: Session, header1: dict):
    user_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1, role = 'admin'))
    client.post("/user/", json=user_json)
    response = client.delete("/user/2", headers = header1)
    assert response.status_code == 204
    assert db.query(models.User).get(2) == None

def test_delete_user_unauthenticated(db: Session):
    user_json = userwrite_json(1)
    client.post("/user/", json=user_json)
    response = client.delete("/user/1")
    asserts_exception_unauthenticated(response)

def test_delete_user_unauthorized(db: Session, header1: dict):
    target_json = userwrite_json(2)
    client.post("/user/", json=userwrite_json(1))
    client.post("/user/", json=target_json)
    response = client.delete("/user/2", headers = header1)
    asserts_exception_unauthorized(response, allow_me = True)