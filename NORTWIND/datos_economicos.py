import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Rutas ancladas al propio archivo: funcionan sin importar desde qué
# carpeta se ejecute el script (terminal, VS Code, etc.)
BASE = Path(__file__).resolve().parent
DATOS_ECONOMICOS = BASE / "datos" / "datos_economicos"

def mostrar_grafico(fig, titulo="Presiona ESC para cerrar la gráfica"):
    """Muestra la figura y permite cerrarla con Escape (o con la X)."""
    def al_presionar_tecla(event):
        if event.key == "escape":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", al_presionar_tecla)
    try:
        fig.canvas.manager.set_window_title(titulo)
        fig.canvas.get_tk_widget().focus_force()  # solo backend Tk (default en Windows)
    except Exception:
        pass

    plt.show()        # se bloquea aquí hasta cerrar la ventana
    plt.close("all")  # libera memoria al volver al menú

def hacer_peticion(url, metodo="GET", datos=None, params=None, headers=None, timeout=5):
    try:
        respuesta = requests.request(
            method=metodo,
            url=url,
            json=datos,
            params=params,
            headers=headers,
            timeout=timeout,
        )
        respuesta.raise_for_status()
        return respuesta.json() if respuesta.content else None

    except requests.exceptions.HTTPError as err:
        print(f"Error HTTP ({respuesta.status_code}): {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error de conexión o tiempo de espera: {err}")

    return None

def obtener_historico_dolar():
    historico_dolar = hacer_peticion("https://ve.dolarapi.com/v1/historicos/dolares/oficial")
    df = pd.DataFrame(historico_dolar)
    # 2. Limpiar, convertir fechas y filtrar desde 2023 hasta hoy
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["promedio"] = pd.to_numeric(df["promedio"], errors="coerce")
    df = df.dropna(subset=["fecha", "promedio"]).sort_values("fecha")
    # Filtrar desde el 1 de enero de 2023 hasta la fecha actual
    df = df[
        (df["fecha"] >= pd.Timestamp("2023-01-01"))
        & (df["fecha"] <= pd.Timestamp.today())
    ]

    # Opcional: si tienes varias fuentes en el mismo JSON, filtra por "oficial"
    if "fuente" in df.columns:
      df_oficial = df[df["fuente"] == "oficial"]
      if not df_oficial.empty:
        df = df_oficial

    # 3. Graficar con Matplotlib
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=150)
    ax.plot(
        df["fecha"],
        df["promedio"],
        linewidth=2,
        color="#1f4e78",
        label="Promedio (Bs./USD)",
    )

    # Marcar valor inicial y último valor disponible
    primer = df.iloc[0]
    ultimo = df.iloc[-1]
    ax.scatter(
        [primer["fecha"], ultimo["fecha"]],
        [primer["promedio"], ultimo["promedio"]],
        color="#1f4e78",
        zorder=5,
    )
    ax.annotate(
        f"Inicio: Bs. {primer['promedio']:,.2f}",
        xy=(primer["fecha"], primer["promedio"]),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
    )
    ax.annotate(
        f"Actual: Bs. {ultimo['promedio']:,.2f} ({ultimo['fecha'].strftime('%Y-%m-%d')})",
        xy=(ultimo["fecha"], ultimo["promedio"]),
        xytext=(-140, 12),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
    )

    # Formato de ejes y diseño
    ax.set_title(
        "Promedio del Dólar (2023 – Actualidad)", fontsize=13, fontweight="bold"
    )
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
    
def obtener_inflacion():
    df = pd.read_csv(DATOS_ECONOMICOS / "inflacion.csv")
    df_rec = df[df["year"] >= 2000].sort_values("year")

    hist = df_rec[df_rec["forecast"] == 0]
    fcast = df_rec[df_rec["forecast"] == 1]
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.plot(
        hist["year"],
        hist["infl"],
        marker="o",
        label="Histórico (forecast = 0)",
        color="#b22222",
    )
    ax.plot(
        fcast["year"],
        fcast["infl"],
        marker="s",
        linestyle="--",
        label="Proyección (forecast = 1)",
        color="#e67e22",
    )
    
    ax.set_yscale("log")
    ax.set_title("Inflación anual en Venezuela (desde 2000, escala logarítmica)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Inflación (%) [Escala log]")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend()
    plt.tight_layout()
    mostrar_grafico(fig)    

