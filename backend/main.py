from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from database import engine
# from models import Base
from auth import oauth2
from routers import user

app = FastAPI()

# Cross-origin resource sharing, use allow_orgin_regex as needed
    # Origins are unique combinations of protocol [http/s]://domain:port
    # Allows same origin as backend by default, else configure middleware
app.add_middleware(CORSMiddleware, allow_credentials = True, allow_methods = ['*'], allow_headers = ['*'],
    allow_origins = ["https://localhost:8000"])

# Base.metadata.create_all(engine) # DB management outsourced to alembic

app.include_router(oauth2.router)
app.include_router(user.router)

@app.get('/')
async def root():
    return {'message': 'Root'}