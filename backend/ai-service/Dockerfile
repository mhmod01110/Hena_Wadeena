FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV HF_HOME=/app/.cache/huggingface
ENV HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface/hub
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY ai-service/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ai-service/ /app/ai-service/

WORKDIR /app/ai-service

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --shell /usr/sbin/nologin --no-create-home appuser \
    && mkdir -p /app/.cache/huggingface/hub /app/.cache/huggingface/transformers \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8010

CMD ["python", "docker/wait_for_services.py"]
