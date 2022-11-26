from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import settings

DB_TYPE = settings.db_type

match DB_TYPE:
    case 'sqlite':
        DB_URL = f'sqlite:///./{settings.sqlite_file}'
    case 'mysql': 
        DB_URL = f'mysql+pymysql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    case 'postgres':
        DB_URL = f'postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'

if DB_TYPE == 'sqlite':
    engine = create_engine(DB_URL, connect_args = {'check_same_thread': False}) #connect_args only for sqlite
else:
    engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind = engine, autocommit = False, autoflush = False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()