def obtener_formacion_fija_capital_fijo():
    df = pd.read_csv(DATOS_ECONOMICOS / "Formación bruta de capital fijo (USD).csv").sort_values("year")
    # 1. Barras del tramo reciente (sin distorsión 2015-2017)
    reciente = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(reciente["year"], reciente["finv_USD"], color="#1f618d")
    axes[0].set_title("Formación Bruta de Capital Fijo (2018 – 2025)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    # 2. Serie histórica completa con media móvil y escala logarítmica
    df["ma5"] = df["finv_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["finv_USD"], label="Anual", color="#1f618d")
    axes[1].plot(
        df["year"],
        df["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#c0392b",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2025, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)
    
def obtener_consumo_familiar():
    df = pd.read_csv(DATOS_ECONOMICOS / "Consumo familiar en USD.csv").sort_values("year")
    rec = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["hcons_USD"], color="#27ae60")
    axes[0].set_title("Consumo Familiar en USD (2018 – 2024)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    df["ma5"] = df["hcons_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["hcons_USD"], label="Anual", color="#1f618d")
    axes[1].plot(
        df["year"],
        df["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#d35400",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2024, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)

def obtener_consumo_hogares():
    df = pd.read_csv(DATOS_ECONOMICOS / "Consumo de los hogares (% del PIB).csv").sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    df["ma5"] = df["hcons_GDP"].rolling(5).mean()

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["hcons_GDP"], color="#16a085")
    axes[0].set_title("Consumo de los Hogares (% del PIB) [2000 – 2024]")
    axes[0].set_ylabel("% del PIB")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    axes[1].plot(df["year"], df["hcons_GDP"], label="Anual", color="#1f4e78")
    axes[1].plot(
        df["year"],
        df["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#c0392b",
    )
    axes[1].set_title("Trayectoria Histórica (1950 – 2024)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("% del PIB")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)

def obtener_consumo_gobierno():
    df = pd.read_csv(DATOS_ECONOMICOS / "Consumo gubernamental.csv").sort_values("year")
    rec = df[df["year"] >= 2018]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["gcons_USD"], color="#5b2c6f")
    axes[0].set_title("Consumo Gubernamental (2018 – 2024)")
    axes[0].set_ylabel("Unidades de la serie")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    df["ma5"] = df["gcons_USD"].rolling(5).mean()
    axes[1].plot(df["year"], df["gcons_USD"], label="Anual", color="#1f4e78")
    axes[1].plot(
        df["year"],
        df["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#c0392b",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2024, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Unidades de la serie [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)

def obtener_pib_real():
    df = pd.read_csv(DATOS_ECONOMICOS / "pib real usd.csv").sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    rec["pct_change"] = rec["rGDP_pc_USD"].pct_change() * 100

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    # 1. Nivel reciente (2000 - 2025)
    axes[0].plot(
        rec["year"],
        rec["rGDP_pc_USD"],
        marker="o",
        color="#1f4e78",
        label="PIB real per cápita (USD)",
    )
    axes[0].set_title("PIB Real per Cápita en USD (2000 – 2025)")
    axes[0].set_ylabel("USD por persona")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()

    # 2. Variación interanual (%) reciente
    colores = [
        "#27ae60" if v >= 0 else "#c0392b" for v in rec["pct_change"].fillna(0)
    ]
    axes[1].bar(rec["year"], rec["pct_change"], color=colores)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Variación Anual del PIB Real per Cápita (%)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Variación (%)")
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    mostrar_grafico(fig)

def obtener_importaciones():
    df = pd.read_csv(DATOS_ECONOMICOS / "Importaciones en USD.csv").sort_values("year")
    rec = df[df["year"] >= 2018].copy()
    df_hist = df[df["year"] >= 1950].copy()
    df_hist["ma5"] = df_hist["imports_USD"].rolling(5).mean()

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(rec["year"], rec["imports_USD"], color="#2874a6")
    axes[0].set_title("Importaciones en USD (2018 – 2027)")
    axes[0].set_ylabel("Millones de USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    axes[1].plot(
        df_hist["year"], df_hist["imports_USD"], label="Anual", color="#1f4e78"
    )
    axes[1].plot(
        df_hist["year"],
        df_hist["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#c0392b",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("Trayectoria Histórica (1950 – 2027, escala logarítmica)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("Millones de USD [Log]")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)
    
def importaciones_pbi():
    df = pd.read_csv(DATOS_ECONOMICOS / "Importaciones (% del PIB).csv").sort_values("year")
    rec = df[df["year"] >= 2000].copy()
    hist = rec[rec["forecast"] == 0]
    fcast = rec[rec["forecast"] == 1]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=150)

    axes[0].bar(
        hist["year"],
        hist["imports_GDP"],
        color="#2874a6",
        label="Histórico (forecast = 0)",
    )
    axes[0].bar(
        fcast["year"],
        fcast["imports_GDP"],
        color="#e67e22",
        hatch="//",
        label="Proyección (forecast = 1)",
    )
    axes[0].set_title("Importaciones (% del PIB) [2000 – 2027]")
    axes[0].set_ylabel("% del PIB")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)
    axes[0].legend()

    df_hist = df[df["year"] >= 1950].copy()
    df_hist["ma5"] = df_hist["imports_GDP"].rolling(5).mean()
    axes[1].plot(
        df_hist["year"], df_hist["imports_GDP"], label="Anual", color="#1f4e78"
    )
    axes[1].plot(
        df_hist["year"],
        df_hist["ma5"],
        linestyle="--",
        label="Media móvil 5 años",
        color="#c0392b",
    )
    axes[1].set_title("Trayectoria Histórica (1950 – 2027)")
    axes[1].set_xlabel("Año")
    axes[1].set_ylabel("% del PIB")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    mostrar_grafico(fig)

def menu():
    opciones = {
        "1": ("Obtener histórico del dólar", obtener_historico_dolar),
        "2": ("Obtener inflación", obtener_inflacion),
        "3": ("Obtener formación bruta de capital fijo", obtener_formacion_fija_capital_fijo),
        "4": ("Obtener consumo familiar", obtener_consumo_familiar),
        "5": ("Obtener consumo de los hogares (% del PIB)", obtener_consumo_hogares),
        "6": ("Obtener consumo gubernamental", obtener_consumo_gobierno),
        "7": ("Obtener PIB real per cápita", obtener_pib_real),
        "8": ("Obtener importaciones en USD", obtener_importaciones),
        "9": ("Obtener importaciones (% del PIB)", importaciones_pbi),
        "0": ("Salir", None)
    }

    while True:
        print("\nMenú de opciones:")
        for clave, (descripcion, _) in opciones.items():
            print(f"{clave}. {descripcion}")
        
        eleccion = input("Seleccione una opción: ")
        
        if eleccion == "0":
            print("Saliendo del programa.")
            break
        elif eleccion in opciones:
            _, funcion = opciones[eleccion]
            if funcion:
                funcion()
        else:
            print("Opción no válida. Intente nuevamente.")
            
if __name__ == "__main__":
    menu()