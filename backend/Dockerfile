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

CMD ["python", "-m", "backend.main"]
