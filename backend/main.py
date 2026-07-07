import os
import isodate
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, render_template, request
from transformers import pipeline
from googleapiclient.discovery import build

from backend.analise import gerar_grafico_engajamento
from backend.comentarios import gerar_grafico_sentimentos

app = Flask(__name__)

# ==========================================
# SUA API KEY DO YOUTUBE
# ==========================================

api_key = os.environ.get("YOUTUBE_API_KEY")
if not api_key:
    raise RuntimeError("Defina a variável YOUTUBE_API_KEY")

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

def analisar_canal(nome_canal, ignorar_curtos=True):

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


    videosBusca = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order="date",
        maxResults=20
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

        comentariosLista = []

        videoId = v["id"]["videoId"]

        titulo = v["snippet"]["title"]

        # estatísticas do vídeo
        estatisticas = youtube.videos().list(
            part="statistics, contentDetails",
            id=videoId
        ).execute()

        duracao = estatisticas["items"][0]["contentDetails"]["duration"]
        duracao = isodate.parse_duration(duracao)
        duracao = duracao.total_seconds()
        
        if ignorar_curtos and duracao < 180:
            continue

        try:

            comentariosBusca = youtube.commentThreads().list(
                part="snippet",
                videoId=videoId,
                maxResults=200
            ).execute()

            for c in comentariosBusca["items"]:

                snippet = c["snippet"]["topLevelComment"]["snippet"]

                texto = snippet["textOriginal"]
                autor = snippet.get("authorDisplayName", "")

                sentimento = analisador(texto)[0]

                quantidadeComentarios += 1
                scoreComentarios += sentimento["score"]

                if sentimento["label"] == "positive":

                    labelComentarios["positive"] += 1
                    sentimentoLabel = "positive"

                elif sentimento["label"] == "neutral":

                    labelComentarios["neutral"] += 1
                    sentimentoLabel = "neutral"

                else:

                    labelComentarios["negative"] += 1
                    sentimentoLabel = "negative"

                comentariosLista.append({
                    "autor": autor,
                    "texto": texto,
                    "sentimento": sentimentoLabel,
                    "score": sentimento["score"]
                })

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

            "sentimentos": labelComentarios,

            "comentarios": comentariosLista,
        })

        if(len(videos) >= 2):
            break
    
    return {"videos": videos}

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
    ignorar_curtos = request.form.get("ignorar_curtos") == "1"

    dados = analisar_canal(nome_canal, ignorar_curtos)
    if "erro" in dados:

        return jsonify({"erro": dados["erro"]}), 404

    grafico_engajamento = gerar_grafico_engajamento(dados["videos"])
    grafico_sentimentos = gerar_grafico_sentimentos(dados["videos"])

    return jsonify({
        "videos": dados["videos"],
        "grafico_engajamento": grafico_engajamento,
        "grafico_sentimentos": grafico_sentimentos
    })

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)