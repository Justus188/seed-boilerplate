Setup
- Switch vsc to cmd to allow conda to work
- Remember to cd to the correct root directory

Environment variables
- Pydantic `config.py` takes relative path
- Docker compose automatically checks for .env file
- To allow shared .env between docker-compose and backend, any docker build for backend must be called from root.

Virtual environment
- Create: Conda: `conda create --name venv_name --file requirments.txt` or just package=version
- Activate: Conda: `activate venv_name`, pip-venv: `venv_name\Scripts\activate`
- Install packages: `conda install pkgname` or `conda install -c conda-forge pkgname`
- Export:
    - Pip: requirements.txt: `pip list --format=freeze > requirements.txt`
    - Conda: env.yml: `conda env export --from-history > env.yml`

Fastapi
- Install: `conda install -c conda-forge fastapi`
- Run server: `uvicorn main:app --reload`

Alembic - DB version control
- Note: config was done in `env.py`, not `alembic.ini`
- Create version: `alembic revision --autogenerate -m version_name`
  - Checks `models.Base` for changes to cached DB structure, generates "versions" which function as diffs to up/downgrade
- Upgrade (version can use unique string or relative indexes, latest = "head"): `alembic upgrade version`
- Downgrade: `alembic downgrade version`

Docker
- Remember to start docker desktop before doing anything
- Build image (current directory = .): `docker build -t image_name directory`
- Start container: `docker run -d --name container_name -p host_port:container_port image_name`
- List containers: `docker ps -q`
- Kill container: `docker kill container_name`
- Remove container after force-stopping: `docker rm -f container_name`
- Remove all stopped containers: `docker system prune`

Docker-compose
- Docker-compose allows containers to access each others' internal environment by using containername as the host.
  - Therefore DB__HOST = database for docker-compose, but DB__HOST = localhost for local testing.
- Build: `docker-compose build`
- Build + Start: `docker-compose up -d`
- See all related containers: `docker-compose ps`
- Stop: `docker-compose down`
  - Remove volumes with `-v` if you edit anything to update

Security
- Generate random secret key: `openssl rand -hex 32`

Pytest
- `python -m pytest`

Deployment on EC2
- Linuz, T2.micro, Keypair is seed_boilerplate.pem
1. Open cmd in .pem folder
2. Copy line from "SSH client" in instance and run to connect to ssh
3. `sudo apt update`
4. `sudo apt install nginx`
5. Check if nginx is running - check the public ip for EC2
  - Change https to http  
6. `sudo apt install docker`
7. `sudo apt install docker-compose`
8. `git clone <github_link> <folder_name>`
  - Private repo is a pita, don't do it
9. `sudo docker-compose up -d`
10. `sudo docker exec <folder_name>-backend alembic upgrade head`
11. `sudo vim /etc/nginx/sites-available/default`
  - i to edit the file
  - at location: change `try_files $uri $uri/ =404;` to `proxy_pass http://127.0.0.1:8000/;`
12. `sudo systemctl restart nginx`
13. Check website
14. Begin debugging for one hour
  - Can try `sudo systemctl status`