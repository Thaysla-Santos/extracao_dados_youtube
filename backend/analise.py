import io
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# =========================
# PALETA (tema dark)
# =========================

COR_TEXTO          = "#f5f5f7"
COR_TEXTO_MUTED    = "#a0a0b0"
COR_GRID           = "#2a2a3a"
COR_POSITIVO       = "#22c55e"
COR_NEGATIVO       = "#ef4444"
COR_NEUTRO_BARRA   = "#6b6b80"
COR_VIEWS          = "#3b82f6"


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def gerar_grafico_engajamento(videos, mostrar=False):

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
            cor = COR_POSITIVO

        elif negativos > positivos:
            cor = COR_NEGATIVO

        else:
            cor = COR_NEUTRO_BARRA

        titulo = v["titulo"]

        if len(titulo) > 28:
            titulo = titulo[:25] + "..."

        titulos.append(titulo)
        likes.append(like)
        views.append(view)
        cores.append(cor)

    # =========================
    # POSIÇÕES DAS BARRAS
    # =========================

    x = np.arange(len(titulos))
    largura = 0.35

    # =========================
    # GRÁFICO
    # =========================

    fig, ax = plt.subplots(figsize=(10, 5), dpi=110)

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # barras de likes
    ax.bar(
        x - largura / 2,
        likes,
        width=largura,
        label="Likes",
        color=cores,
        edgecolor="none"
    )

    # barras de views
    ax.bar(
        x + largura / 2,
        views,
        width=largura,
        label="Views",
        color=COR_VIEWS,
        edgecolor="none",
        alpha=0.9
    )

    # =========================
    # CONFIGURAÇÕES
    # =========================

    ax.set_xticks(x)

    ax.set_xticklabels(
        titulos,
        rotation=12,
        color=COR_TEXTO_MUTED,
        fontsize=9
    )

    ax.tick_params(
        axis="y",
        colors=COR_TEXTO_MUTED,
        labelsize=9
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xlabel(
        "Vídeos",
        color=COR_TEXTO_MUTED,
        fontsize=10,
        labelpad=8
    )

    ax.set_ylabel(
        "Quantidade",
        color=COR_TEXTO_MUTED,
        fontsize=10,
        labelpad=8
    )

    ax.legend(
        facecolor="#14141c",
        edgecolor=COR_GRID,
        labelcolor=COR_TEXTO,
        fontsize=9,
        framealpha=0.9
    )

    ax.grid(
        axis="y",
        color=COR_GRID,
        linestyle="-",
        linewidth=0.6,
        alpha=0.7
    )

    ax.set_axisbelow(True)

    plt.tight_layout()

    # =========================
    # SAÍDA
    # =========================

    if mostrar:
        plt.show()
        plt.close(fig)
        return None

    buf = io.BytesIO()

    plt.savefig(
        buf,
        format="png",
        transparent=True,
        bbox_inches="tight"
    )

    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")
