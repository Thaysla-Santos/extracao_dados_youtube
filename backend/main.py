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

    canal = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    if not canal["items"]:
        return {"erro": "Canal não encontrado"}

    uploads_id = canal["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videosBusca = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_id,
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

        videoId = v["snippet"]["resourceId"]["videoId"]

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

                # O texto serve apenas para classificar e é descartado em
                # seguida. Nenhum dado pessoal entra no resultado.
                texto = snippet["textOriginal"]

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

            "sentimentos": labelComentarios,
        })

        if(len(videos) >= 2):
            break
    
    return {"videos": videos}


def analisar_videos(link_video_1, link_video_2):

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    videos = []

    for link in [link_video_1, link_video_2]:

        if link == "":
            continue

        if "v=" in link:
            videoId = link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in link:
            videoId = link.split("youtu.be/")[1].split("?")[0]
        elif "shorts/" in link:
            videoId = link.split("shorts/")[1].split("?")[0].split("/")[0]
        else:
            videoId = link.strip()

        quantidadeComentarios = 0
        scoreComentarios = 0

        labelComentarios = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        estatisticas = youtube.videos().list(
            part="statistics, contentDetails, snippet",
            id=videoId
        ).execute()

        if not estatisticas["items"]:
            continue

        titulo = estatisticas["items"][0]["snippet"]["title"]

        try:

            comentariosBusca = youtube.commentThreads().list(
                part="snippet",
                videoId=videoId,
                maxResults=200
            ).execute()

            for c in comentariosBusca["items"]:

                snippet = c["snippet"]["topLevelComment"]["snippet"]

                # O texto serve apenas para classificar e é descartado em
                # seguida. Nenhum dado pessoal entra no resultado.
                texto = snippet["textOriginal"]

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
        })

    if not videos:

        return {
            "erro": "Vídeo não encontrado"
        }

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

    nome_canal = request.form.get("canal", "")
    link_video_1 = request.form.get("link_video_1", "")
    link_video_2 = request.form.get("link_video_2", "")
    ignorar_curtos = request.form.get("ignorar_curtos") == "1"

    if link_video_1 != "" or link_video_2 != "":
        dados = analisar_videos(link_video_1, link_video_2)
    else:
        dados = analisar_canal(nome_canal, ignorar_curtos)
    if "erro" in dados:
        return jsonify({"erro": dados["erro"]}), 404

    grafico_engajamento = gerar_grafico_engajamento(dados["videos"])
    grafico_sentimentos = gerar_grafico_sentimentos(dados["videos"])

    resposta = jsonify({
        "videos": dados["videos"],
        "grafico_engajamento": grafico_engajamento,
        "grafico_sentimentos": grafico_sentimentos
    })

    resposta.headers["Cache-Control"] = "no-store"

    return resposta

# ==========================================
# POLÍTICA DE PRIVACIDADE
# ==========================================

@app.route("/privacidade")
def privacidade():

    return render_template("privacidade.html")

# ==========================================
# INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)