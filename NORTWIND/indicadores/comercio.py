
import os
import matplotlib
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import pandas as pd
import matplotlib.pyplot as plt
from config import DATOS
from utils import mostrar_grafico

def obtener_importaciones():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Importaciones en USD.csv")).sort_values("year")
    rec = df[df["year"] >= 2018].copy()
    df_hist = df[df["year"] >= 1950].copy()
    df_hist["ma5"] = df_hist["imports_USD"].rolling(5).mean()

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["imports_USD"], color="#2874a6")
    axes[0].set_title("Importaciones en USD (2018 – 2027)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    axes[1].plot(df_hist["year"], df_hist["imports_USD"], label="Anual", color="#1f4e78")
    axes[1].plot(df_hist["year"], df_hist["ma5"], linestyle="--", label="Media móvil 5 años", color="#c0392b")
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2027, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)

def importaciones_pbi():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Importaciones (% del PIB).csv")).sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    hist = rec[rec["forecast"] == 0]
    fcast = rec[rec["forecast"] == 1]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(hist["year"], hist["imports_GDP"], color="#2874a6", label="Histórico (forecast = 0)")
    axes[0].bar(fcast["year"], fcast["imports_GDP"], color="#e67e22", hatch="//", label="Proyección (forecast = 1)")
    axes[0].set_title("Importaciones (% del PIB) [2000 – 2027]")
    axes[0].set_ylabel("% del PIB")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)
    axes[0].legend()

    df_hist = df[df["year"] >= 1950].copy()
    df_hist["ma5"] = df_hist["imports_GDP"].rolling(5).mean()
    axes[1].plot(df_hist["year"], df_hist["imports_GDP"], label="Anual", color="#1f4e78")
    axes[1].plot(df_hist["year"], df_hist["ma5"], linestyle="--", label="Media móvil 5 años", color="#c0392b")
    axes[1].set_title("Trayectoria Histórica (1950 – 2027)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("% del PIB")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)