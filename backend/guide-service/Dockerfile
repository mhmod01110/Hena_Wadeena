FROM python:3.11-slim

WORKDIR /app

COPY guide-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY guide-service/ /app/guide-service/

WORKDIR /app/guide-service

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
