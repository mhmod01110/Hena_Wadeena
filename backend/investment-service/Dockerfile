FROM python:3.11-slim

WORKDIR /app

COPY investment-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY investment-service/ /app/investment-service/

WORKDIR /app/investment-service

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
