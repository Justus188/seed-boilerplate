from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

from auth.hash import verify_password_hash
from auth.schemas import Token
from auth.token import create_token, decode_token
from auth.exceptions import CredentialsException, FailedLoginException

PATH_AUTH = '/login'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = PATH_AUTH[1:])

def get_user_by_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).get(decode_token(token))
    if not user:
        raise CredentialsException
    return user

router = APIRouter(tags = ['auth'])

@router.post(PATH_AUTH, response_model = Token)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise FailedLoginException
    if not verify_password_hash(request.password, user.hashed_password):
        raise FailedLoginException
    return {'access_token': create_token({"sub": user.id}), 'token_type': 'bearer'}