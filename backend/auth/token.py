from datetime import datetime, timedelta
from jose import JWTError, jwt

from config import settings

from auth.exceptions import CredentialsException

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)

def create_token(data: dict, expires_delta: timedelta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    # JWT subject must be string
    data['sub'] = str(data['sub'])
    # Claims: https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-hs256
    expire = datetime.utcnow() + expires_delta
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm = ALGORITHM)

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        # get other information from payload here
    except JWTError:
        raise CredentialsException
    try:
        userid = int(payload.get('sub'))
    except:
        raise CredentialsException
    return userid