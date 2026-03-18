FROM python:3.11-slim

WORKDIR /app

COPY analytics-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY analytics-service/ /app/analytics-service/

WORKDIR /app/analytics-service

EXPOSE 8012

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8012"]
