import os
import matplotlib
import requests

matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def formato_miles(ax, eje="y"):
    """Muestra los ticks del eje con separador de miles y sin notación científica."""
    formateador = FuncFormatter(lambda valor, _: f"{valor:,.0f}")
    if eje == "y":
        ax.yaxis.set_major_formatter(formateador)
    else:
        ax.xaxis.set_major_formatter(formateador)


def marcar_fuera_de_escala(ax, desde, hasta, nota, color="#c0392b"):
    """Sombrea un periodo con valores fuera del tope del eje y lo explica con una nota."""
    ax.axvspan(desde - 0.5, hasta + 0.5, color=color, alpha=0.10, zorder=0)
    ax.text(0.985, 0.96, nota, transform=ax.transAxes, va="top", ha="right",
            fontsize=8, color=color,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor=color, alpha=0.9), zorder=6)


def mostrar_grafico(fig, titulo="Presiona ESC para cerrar la gráfica"):
    """Muestra la figura maximizada (pantalla completa) para verla completa sin moverla.
    Permite cerrarla con Escape (o con la X) y volver al menú."""
    def al_presionar_tecla(event):
        if event.key == "escape":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", al_presionar_tecla)
    try:
        fig.canvas.manager.set_window_title(titulo)
    except Exception:
        pass

    # Maximizar la ventana para que la gráfica se vea completa desde el inicio
    try:
        ventana = fig.canvas.manager.window
        try:
            if os.name == 'nt':
                ventana.state('zoomed')            # Windows: maximizar
            else:
                ventana.attributes('-zoomed', True)  # Linux: maximizar
        except Exception:
            # Respaldo: ocupar toda la pantalla
            ventana.geometry(f"{ventana.winfo_screenwidth()}x{ventana.winfo_screenheight()}+0+0")
        ventana.lift()
        ventana.focus_force()
    except Exception:
        pass

    plt.show()
    plt.close("all")


def hacer_peticion(url, metodo="GET", datos=None, params=None, headers=None, timeout=5):
    try:
        respuesta = requests.request(
            method=metodo, url=url, json=datos,
            params=params, headers=headers, timeout=timeout,
        )
        respuesta.raise_for_status()
        return respuesta.json() if respuesta.content else None
    except requests.exceptions.HTTPError as err:
        print(f"Error HTTP ({respuesta.status_code}): {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error de conexión o tiempo de espera: {err}")
    return None
