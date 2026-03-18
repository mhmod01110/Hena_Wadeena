FROM python:3.11-slim

WORKDIR /app

COPY media-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY media-service/ /app/media-service/

WORKDIR /app/media-service

EXPOSE 8013

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8013"]
