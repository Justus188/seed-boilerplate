Boilerplate for SEED 2022

For .env to be shared by docker-compose and backend, project has been designed such that docker build needs to be run from root.

Backend: Fastapi
- Built-in Swagger UI docs (Change metadata at metadata_docs.py)
- Database credentials and hashing setting set in `.env`: create using config.py pydantic model
- JWT oauth2 security
- Alembic DB versioning
- Dockerized
- Pytest /user route test suite