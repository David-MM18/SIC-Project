# -*- coding: utf-8 -*-
"""
Menú interactivo de gráficos Northwind
---------------------------------------
Ejecutar en terminal:   python menu.py

- Selecciona una opción del menú con el número correspondiente.
- Se abre la gráfica (o tabla) en una ventana.
- Presiona ESC dentro de la ventana para volver al menú.
- Selecciona 0 para salir del programa.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Consola en UTF-8 para mostrar bien tildes y ñ (Windows)
if os.name == 'nt':
    try:
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(BASE, 'datos')        # Carpeta con los CSV de Northwind
GRAFICOS = os.path.join(BASE, 'gráficos')  # Carpeta donde se guardan las imágenes

os.makedirs(GRAFICOS, exist_ok=True)

# Que los signos $ se muestren literal (y no como fórmula matemática)
plt.rcParams['text.parse_math'] = False


# ---------------------------------------------------------------------------
# 1. CARGA DE DATOS
# ---------------------------------------------------------------------------
def cargar_datos():
    def leer(nombre):
        return pd.read_csv(os.path.join(DATOS, nombre), sep=';')

    employees = leer('Employees.csv')
    employees['Empleado'] = employees['FirstName'] + ' ' + employees['LastName']

    rewards = leer('Rewards.csv')
    rewards = rewards.dropna(subset=['EmployeeID']).copy()
    rewards['EmployeeID'] = rewards['EmployeeID'].astype(int)

    dfs = {
        'orders': leer('Orders.csv'),
        'order_details': leer('OrderDetails.csv'),
        'employees': employees,
        'products': leer('Products.csv'),
        'categories': leer('Categories.csv'),
        'customers': leer('Customers.csv'),
        'shippers': leer('Shippers.csv'),
        'rewards': rewards,
    }
    dfs['orders']['OrderDate'] = pd.to_datetime(
        dfs['orders']['OrderDate'], errors='coerce')
    return dfs


# ---------------------------------------------------------------------------
# 2. ENRIQUECER OrderDetails CON PRECIO -> LineTotal
# ---------------------------------------------------------------------------
def enriquecer_order_details(dfs):
    od = dfs['order_details'].merge(
        dfs['products'][['ProductID', 'ProductName', 'Price',
                         'CategoryID', 'SupplierID']],
        on='ProductID', how='left')
    od['LineTotal'] = od['Quantity'] * od['Price']
    return od


# ---------------------------------------------------------------------------
# 3. DATAFRAME MAESTRO (df_full)
# ---------------------------------------------------------------------------
def construir_df_full(dfs, od):
    df_full = (od
               .merge(dfs['orders'], on='OrderID', how='left')
               .merge(dfs['customers'], on='CustomerID', how='left')
               .merge(dfs['employees'][['EmployeeID', 'FirstName', 'LastName']],
                      on='EmployeeID', how='left')
               .merge(dfs['categories'], on='CategoryID', how='left')
               .merge(dfs['shippers'], on='ShipperID', how='left'))
    df_full['EmployeeName'] = df_full['FirstName'] + ' ' + df_full['LastName']
    return df_full


# ---------------------------------------------------------------------------
# 4. CÁLCULOS DE LOS TOP 4
# ---------------------------------------------------------------------------
def calcular_top_ordenes(dfs):
    """Top empleados que más órdenes cerraron."""
    conteo = dfs['orders'].groupby('EmployeeID').size()
    df = dfs['employees'][['EmployeeID', 'Empleado']].copy()
    df['TotalVentas'] = df['EmployeeID'].map(conteo).fillna(0).astype(int)
    df = df.sort_values('TotalVentas', ascending=True)[['Empleado', 'TotalVentas']]
    return df


def calcular_top_productos(dfs):
    """Top 10 productos más vendidos (por unidades)."""
    df = dfs['order_details'].merge(
        dfs['products'][['ProductID', 'ProductName']], on='ProductID')
    df = df.groupby('ProductName', as_index=False).agg(
        UnidadesVendidas=('Quantity', 'sum'))
    df = df.nlargest(10, 'UnidadesVendidas')[['ProductName', 'UnidadesVendidas']]
    return df.sort_values('UnidadesVendidas')


def calcular_top_beneficio(dfs):
    """Top 10 productos con mayor beneficio ($)."""
    df = dfs['order_details'].merge(dfs['products'], on='ProductID')
    df = df.groupby('ProductName', as_index=False).agg(
        {'Quantity': 'sum', 'Price': 'first'})
    df['TotalBeneficio'] = df['Quantity'] * df['Price']
    df = df.nlargest(10, 'TotalBeneficio')[['ProductName', 'TotalBeneficio']]
    return df.sort_values('TotalBeneficio')


def calcular_top_recaudado(dfs):
    """Top empleados que más dinero recaudaron hasta ahora."""
    df = dfs['employees'].merge(dfs['orders'], on='EmployeeID', how='left')
    df = df.merge(dfs['order_details'], on='OrderID', how='left')
    df = df.merge(dfs['products'], on='ProductID', how='left')
    df['TotalRecaudado'] = df['Quantity'] * df['Price']
    df = df.groupby(['EmployeeID', 'Empleado'], as_index=False)[
        ['TotalRecaudado']].sum()
    df = df.sort_values('TotalRecaudado', ascending=True)[
        ['Empleado', 'TotalRecaudado']]
    return df


# ---------------------------------------------------------------------------
# 5. CONSTRUCCIÓN DE GRÁFICOS DE BARRAS
# ---------------------------------------------------------------------------
def _hint(fig):
    fig.text(0.5, 0.01, '>> Presiona ESC para volver al menú <<',
             ha='center', fontsize=10, style='italic', color='gray')


def crear_grafico(df, titulo, tono, xlabel, ylabel, filename=None,
                  vertical=False):
    col0, col1 = df.columns
    fig, ax = plt.subplots(figsize=(10, 5.5))

    if vertical:
        # Barras verticales (xlabel = categoría, ylabel = valor)
        df.plot(x=col0, y=col1, kind='bar', ax=ax, legend=False, color=tono)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)
        # Margen superior para las etiquetas rotadas
        ax.set_ylim(0, df[col1].max() * 1.18)
        for cont in ax.containers:
            ax.bar_label(cont, fmt='{:,.0f}', rotation=90, padding=3,
                         fontsize=8)
    else:
        # Barras horizontales
        df.plot(x=col0, y=col1, kind='barh', ax=ax, legend=False, color=tono)
        ax.grid(axis='x', alpha=0.3)
        for cont in ax.containers:
            ax.bar_label(cont, fmt='{:,.0f}', padding=3, fontsize=9)

    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    _hint(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    if filename:
        fig.savefig(os.path.join(GRAFICOS, filename), dpi=150,
                    bbox_inches='tight')
    return fig


# ---------------------------------------------------------------------------
# 6. CONSTRUCTORES DE CADA OPCIÓN DEL MENÚ
# ---------------------------------------------------------------------------
# --- TOP 4 -----------------------------------------------------------------
def op_top_ordenes(ctx):
    df = calcular_top_ordenes(ctx['dfs'])
    return crear_grafico(df, 'Empleados Que Más Órdenes Cerraron', 'orange',
                         'Órdenes Cerradas', 'Empleado', 'TopVendedores.png')


def op_top_productos(ctx):
    df = calcular_top_productos(ctx['dfs'])
    return crear_grafico(df, 'Top 10 Productos Más Vendidos', 'green',
                         'Total de Unidades Vendidas', 'Artículo',
                         'TopArticulosVendidos.png')


def op_top_beneficio(ctx):
    df = calcular_top_beneficio(ctx['dfs'])
    return crear_grafico(df, 'Top 10 Productos con Mayor Beneficio ($)',
                         'darkblue', 'Ganancia ($)', 'Artículo',
                         'TopGananciaArticulos.png')


def op_top_recaudado(ctx):
    df = calcular_top_recaudado(ctx['dfs'])
    return crear_grafico(df, 'Empleados Que Más Dinero Recaudaron', 'darkred',
                         'Recaudado ($)', 'Empleado', 'TopRecaudados.png')


# --- ANÁLISIS EXPLORATORIO -------------------------------------------------
def op_enriquecer(ctx):
    """Enriquecer OrderDetails con precio -> LineTotal (dispersión)."""
    od = ctx['od'].dropna(subset=['Quantity', 'Price', 'LineTotal'])

    fig, ax = plt.subplots(figsize=(10, 6))
    puntos = ax.scatter(od['Quantity'], od['Price'], c=od['LineTotal'],
                        cmap='plasma', s=50, alpha=0.85, edgecolors='none')
    cbar = fig.colorbar(puntos, ax=ax)
    cbar.set_label('LineTotal ($)')

    ax.set_title('OrderDetails Enriquecido: Quantity × Price = LineTotal',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Quantity (cantidad del pedido)')
    ax.set_ylabel('Price (precio unitario)')
    ax.grid(alpha=0.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))

    fig.savefig(os.path.join(GRAFICOS, 'EnriquecerOrderDetails.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_df_maestro(ctx):
    """Data frame maestro (df_full): Top 10 clientes por importe."""
    df_full = ctx['df_full']
    df = (df_full.groupby('CustomerName', as_index=False)['LineTotal'].sum()
          .nlargest(10, 'LineTotal')[['CustomerName', 'LineTotal']]
          .sort_values('LineTotal'))
    return crear_grafico(df, 'Data Frame Maestro: Top 10 Clientes por Importe',
                         'royalblue', 'Cliente', 'Importe ($)',
                         'DataFrameMaestro.png', vertical=True)


def op_histogramas(ctx):
    """Histogramas (2x2)."""
    df_full = ctx['df_full']
    rewards = ctx['dfs']['rewards']

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].hist(df_full['Quantity'].dropna(), bins=15,
                    edgecolor='black', color='steelblue')
    axes[0, 0].set_title('Cantidad por línea de pedido')
    axes[0, 0].set_xlabel('Quantity')
    axes[0, 0].set_ylabel('Frecuencia')

    axes[0, 1].hist(df_full['Price'].dropna(), bins=20,
                    edgecolor='black', color='seagreen')
    axes[0, 1].set_title('Precio unitario de productos')
    axes[0, 1].set_xlabel('Price')

    axes[1, 0].hist(df_full['LineTotal'].dropna(), bins=25,
                    edgecolor='black', color='darkorange')
    axes[1, 0].set_title('Importe por línea (Quantity × Price)')
    axes[1, 0].set_xlabel('LineTotal')

    axes[1, 1].hist(rewards['Reward'].dropna(), bins=15,
                    edgecolor='black', color='salmon')
    axes[1, 1].set_title('Recompensas por empleado')
    axes[1, 1].set_xlabel('Reward')

    fig.suptitle('Histogramas - Análisis Exploratorio', fontsize=15,
                 fontweight='bold')
    _hint(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(os.path.join(GRAFICOS, 'Histogramas.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_boxplots(ctx):
    """Box plots (3 en una ventana)."""
    df_full = ctx['df_full']
    rewards = ctx['dfs']['rewards'].merge(
        ctx['dfs']['employees'][['EmployeeID', 'Empleado']],
        on='EmployeeID', how='left')

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    # 1) LineTotal por categoría
    grupos = [(nombre, grupo['LineTotal'].dropna())
              for nombre, grupo in df_full.groupby('CategoryName')]
    axes[0].boxplot([g.values for _, g in grupos],
                    tick_labels=[n for n, _ in grupos])
    axes[0].set_title('LineTotal por Categoría')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].set_ylabel('LineTotal ($)')

    # 2) Quantity por transportista
    grupos = [(nombre, grupo['Quantity'].dropna())
              for nombre, grupo in df_full.groupby('ShipperName')]
    axes[1].boxplot([g.values for _, g in grupos],
                    tick_labels=[n for n, _ in grupos])
    axes[1].set_title('Cantidad por Transportista')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].set_ylabel('Quantity')

    # 3) Reward por empleado
    grupos = [(nombre, grupo['Reward'].dropna())
              for nombre, grupo in rewards.groupby('Empleado')]
    axes[2].boxplot([g.values for _, g in grupos],
                    tick_labels=[n for n, _ in grupos])
    axes[2].set_title('Recompensas por Empleado')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].set_ylabel('Reward ($)')

    fig.suptitle('Box Plots - Análisis Exploratorio', fontsize=15,
                 fontweight='bold')
    _hint(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(os.path.join(GRAFICOS, 'BoxPlots.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_matriz(ctx):
    """Matriz de correlación."""
    df_full = ctx['df_full']
    cols = ['Quantity', 'Price', 'CategoryID', 'SupplierID',
            'ShipperID', 'EmployeeID']
    corr = df_full[cols].corr(numeric_only=True)

    # Posiciones manuales para dejar espacio abajo del aviso ESC
    fig = plt.figure(figsize=(8.5, 7))
    ax = fig.add_axes([0.14, 0.26, 0.64, 0.60])
    im = ax.imshow(corr.values, cmap='coolwarm', vmin=-1, vmax=1)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Correlación')

    ax.set_xticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(corr.columns)))
    ax.set_yticklabels(corr.columns)

    for i in range(len(corr)):
        for j in range(len(corr)):
            val = corr.values[i, j]
            color = 'white' if abs(val) > 0.5 else 'black'
            ax.text(j, i, f"{val:.2f}", ha='center', va='center',
                    color=color, fontsize=9)

    ax.set_title('Matriz de Correlación (df_full)', fontsize=14,
                 fontweight='bold')
    _hint(fig)
    fig.savefig(os.path.join(GRAFICOS, 'MatrizCorrelacion.png'), dpi=150,
                bbox_inches='tight')
    return fig


# --- GRÁFICAS TEMPORALES Y CATEGÓRICAS ------------------------------------
def op_ventas_mes(ctx):
    """Ventas por mes."""
    df_full = ctx['df_full']
    serie = (df_full.dropna(subset=['OrderDate'])
             .set_index('OrderDate').sort_index()['LineTotal']
             .resample('ME').sum())

    fig, ax = plt.subplots(figsize=(11, 4.5))
    serie.plot(ax=ax, marker='o', color='teal', linewidth=2)
    ax.set_title('Importe Total por Mes', fontsize=14, fontweight='bold')
    ax.set_ylabel('LineTotal ($)')
    ax.set_xlabel('Mes')
    ax.grid(alpha=.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(GRAFICOS, 'VentasPorMes.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_top_importe(ctx):
    """Top 10 productos por importe (barras verticales)."""
    df_full = ctx['df_full']
    df = (df_full.groupby('ProductName', as_index=False)['LineTotal'].sum()
          .nlargest(10, 'LineTotal')[['ProductName', 'LineTotal']]
          .sort_values('LineTotal'))
    return crear_grafico(df, 'Top 10 Productos por Importe', 'teal',
                         'Producto', 'Importe ($)', 'TopImporteProductos.png',
                         vertical=True)


def op_importe_categoria(ctx):
    """Importe por categoría (barras verticales)."""
    df_full = ctx['df_full']
    df = (df_full.groupby('CategoryName', as_index=False)['LineTotal'].sum()
          .sort_values('LineTotal'))
    return crear_grafico(df, 'Importe por Categoría', 'coral',
                         'Categoría', 'Importe ($)', 'ImportePorCategoria.png',
                         vertical=True)


def op_top_paises(ctx):
    """Top 10 países: dispersión pedidos vs importe recaudado."""
    df_full = ctx['df_full']
    pedidos = df_full.groupby('Country')['OrderID'].nunique().nlargest(10)
    importes = df_full.groupby('Country')['LineTotal'].sum()
    df = pd.DataFrame({'Pedidos': pedidos,
                       'Importe': importes.loc[pedidos.index]})

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['Pedidos'], df['Importe'], s=140, color='slateblue',
               alpha=0.85, edgecolors='white', linewidths=1.5, zorder=3)
    for pais, fila in df.iterrows():
        ax.annotate(pais, (fila['Pedidos'], fila['Importe']),
                    textcoords='offset points', xytext=(0, 10),
                    ha='center', fontsize=9)

    ax.set_title('Top 10 Países: Pedidos vs Importe Recaudado',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Número de pedidos')
    ax.set_ylabel('Importe recaudado ($)')
    ax.set_ylim(0, df['Importe'].max() * 1.18)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: f'{v:,.0f}'))
    ax.grid(alpha=0.3, zorder=0)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))

    fig.savefig(os.path.join(GRAFICOS, 'TopPaisesPedidos.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_importe_empleado(ctx):
    """Importe total por empleado."""
    df_full = ctx['df_full']
    df = (df_full.groupby('EmployeeName', as_index=False)['LineTotal'].sum()
          .sort_values('LineTotal'))
    return crear_grafico(df, 'Importe Total por Empleado', 'goldenrod',
                         'Importe ($)', 'Empleado', 'ImportePorEmpleado.png')


# --- GRÁFICAS ADICIONALES --------------------------------------------------
def op_precio_unidades(ctx):
    """Precio vs unidades vendidas (dispersión con tendencia)."""
    dfs = ctx['dfs']
    prod = (dfs['order_details']
            .merge(dfs['products'][['ProductID', 'ProductName', 'Price']],
                   on='ProductID')
            .groupby(['ProductID', 'ProductName'], as_index=False)
            .agg(Unidades=('Quantity', 'sum'), Precio=('Price', 'first')))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(prod['Precio'], prod['Unidades'], color='darkorange',
               s=60, alpha=0.85, edgecolors='white', label='Productos')

    # Línea de tendencia (regresión lineal)
    z = np.polyfit(prod['Precio'], prod['Unidades'], 1)
    x_linea = np.linspace(prod['Precio'].min(), prod['Precio'].max(), 50)
    ax.plot(x_linea, np.polyval(z, x_linea), color='navy', linewidth=2,
            label='Línea de tendencia')

    # Anotar los productos extremos
    for _, fila in prod.nlargest(1, 'Unidades').iterrows():
        ax.annotate(fila['ProductName'], (fila['Precio'], fila['Unidades']),
                    textcoords='offset points', xytext=(0, 10),
                    ha='center', fontsize=9)
    for _, fila in prod.nlargest(1, 'Precio').iterrows():
        ax.annotate(fila['ProductName'], (fila['Precio'], fila['Unidades']),
                    textcoords='offset points', xytext=(0, 10),
                    ha='center', fontsize=9)

    ax.set_title('Precio vs Unidades Vendidas por Producto',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Precio unitario ($)')
    ax.set_ylabel('Unidades vendidas')
    ax.legend()
    ax.grid(alpha=0.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))

    fig.savefig(os.path.join(GRAFICOS, 'PrecioVsUnidades.png'), dpi=150,
                bbox_inches='tight')
    return fig


def op_dias_semana(ctx):
    """Pedidos por día de la semana (barras verticales)."""
    df_full = ctx['df_full'].dropna(subset=['OrderDate'])
    nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes',
               'Sábado', 'Domingo']
    serie = (df_full.groupby(df_full['OrderDate'].dt.weekday)['OrderID']
             .nunique().reindex(range(7), fill_value=0))
    df = pd.DataFrame({'Día': nombres, 'Pedidos': serie.values})
    return crear_grafico(df, 'Pedidos por Día de la Semana', 'mediumseagreen',
                         'Día', 'Pedidos', 'PedidosPorDia.png', vertical=True)


def op_unidades_categoria(ctx):
    """Unidades vendidas por categoría (barras verticales)."""
    df_full = ctx['df_full']
    df = (df_full.groupby('CategoryName', as_index=False)['Quantity'].sum()
          .sort_values('Quantity'))
    df.columns = ['Categoría', 'Unidades']
    return crear_grafico(df, 'Unidades Vendidas por Categoría',
                         'mediumpurple', 'Categoría', 'Unidades vendidas',
                         'UnidadesPorCategoria.png', vertical=True)


# ---------------------------------------------------------------------------
# 7. MOSTRAR GRÁFICO (ESC vuelve al menú)
# ---------------------------------------------------------------------------
def mostrar_grafico(fig):
    def al_presionar_tecla(event):
        if event.key == 'escape':
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', al_presionar_tecla)
    try:
        fig.canvas.manager.set_window_title(
            'Northwind - Presiona ESC para volver')
    except Exception:
        pass

    plt.show()          # Se bloquea aquí hasta que se cierre la ventana
    plt.close('all')


# ---------------------------------------------------------------------------
# 8. MENÚ PRINCIPAL
# ---------------------------------------------------------------------------
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def imprimir_menu(secciones):
    limpiar_pantalla()
    ancho = 78
    print('=' * ancho)
    print('HOLA, BIENVENIDO AL VISUALIZADOR DE GRÁFICOS NORTHWIND'.center(ancho))
    print('=' * ancho)
    for nombre, items in secciones:
        print(f'  {nombre}')
        print('-' * ancho)
        # Dos columnas: 1 a la izquierda, 2 a su derecha, 3 debajo, etc.
        for i in range(0, len(items), 2):
            izq = items[i]
            der = items[i + 1] if i + 1 < len(items) else None
            linea = f'  {izq[0]:>2}. {izq[1][:33]:<33}'
            if der:
                linea += f'  {der[0]:>2}. {der[1][:33]}'
            print(linea)
        print('-' * ancho)
    print('    0. Salir')
    print('=' * ancho)


def construir_menu():
    secciones = [
        ('TOP 4 - LO MÁS IMPORTANTE', [
            ('Top empleados con más órdenes', op_top_ordenes),
            ('Top 10 productos más vendidos', op_top_productos),
            ('Top 10 productos con beneficio', op_top_beneficio),
            ('Top empleados que más recaudaron', op_top_recaudado),
        ]),
        ('ANÁLISIS EXPLORATORIO DE DATOS', [
            ('Enriquecer OrderDetails', op_enriquecer),
            ('Top 10 clientes por importe', op_df_maestro),
            ('Histogramas', op_histogramas),
            ('Box plots', op_boxplots),
            ('Matriz de correlación', op_matriz),
        ]),
        ('GRÁFICAS TEMPORALES Y CATEGÓRICAS', [
            ('Ventas por mes', op_ventas_mes),
            ('Top 10 productos por importe', op_top_importe),
            ('Importe por categoría', op_importe_categoria),
            ('Top 10 países: pedidos vs importe', op_top_paises),
            ('Importe total por empleado', op_importe_empleado),
        ]),
        ('GRÁFICAS ADICIONALES', [
            ('Precio vs unidades vendidas', op_precio_unidades),
            ('Pedidos por día de la semana', op_dias_semana),
            ('Unidades vendidas por categoría', op_unidades_categoria),
        ]),
    ]

    # Numeración automática: 1, 2, 3, ... en todo el menú
    numerado = []
    numero = 1
    for nombre, items in secciones:
        nuevos = []
        for titulo, funcion in items:
            nuevos.append((str(numero), titulo, funcion))
            numero += 1
        numerado.append((nombre, nuevos))
    return numerado


def main():
    print('Cargando datos de Northwind...')
    dfs = cargar_datos()
    od = enriquecer_order_details(dfs)
    df_full = construir_df_full(dfs, od)
    ctx = {'dfs': dfs, 'od': od, 'df_full': df_full}

    secciones = construir_menu()
    opciones = {clave: (titulo, funcion)
                for _, items in secciones
                for clave, titulo, funcion in items}

    while True:
        imprimir_menu(secciones)
        opcion = input('  Elige una opción: ').strip()

        if opcion == '0':
            print('\n  ¡Hasta luego! Gracias por usar el visor Northwind.\n')
            break

        if opcion not in opciones:
            input('  ⚠ Opción no válida. Presiona ENTER para intentar '
                  'de nuevo...')
            continue

        titulo, funcion = opciones[opcion]
        fig = funcion(ctx)

        print(f'\n  Abriendo "{titulo}"... '
              '(Presiona ESC en la ventana para volver al menú)')
        mostrar_grafico(fig)


if __name__ == '__main__':
    main()
