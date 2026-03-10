FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities and service code
COPY shared/ /app/shared/
COPY auth-service/ /app/auth-service/

WORKDIR /app/auth-service

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
