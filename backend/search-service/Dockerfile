FROM python:3.11-slim

WORKDIR /app

COPY search-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY search-service/ /app/search-service/

WORKDIR /app/search-service

EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
