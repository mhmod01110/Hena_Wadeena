FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities and service code
COPY shared/ /app/shared/
COPY user-service/ /app/user-service/

WORKDIR /app/user-service

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
