import os
import matplotlib
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import pandas as pd
import matplotlib.pyplot as plt
from config import DATOS
from utils import mostrar_grafico

def obtener_formacion_fija_capital_fijo():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Formación bruta de capital fijo (USD).csv")).sort_values("year")
    reciente = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(reciente["year"], reciente["finv_USD"], color="#1f618d")
    axes[0].set_title("Formación Bruta de Capital Fijo (2018 – 2025)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    df["ma5"] = df["finv_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["finv_USD"], label="Anual", color="#1f618d")
    axes[1].plot(df["year"], df["ma5"], linestyle="--", label="Media móvil 5 años", color="#c0392b")
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2025, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)