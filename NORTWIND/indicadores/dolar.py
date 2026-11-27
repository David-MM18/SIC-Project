import pandas as pd
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from utils import hacer_peticion, mostrar_grafico


matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux


def obtener_historico_dolar():
    historico_dolar = hacer_peticion("https://ve.dolarapi.com/v1/historicos/dolares/oficial")
    df = pd.DataFrame(historico_dolar)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["promedio"] = pd.to_numeric(df["promedio"], errors="coerce")
    df = df.dropna(subset=["fecha", "promedio"]).sort_values("fecha")
    df = df[(df["fecha"] >= pd.Timestamp("2023-01-01")) & (df["fecha"] <= pd.Timestamp.today())]

    if "fuente" in df.columns:
        df_oficial = df[df["fuente"] == "oficial"]
        if not df_oficial.empty:
            df = df_oficial

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=150)
    ax.plot(df["fecha"], df["promedio"], linewidth=2, color="#1f4e78", label="Promedio (Bs./USD)")

    primer = df.iloc[0]
    ultimo = df.iloc[-1]
    ax.scatter([primer["fecha"], ultimo["fecha"]], [primer["promedio"], ultimo["promedio"]], color="#1f4e78", zorder=5)
    ax.annotate(f"Inicio: Bs. {primer['promedio']:,.2f}", xy=(primer["fecha"], primer["promedio"]), xytext=(10, 10), textcoords="offset points", fontsize=9, fontweight="bold")
    ax.annotate(f"Actual: Bs. {ultimo['promedio']:,.2f} ({ultimo['fecha'].strftime('%Y-%m-%d')})", xy=(ultimo["fecha"], ultimo["promedio"]), xytext=(-140, 12), textcoords="offset points", fontsize=9, fontweight="bold")

    ax.set_title("Promedio del Dólar (2023 – Actualidad)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Fecha", fontsize=11)
    ax.set_ylabel("Promedio (Bs. / USD)", fontsize=11)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right")
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig("promedio_dolar.png")
    mostrar_grafico(fig)