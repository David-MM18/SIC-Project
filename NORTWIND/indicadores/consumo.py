import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from config import DATOS
from utils import mostrar_grafico, formato_miles, marcar_fuera_de_escala


matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux


def obtener_consumo_familiar():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Consumo familiar en USD.csv")).sort_values("year")
    rec = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["hcons_USD"], color="#27ae60")
    axes[0].set_title("Consumo Familiar en USD (2018 – 2024)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    df["ma5"] = df["hcons_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["hcons_USD"], label="Anual", color="#1f618d")
    axes[1].plot(df["year"], df["ma5"], linestyle="--", label="Media móvil 5 años", color="#d35400")
    axes[1].set_ylim(0, 382_000)
    marcar_fuera_de_escala(axes[1], 2015, 2017, "2015–2017 fuera de escala · máx. 17 927 096")
    axes[1].set_title("Trayectoria Histórica (1950 – 2024)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend(loc="upper left")

    formato_miles(axes[0])
    formato_miles(axes[1])

    plt.tight_layout()
    mostrar_grafico(fig)


def obtener_consumo_hogares():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Consumo de los hogares (% del PIB).csv")).sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    df["ma5"] = df["hcons_GDP"].rolling(5).mean()

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["hcons_GDP"], color="#16a085")
    axes[0].set_title("Consumo de los Hogares (% del PIB) [2000 – 2024]")
    axes[0].set_ylabel("% del PIB")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    axes[1].plot(df["year"], df["hcons_GDP"], label="Anual", color="#1f4e78")
    axes[1].plot(df["year"], df["ma5"], linestyle="--", label="Media móvil 5 años", color="#c0392b")
    axes[1].set_title("Trayectoria Histórica (1950 – 2024)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("% del PIB")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)


def obtener_consumo_gobierno():
    df = pd.read_csv(os.path.join(DATOS, "datos_economicos", "Consumo gubernamental.csv")).sort_values("year")
    rec = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["gcons_USD"], color="#5b2c6f")
    axes[0].set_title("Consumo Gubernamental (2018 – 2024)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    df["ma5"] = df["gcons_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["gcons_USD"], label="Anual", color="#1f4e78")
    axes[1].plot(df["year"], df["ma5"], linestyle="--", label="Media móvil 5 años", color="#c0392b")
    axes[1].set_ylim(0, 74_000)
    marcar_fuera_de_escala(axes[1], 2015, 2017, "2015–2017 fuera de escala · máx. 1 812 251")
    axes[1].set_title("Trayectoria Histórica (1950 – 2024)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend(loc="upper left")

    formato_miles(axes[0])
    formato_miles(axes[1])

    plt.tight_layout()
    mostrar_grafico(fig)
