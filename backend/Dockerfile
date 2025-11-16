# app/Dockerfile
FROM python:3.10

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/ /app/frontend/
RUN chmod +x start.sh

EXPOSE 8000

WORKDIR /app
ENTRYPOINT ["sh", "./backend/start.sh"]
