from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import schemas, models
from auth import get_password_hash, get_user_by_token
import util.user_checks as checks
from util.common import responses

def hash_request(request: schemas.UserCreate|dict) -> dict:
    if type(request) is dict: request_dict = request.copy()
    else: request_dict = request.dict()
    request_dict['hashed_password'] = get_password_hash(request_dict.pop('password'))
    return request_dict

# Routes
router = APIRouter(prefix = '/user', tags = ['users'])

@router.post('/', status_code = status.HTTP_201_CREATED, response_model = schemas.UserRead,
    responses = checks.responses['duplicate'])
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    dbUsers = db.query(models.User)
    checks.duplicate_username(request.username, dbUsers)
    checks.duplicate_email(request.email, dbUsers)
    new_user = models.User(**hash_request(request))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/', response_model = List[schemas.UserRead],
    responses = responses['unauthenticated'] | checks.responses['admin'])
def get_all_users(db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)): #limit: int = 10, skip: int = 0): # Pagination
    checks.admin(user)
    return db.query(models.User).all() #.offset(skip).limit(limit).all() # Pagination

@router.get('/me', response_model = schemas.UserRead,
    responses = responses['unauthenticated'])
def get_user_me(user: models.User = Depends(get_user_by_token)):
    return user

@router.get('/{id}', response_model = schemas.UserRead,
    responses = responses['unauthenticated'] | checks.responses['exists'] | checks.responses['me_or_admin'])
def get_user_by_id(id: int, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    target = db.query(models.User).get(id)
    checks.exists_user(target)
    checks.me_or_admin(user, id)
    return target

@router.put('/{id}', response_model = schemas.UserRead,
    responses = responses['unauthenticated'] | checks.responses['exists'] | checks.responses['me_or_admin'] | checks.responses['duplicate'])
def update_user(id: int, request: schemas.UserUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    dbUsers = db.query(models.User)
    querySet = dbUsers.filter(models.User.id == id)
    target = querySet.first()
    checks.exists_user(target)
    checks.me_or_admin(user, id)
    if request.username: checks.duplicate_username(request.username, dbUsers)
    if request.email: checks.duplicate_email(request.email, dbUsers)
    querySet.update(hash_request(request))
    db.commit()
    db.refresh(target)
    return target

@router.delete('/{id}', status_code = status.HTTP_204_NO_CONTENT,
    responses = responses['unauthenticated'] | checks.responses['exists'] | checks.responses['me_or_admin'])
def delete_user(id: int, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    target = db.query(models.User).get(id)
    checks.exists_user(target)
    checks.me_or_admin(user, id)
    db.delete(target)
    db.commit()
    return