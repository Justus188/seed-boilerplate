from pytest import fixture

from models import Base
from database import create_sqlalchemy_url_engine_session
from auth.token import create_token

testing_sqlalchemy_url, engine, TestingSessionLocal, get_testing_db = create_sqlalchemy_url_engine_session(type = 'sqlite', database = 'test.db')

@fixture
def db():
    Base.metadata.create_all(bind = engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind = engine)

@fixture
def header1():
    token = create_token({'sub': 1})
    return {'Authorization': f'Bearer {token}'}