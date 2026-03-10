FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities and gateway code
COPY shared/ /app/shared/
COPY gateway/ /app/gateway/

WORKDIR /app/gateway

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
