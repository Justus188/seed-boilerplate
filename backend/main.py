from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.wsgi import WSGIMiddleware # Mount other api on this one

# from database import engine # DB management outsourced to alembic
# from models import Base # DB management outsourced to alembic
import auth
from routers import user
from config import settings

app = FastAPI(**settings.openapi_metadata.dict())

# Cross-origin resource sharing, use allow_orgin_regex as needed
    # Origins are unique combinations of protocol [http/s]://domain:port
    # Allows same origin as backend by default, else configure middleware
app.add_middleware(CORSMiddleware, allow_credentials = True, allow_methods = ['*'], allow_headers = ['*'],
    allow_origins = ["https://localhost:8000"])

# Base.metadata.create_all(engine) # DB management outsourced to alembic

app.include_router(auth.router)
app.include_router(user.router)

@app.get('/')
async def root():
    return {'message': 'Root'}

# app.mount('/flask', WSGIMiddleware(flaskapp)) # Mount: Access the flaskapp api at localhost:8000/flask/