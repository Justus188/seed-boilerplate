from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

from config import settings

def create_sqlalchemy_url_engine_session(type: str, database: str, host: str|None = None, port: str|None = None, username: str|None = None, password: str|None = None):
    if type not in ['sqlite', 'mysql', 'postgresql']:
        raise ValueError('Invalid database type')

    if type == 'sqlite':
        sqlalchemy_url = f'sqlite:///{database}'
        engine = create_engine(sqlalchemy_url, connect_args = {'check_same_thread': False})
    else:
        if not host or not port or not username or not password:
            raise ValueError('Invalid database credentials')

        if type == 'mysql':
            type = 'mysql+pymysql'
        
        sqlalchemy_url = f'{type}://{username}:{password}@{host}:{port}/{database}'
        engine = create_engine(sqlalchemy_url)

    SessionLocal = sessionmaker(bind = engine, autocommit = False, autoflush = False)

    def db_generator() -> Generator:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return sqlalchemy_url, engine, SessionLocal, db_generator
    
sqlalchemy_url, engine, SessionLocal, get_db = create_sqlalchemy_url_engine_session(**settings.db.dict())

Base = declarative_base()