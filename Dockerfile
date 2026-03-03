FROM python:3.11-slim
WORKDIR /app
RUN pip install pika fastapi uvicorn psycopg2-binary

