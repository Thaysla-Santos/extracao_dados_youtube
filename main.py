from flask import Flask, jsonify, render_template, request
from transformers import pipeline
from googleapiclient.discovery import build
import json

app = Flask(__name__)

# ==========================================
# SUA API KEY DO YOUTUBE
# ==========================================

api_key = "AIzaSyBZt1mlS3KyzAqCZ2-CC1y2cPk0XUXtG9U"

# ==========================================
# MODELO DE IA
# ==========================================

analisador = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-xlm-roberta-base-sentiment"
)

# ==========================================
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ==========================================

def analisar_canal(nome_canal):

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    # busca canal
    search = youtube.search().list(
        part="snippet",
        q=nome_canal,
        type="channel",
        maxResults=1
    ).execute()

    if not search["items"]:

        return {
            "erro": "Canal não encontrado"
        }

    channel_id = search["items"][0]["snippet"]["channelId"]

    # busca vídeos
    videosBusca = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order="date",
        maxResults=2
    ).execute()

    videos = []

    for v in videosBusca["items"]:

        quantidadeComentarios = 0
        scoreComentarios = 0

        labelComentarios = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        videoId = v["id"]["videoId"]

        titulo = v["snippet"]["title"]

        # estatísticas do vídeo
        estatisticas = youtube.videos().list(
            part="statistics",
            id=videoId
        ).execute()

        try:

            comentariosBusca = youtube.commentThreads().list(
                part="snippet",
                videoId=videoId,
                maxResults=200
            ).execute()

            for c in comentariosBusca["items"]:

                texto = c["snippet"]["topLevelComment"]["snippet"]["textOriginal"]

                sentimento = analisador(texto)[0]

                quantidadeComentarios += 1
                scoreComentarios += sentimento["score"]

                if sentimento["label"] == "positive":

                    labelComentarios["positive"] += 1

                elif sentimento["label"] == "neutral":

                    labelComentarios["neutral"] += 1

                else:

                    labelComentarios["negative"] += 1

        except:
            pass

        # evita divisão por zero
        if quantidadeComentarios > 0:

            scoreComentarios = (
                scoreComentarios / quantidadeComentarios
            )

        else:

            scoreComentarios = 0

        videos.append({

            "videoId": videoId,

            "titulo": titulo,

            "url": f"https://youtube.com/watch?v={videoId}",

            "estatisticas":
                estatisticas["items"][0]["statistics"],

            "scoreComentarios": scoreComentarios,

            "quantidadeComentarios":
                quantidadeComentarios,

            "sentimentos": labelComentarios
        })

    dados = {
        "videos": videos
    }

    # salva json
    with open(
        "dados.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    return dados

# ==========================================
# TELA INICIAL
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")

# ==========================================
# ROTA HTML
# ==========================================

@app.route("/analisar", methods=["POST"])
def analisar():

    nome_canal = request.form["canal"]

    dados = analisar_canal(nome_canal)

    if "erro" in dados:

        return render_template(
            "index.html",
            erro=dados["erro"]
        )

    return render_template(
        "index.html",
        videos=dados["videos"]
    )

# ==========================================
# ROTA JSON
# ==========================================

@app.route("/api/<nome_canal>")
def api(nome_canal):

    dados = analisar_canal(nome_canal)

    return jsonify(dados)

# ==========================================
# INICIAR SERVIDOR
# ==========================================

app.run(debug=True)