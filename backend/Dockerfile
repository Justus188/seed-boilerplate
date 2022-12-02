FROM python:3.10-slim
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY .env .env
COPY ./backend .
CMD ["/bin/bash", "-c", "./startup.sh"]