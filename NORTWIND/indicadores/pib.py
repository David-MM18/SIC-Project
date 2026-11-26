import os
import pandas as pd
import matplotlib
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import matplotlib.pyplot as plt
from config import DATOS
from utils import mostrar_grafico

def obtener_pib_real():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "pib real usd.csv")).sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    rec["pct_change"] = rec["rGDP_pc_USD"].pct_change() * 100

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].plot(rec["year"], rec["rGDP_pc_USD"], marker="o", color="#1f4e78", label="PIB real per cápita (USD)")
    axes[0].set_title("PIB Real per Cápita en USD (2000 – 2025)")
    axes[0].set_ylabel("USD por persona")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()

    colores = ["#27ae60" if v >= 0 else "#c0392b" for v in rec["pct_change"].fillna(0)]
    axes[1].bar(rec["year"], rec["pct_change"], color=colores)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Variación Anual del PIB Real per Cápita (%)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Variación (%)")
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    mostrar_grafico(fig)