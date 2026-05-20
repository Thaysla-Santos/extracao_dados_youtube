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
positivos = []
negativos = []
neutros = []

for v in videos:

    titulos.append(v["titulo"][:20])

    positivos.append(v["sentimentos"]["positive"])
    negativos.append(v["sentimentos"]["negative"])
    neutros.append(v["sentimentos"]["neutral"])

# =========================
# DATAFRAME
# =========================

df = pd.DataFrame({
    "Vídeo": titulos,
    "Positivos": positivos,
    "Neutros": neutros,
    "Negativos": negativos
})

# =========================
# EXIBIR COMPARATIVO
# =========================

print("\n========== COMPARATIVO DOS SENTIMENTOS ==========\n")

print(df)

# =========================
# IDENTIFICAR PREDOMINÂNCIA
# =========================

print("\n========== ANÁLISE DOS VÍDEOS ==========\n")

for i in range(len(df)):

    video = df["Vídeo"][i]

    positivo = df["Positivos"][i]
    neutro = df["Neutros"][i]
    negativo = df["Negativos"][i]

    # identifica maior sentimento
    if positivo > neutro and positivo > negativo:

        resultado = "Predominância POSITIVA"

    elif negativo > positivo and negativo > neutro:

        resultado = "Predominância NEGATIVA"

    else:

        resultado = "Predominância NEUTRA"

    print(f"{video} -> {resultado}")

# =========================
# POSIÇÕES DAS BARRAS
# =========================

x = np.arange(len(titulos))
largura = 0.25

# =========================
# GRÁFICO
# =========================

plt.figure(figsize=(16, 8))

# barras positivas
barra_positivos = plt.bar(
    x - largura,
    positivos,
    width=largura,
    label="Positivos",
    color="green"
)

# barras neutras
barra_neutros = plt.bar(
    x,
    neutros,
    width=largura,
    label="Neutros",
    color="blue"
)

# barras negativas
barra_negativos = plt.bar(
    x + largura,
    negativos,
    width=largura,
    label="Negativos",
    color="red"
)

# =========================
# VALORES NAS BARRAS
# =========================

def adicionar_valores(barras):

    for barra in barras:

        altura = barra.get_height()

        plt.text(
            barra.get_x() + barra.get_width()/2,
            altura + 0.1,
            str(int(altura)),
            ha='center',
            va='bottom',
            fontsize=9
        )

adicionar_valores(barra_positivos)
adicionar_valores(barra_neutros)
adicionar_valores(barra_negativos)

# =========================
# CONFIGURAÇÕES
# =========================

plt.xticks(
    x,
    titulos,
    rotation=20
)

plt.xlabel("Vídeos")
plt.ylabel("Quantidade de Comentários")

plt.title("Comparativo de Comentários por Sentimento")

plt.legend()

plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()

plt.show()