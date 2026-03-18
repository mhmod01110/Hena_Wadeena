FROM python:3.11-slim

WORKDIR /app

COPY admin-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY admin-service/ /app/admin-service/

WORKDIR /app/admin-service

EXPOSE 8011

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]
