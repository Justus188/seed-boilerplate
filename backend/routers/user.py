from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import schemas, models
from auth.hash import get_password_hash
from auth.oauth2 import get_user_by_token

router = APIRouter(prefix = '/user', tags = ['users'])

@router.post('/', status_code = status.HTTP_202_ACCEPTED, response_model = schemas.UserCreate)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    # Post: Duplicate check
    dbUsers = db.query(models.User)
    if dbUsers.filter(models.User.username == request.username).first():
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = {'detail': f'Username {request.username} already taken.'})
    if dbUsers.filter(models.User.email == request.email).first():
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = {'detail': f'Email {request.email} already has an account. Please log in instead.'})
    # Role check - skipped
    # Do
    request_dict = request.dict()
    #   Hash password
    request_dict['hashed_password'] = get_password_hash(request_dict.pop('password'))
    new_user = models.User(**request_dict)
    #   Post
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/', response_model = List[schemas.UserReadAdmin])
def get_all_users(db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    # Get all
    # Role check
    if user.role != 'admin':
        raise HTTPException(statys_code = status.HTTP_403_FORBIDDEN, detail = {'detail': 'Only admin can access this.'})
    # Do
    #   Get
    return db.query(models.User).all()

@router.get('/me', response_model = schemas.UserRead)
def get_user_me(user: models.User = Depends(get_user_by_token)):
    return user

@router.get('/{id}', response_model = schemas.UserRead)
def get_user_by_id(id: int, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    # Get specific: Existence check
    target = db.query(models.User).get(id)
    if not target:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = {'detail': f'User with id {id} not found.'})
    # Role check
    if user.role != 'admin' and user.id == id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = {'detail': f'Only the user {user.username} or admin can access this.'})
    # Do
    #   Get
    return target

@router.put('/{id}', response_model = schemas.UserRead)
def update_user(id: int, request: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    # Put: Existence check
    target = db.query(models.User).get(id)
    if not target:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = {'detail': f'User with id {id} not found.'})
    # Role check
    if user.role != 'admin' and user.id == id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = {'detail': f'Only the user {user.username} or admin can access this.'})
    # Do
    #   Hash password
    request_dict = request.dict()
    request_dict['hashed_password'] = get_password_hash(request_dict.pop('password'))
    #   Put
    target.update(**request.dict())
    db.commit()
    db.refresh(target)
    return target

@router.delete('/{id}', status_code = status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), user: models.User = Depends(get_user_by_token)):
    # Delete: Existence check
    target = db.query(models.User).get(id)
    if not target:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = {'detail': f'User with id {id} not found.'})
    # Role check
    if user.role != 'admin' and user.id == id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = {'detail': f'Only the user {user.username} or admin can access this.'})
    # Do
    #   Delete
    db.delete(target)
    db.commit()
    return