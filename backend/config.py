from pydantic import BaseSettings, BaseModel
from dotenv import find_dotenv

class DbArgs(BaseModel):
    type: str = 'sqlite' # sqlite | mysql | postgresql
    host: str | None
    port: int | None
    username: str | None
    password: str | None
    database: str = 'db.db' # sqlite: file name

class OpenAPIMetadata(BaseModel):
    title: str = 'FastAPI'
    version: str = '0.1.0'
    description: str = 'API description'

class Settings(BaseSettings):
    db: DbArgs

    secret_key: str = 'secret'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 7 * 24 * 60 # 7 days

    openapi_metadata: OpenAPIMetadata

    class Config:
        env_file = find_dotenv(usecwd = True)
        env_nested_delimiter = '__'

settings = Settings()