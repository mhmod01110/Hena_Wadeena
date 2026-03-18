FROM python:3.11-slim

WORKDIR /app

COPY market-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY market-service/ /app/market-service/

WORKDIR /app/market-service

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
