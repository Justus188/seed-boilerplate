from fastapi import HTTPException, status

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

FailedLoginException = HTTPException(status_code = status.HTTP_200_OK, detail = 'Invalid credentials')