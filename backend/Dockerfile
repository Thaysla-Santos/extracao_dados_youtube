# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

ENV HF_HOME=/root/.cache/huggingface

# Camada pesada e estável: PyTorch, Transformers etc.
COPY backend/requirements-ml.txt ./requirements-ml.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-ml.txt

# Modelo baixado uma vez; não refaz se só requirements.txt mudar.
RUN --mount=type=cache,target=/root/.cache/huggingface \
    python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-xlm-roberta-base-sentiment')"

# Dependências leves da aplicação (Flask, Google API, MySQL etc.).
COPY backend/requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY backend/ ./backend/

ENV PYTHONPATH=/app

EXPOSE 5000

# --preload carrega o modelo uma vez antes de bifurcar os workers.
# -t 300 porque a inferência sobre os comentários passa dos 30s padrão.
CMD ["gunicorn", "--preload", "-w", "1", "--threads", "2", \
     "-t", "300", "-b", "0.0.0.0:5000", "backend.main:app"]
