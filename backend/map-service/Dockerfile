FROM python:3.11-slim

WORKDIR /app

COPY map-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY map-service/ /app/map-service/

WORKDIR /app/map-service

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
