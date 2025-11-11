# app/Dockerfile
FROM python:3.10

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 8000

WORKDIR /app
ENTRYPOINT ["sh", "./backend/start.sh"]
