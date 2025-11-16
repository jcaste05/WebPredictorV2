# app/Dockerfile
FROM python:3.10

WORKDIR /app/backend

RUN echo "== Build context PWD ==" && pwd && \
    echo "== Listado nivel 1 ==" && ls -1 && \
    echo "== Árbol corto ==" && find . -maxdepth 2 -type f -printf '%p\n' | head -n 40


COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/ /app/frontend/
RUN chmod +x start.sh

EXPOSE 8000

WORKDIR /app
ENTRYPOINT ["sh", "./backend/start.sh"]
