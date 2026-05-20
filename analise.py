import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================
# LER JSON
# =========================

with open("dados.json", "r", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

videos = dados["videos"]

# =========================
# PREPARAR DADOS
# =========================

titulos = []
likes = []
views = []
cores = []

for v in videos:

    like = int(v["estatisticas"].get("likeCount", 0))
    view = int(v["estatisticas"].get("viewCount", 0))

    positivos = v["sentimentos"]["positive"]
    negativos = v["sentimentos"]["negative"]

    # cor baseada no sentimento
    if positivos > negativos:
        cor = "green"

    elif negativos > positivos:
        cor = "red"

    else:
        cor = "gray"

    titulos.append(v["titulo"][:20])
    likes.append(like)
    views.append(view)
    cores.append(cor)

# =========================
# POSIÇÕES DAS BARRAS
# =========================

x = np.arange(len(titulos))
largura = 0.35

# =========================
# GRÁFICO DE BARRAS
# =========================

plt.figure(figsize=(16, 8))

# barras de likes
plt.bar(
    x - largura/2,
    likes,
    width=largura,
    label="Likes",
    color=cores,
    alpha=0.8
)

# barras de views
plt.bar(
    x + largura/2,
    views,
    width=largura,
    label="Views",
    color="skyblue",
    alpha=0.8
)

# =========================
# CONFIGURAÇÕES
# =========================

plt.xticks(
    x,
    titulos,
    rotation=20
)

plt.xlabel("Vídeos")
plt.ylabel("Quantidade")

plt.title("Engajamento dos Vídeos do YouTube")

plt.legend()

plt.grid(axis="y")

plt.tight_layout()

plt.show()