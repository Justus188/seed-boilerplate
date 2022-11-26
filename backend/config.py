from pydantic import BaseSettings

class Settings(BaseSettings):
    db_type: str # sqlite | mysql | postgres
    db_host: str | None
    db_port: str | None
    db_username: str | None
    db_password: str | None
    db_name: str | None

    sqlite_file: str | None

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = '.env'

settings = Settings()