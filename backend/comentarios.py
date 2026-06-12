import io
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# =========================
# PALETA (tema dark)
# =========================

COR_TEXTO       = "#f5f5f7"
COR_TEXTO_MUTED = "#a0a0b0"
COR_GRID        = "#2a2a3a"
COR_POSITIVO    = "#22c55e"
COR_NEUTRO      = "#facc15"
COR_NEGATIVO    = "#ef4444"


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def gerar_grafico_sentimentos(videos, mostrar=False):

    titulos = []
    positivos = []
    negativos = []
    neutros = []

    for v in videos:

        titulo = v["titulo"]

        if len(titulo) > 28:
            titulo = titulo[:25] + "..."

        titulos.append(titulo)

        positivos.append(v["sentimentos"]["positive"])
        negativos.append(v["sentimentos"]["negative"])
        neutros.append(v["sentimentos"]["neutral"])

    # =========================
    # POSIÇÕES DAS BARRAS
    # =========================

    x = np.arange(len(titulos))
    largura = 0.25

    # =========================
    # GRÁFICO
    # =========================

    fig, ax = plt.subplots(figsize=(10, 5), dpi=110)

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # barras positivas
    barra_positivos = ax.bar(
        x - largura,
        positivos,
        width=largura,
        label="Positivos",
        color=COR_POSITIVO,
        edgecolor="none"
    )

    # barras neutras
    barra_neutros = ax.bar(
        x,
        neutros,
        width=largura,
        label="Neutros",
        color=COR_NEUTRO,
        edgecolor="none"
    )

    # barras negativas
    barra_negativos = ax.bar(
        x + largura,
        negativos,
        width=largura,
        label="Negativos",
        color=COR_NEGATIVO,
        edgecolor="none"
    )

    # =========================
    # VALORES NAS BARRAS
    # =========================

    def adicionar_valores(barras):

        for barra in barras:

            altura = barra.get_height()

            if altura <= 0:
                continue

            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 0.4,
                str(int(altura)),
                ha="center",
                va="bottom",
                fontsize=8,
                color=COR_TEXTO
            )

    adicionar_valores(barra_positivos)
    adicionar_valores(barra_neutros)
    adicionar_valores(barra_negativos)

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
        "Quantidade de Comentários",
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
