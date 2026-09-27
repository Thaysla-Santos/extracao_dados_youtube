# YouTube Metrics

Aplicação web que analisa vídeos do YouTube: busca estatísticas (views, likes) pela YouTube Data API e classifica o sentimento dos comentários (positivo, neutro, negativo) com um modelo de IA, exibindo o resultado em gráficos.

Em produção: [youtubemetrics.com.br](https://youtubemetrics.com.br)

## Funcionalidades

- **Análise por canal:** informe o nome do canal e são analisados os 2 vídeos mais recentes (opcionalmente ignorando vídeos com menos de 3 minutos).
- **Comparação de vídeos:** informe até 2 links (`watch?v=`, `youtu.be/` ou `shorts/`).
- **Sentimento dos comentários:** até 200 comentários por vídeo, classificados com o modelo [`cardiffnlp/twitter-xlm-roberta-base-sentiment`](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment). O texto dos comentários não é armazenado.
- **Gráficos:** engajamento (likes x views) e distribuição de sentimentos, gerados com Matplotlib.

## Stack

- Python 3.12, Flask, Gunicorn
- Google API Python Client (YouTube Data API v3)
- Hugging Face Transformers + PyTorch
- Matplotlib
- Docker / Docker Compose, com Traefik como proxy reverso em produção

## Estrutura

```
backend/
├── main.py              # App Flask, rotas e integração com a API do YouTube
├── analise.py           # Gráfico de engajamento
├── comentarios.py       # Gráfico de sentimentos
├── templates/           # index.html e privacidade.html
├── static/              # CSS, JS, fontes e imagens
├── requirements.txt     # Dependências da aplicação
├── requirements-ml.txt  # Dependências de ML (torch, transformers)
└── Dockerfile
docker-compose.yml
```

## Configuração

Crie um arquivo `.env` na raiz com sua chave da [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com):

```
YOUTUBE_API_KEY=sua_chave_aqui
```

## Como rodar

### Com Docker (recomendado)

O `docker-compose.yml` usa a rede externa `traefik`. Se ela ainda não existir, crie-a uma vez:

```bash
docker network create traefik
```

Para rodar localmente em `http://localhost:5000`:

```bash
docker compose build
docker compose run --rm --name youtube-local -p 5000:5000 app
```

Em produção (atrás do Traefik):

```bash
docker compose up -d --build
```

### Sem Docker

A partir da raiz do projeto:

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements-ml.txt -r backend/requirements.txt
export YOUTUBE_API_KEY=sua_chave_aqui
python -m backend.main
```

Na primeira execução o modelo de sentimento (~1 GB) é baixado do Hugging Face.

## Rotas

- `GET /`: página inicial.
- `POST /analisar`: recebe `canal` ou `link_video_1`/`link_video_2` e retorna JSON com os vídeos e os gráficos em base64.
- `GET /privacidade`: política de privacidade.
