import matplotlib
import requests
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import matplotlib.pyplot as plt

def mostrar_grafico(fig, titulo="Presiona ESC para cerrar la gráfica"):
    """Muestra la figura y permite cerrarla con Escape (o con la X)."""
    def al_presionar_tecla(event):
        if event.key == "escape":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", al_presionar_tecla)
    try:
        fig.canvas.manager.set_window_title(titulo)
        fig.canvas.get_tk_widget().focus_force()
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