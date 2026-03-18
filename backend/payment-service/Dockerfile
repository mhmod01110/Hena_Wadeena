FROM python:3.11-slim

WORKDIR /app

COPY payment-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY payment-service/ /app/payment-service/

WORKDIR /app/payment-service

EXPOSE 8007

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
