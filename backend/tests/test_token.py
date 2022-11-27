from fastapi import HTTPException
from pytest import raises
from datetime import timedelta

from auth.token import create_token, decode_token

def test_create_token():
    original_id = 123
    token = create_token({'sub': original_id})
    assert token is not None
    assert token != {'sub': original_id}

def test_create_decode_token():
    original_id = 345
    userid = decode_token(create_token({'sub': original_id}))
    assert userid == original_id

def test_decode_token_expired():
    with raises(HTTPException):
        decode_token(create_token({'sub': 123}, expires_delta = timedelta(minutes = -1)))