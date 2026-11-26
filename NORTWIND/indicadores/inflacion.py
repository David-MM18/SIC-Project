import os
import pandas as pd
import matplotlib
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import matplotlib.pyplot as plt
from config import DATOS
from utils import mostrar_grafico

def obtener_inflacion():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "inflacion.csv"))
    df_rec = df[df["year"] >= 2000].sort_values("year")

    hist = df_rec[df_rec["forecast"] == 0]
    fcast = df_rec[df_rec["forecast"] == 1]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.plot(hist["year"], hist["infl"], marker="o", label="Histórico (forecast = 0)", color="#b22222")
    ax.plot(fcast["year"], fcast["infl"], marker="s", linestyle="--", label="Proyección (forecast = 1)", color="#e67e22")

    ax.set_yscale("log")
    ax.set_title("Inflación anual en Venezuela (desde 2000, escala logarítmica)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Inflación (%) [Escala log]")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend()
    plt.tight_layout()
    mostrar_grafico(fig)