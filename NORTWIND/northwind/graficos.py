import matplotlib
matplotlib.use('TkAgg') #soporte para mostrar gráficos en ventanas separadas en linux
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import GRAFICOS
from northwind.calculos import calcular_top_ordenes, calcular_top_productos, calcular_top_beneficio, calcular_top_recaudado


def _hint(fig):
    fig.text(0.5, 0.01, '>> Presiona ESC para volver al menú <<', ha='center', fontsize=10, style='italic', color='gray')


def crear_grafico(df, titulo, tono, xlabel, ylabel, filename=None, vertical=False):
    col0, col1 = df.columns
    fig, ax = plt.subplots(figsize=(10, 5.5))

    if vertical:
        df.plot(x=col0, y=col1, kind='bar', ax=ax, legend=False, color=tono)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, df[col1].max() * 1.18)
        for cont in ax.containers:
            ax.bar_label(cont, fmt='{:,.0f}', rotation=90, padding=3, fontsize=8) # type: ignore
    else:
        df.plot(x=col0, y=col1, kind='barh', ax=ax, legend=False, color=tono)
        ax.grid(axis='x', alpha=0.3)
        for cont in ax.containers:
            ax.bar_label(cont, fmt='{:,.0f}', padding=3, fontsize=9) # type: ignore

    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    if filename:
        fig.savefig(os.path.join(GRAFICOS, filename), dpi=150, bbox_inches='tight')
    return fig

def op_top_ordenes(ctx):
    df = calcular_top_ordenes(ctx['dfs'])
    return crear_grafico(df, 'Empleados Que Más Órdenes Cerraron', 'orange', 'Órdenes Cerradas', 'Empleado', 'TopVendedores.png')

def op_top_productos(ctx):
    df = calcular_top_productos(ctx['dfs'])
    return crear_grafico(df, 'Top 10 Productos Más Vendidos', 'green', 'Total de Unidades Vendidas', 'Artículo', 'TopArticulosVendidos.png')

def op_top_beneficio(ctx):
    df = calcular_top_beneficio(ctx['dfs'])
    return crear_grafico(df, 'Top 10 Productos con Mayor Beneficio ($)', 'darkblue', 'Ganancia ($)', 'Artículo', 'TopGananciaArticulos.png')

def op_top_recaudado(ctx):
    df = calcular_top_recaudado(ctx['dfs'])
    return crear_grafico(df, 'Empleados Que Más Dinero Recaudaron', 'darkred', 'Recaudado ($)', 'Empleado', 'TopRecaudados.png')

def op_enriquecer(ctx):
    od = ctx['od'].dropna(subset=['Quantity', 'Price', 'LineTotal'])
    fig, ax = plt.subplots(figsize=(10, 6))
    puntos = ax.scatter(od['Quantity'], od['Price'], c=od['LineTotal'], cmap='plasma', s=50, alpha=0.85, edgecolors='none')
    cbar = fig.colorbar(puntos, ax=ax)
    cbar.set_label('LineTotal ($)')
    ax.set_title('OrderDetails Enriquecido: Quantity × Price = LineTotal', fontsize=14, fontweight='bold')
    ax.set_xlabel('Quantity (cantidad del pedido)')
    ax.set_ylabel('Price (precio unitario)')
    ax.grid(alpha=0.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(GRAFICOS, 'EnriquecerOrderDetails.png'), dpi=150, bbox_inches='tight')
    return fig

def op_df_maestro(ctx):
    df_full = ctx['df_full']
    df = (df_full.groupby('CustomerName', as_index=False)['LineTotal'].sum().nlargest(10, 'LineTotal')[['CustomerName', 'LineTotal']].sort_values('LineTotal'))
    return crear_grafico(df, 'Data Frame Maestro: Top 10 Clientes por Importe', 'royalblue', 'Cliente', 'Importe ($)', 'DataFrameMaestro.png', vertical=True)

def op_histogramas(ctx):
    df_full = ctx['df_full']
    rewards = ctx['dfs']['rewards']
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes[0, 0].hist(df_full['Quantity'].dropna(), bins=15, edgecolor='black', color='steelblue')
    axes[0, 0].set_title('Cantidad por línea de pedido')
    axes[0, 0].set_xlabel('Quantity')
    axes[0, 0].set_ylabel('Frecuencia')
    axes[0, 1].hist(df_full['Price'].dropna(), bins=20, edgecolor='black', color='seagreen')
    axes[0, 1].set_title('Precio unitario de productos')
    axes[0, 1].set_xlabel('Price')
    axes[1, 0].hist(df_full['LineTotal'].dropna(), bins=25, edgecolor='black', color='darkorange')
    axes[1, 0].set_title('Importe por línea (Quantity × Price)')
    axes[1, 0].set_xlabel('LineTotal')
    axes[1, 1].hist(rewards['Reward'].dropna(), bins=15, edgecolor='black', color='salmon')
    axes[1, 1].set_title('Recompensas por empleado')
    axes[1, 1].set_xlabel('Reward')
    fig.suptitle('Histogramas - Análisis Exploratorio', fontsize=15, fontweight='bold')
    _hint(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(os.path.join(GRAFICOS, 'Histogramas.png'), dpi=150, bbox_inches='tight')
    return fig

def op_boxplots(ctx):
    df_full = ctx['df_full']
    rewards = ctx['dfs']['rewards'].merge(ctx['dfs']['employees'][['EmployeeID', 'Empleado']], on='EmployeeID', how='left')
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
    grupos = [(nombre, grupo['LineTotal'].dropna()) for nombre, grupo in df_full.groupby('CategoryName')]
    axes[0].boxplot([g.values for _, g in grupos], tick_labels=[n for n, _ in grupos])
    axes[0].set_title('LineTotal por Categoría')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].set_ylabel('LineTotal ($)')
    grupos = [(nombre, grupo['Quantity'].dropna()) for nombre, grupo in df_full.groupby('ShipperName')]
    axes[1].boxplot([g.values for _, g in grupos], tick_labels=[n for n, _ in grupos])
    axes[1].set_title('Cantidad por Transportista')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].set_ylabel('Quantity')
    grupos = [(nombre, grupo['Reward'].dropna()) for nombre, grupo in rewards.groupby('Empleado')]
    axes[2].boxplot([g.values for _, g in grupos], tick_labels=[n for n, _ in grupos])
    axes[2].set_title('Recompensas por Empleado')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].set_ylabel('Reward ($)')
    fig.suptitle('Box Plots - Análisis Exploratorio', fontsize=15, fontweight='bold')
    _hint(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(os.path.join(GRAFICOS, 'BoxPlots.png'), dpi=150, bbox_inches='tight')
    return fig


def op_matriz(ctx):
    df_full = ctx['df_full']
    cols = ['Quantity', 'Price', 'CategoryID', 'SupplierID', 'ShipperID', 'EmployeeID']
    corr = df_full[cols].corr(numeric_only=True)
    fig = plt.figure(figsize=(8.5, 7))
    ax = fig.add_axes([0.14, 0.26, 0.64, 0.60]) # type: ignore
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
            ax.text(j, i, f"{val:.2f}", ha='center', va='center', color=color, fontsize=9)
    ax.set_title('Matriz de Correlación (df_full)', fontsize=14, fontweight='bold')
    _hint(fig)
    fig.savefig(os.path.join(GRAFICOS, 'MatrizCorrelacion.png'), dpi=150, bbox_inches='tight')
    return fig


def op_ventas_mes(ctx):
    df_full = ctx['df_full']
    serie = (df_full.dropna(subset=['OrderDate']).set_index('OrderDate').sort_index()['LineTotal'].resample('ME').sum())
    fig, ax = plt.subplots(figsize=(11, 4.5))
    serie.plot(ax=ax, marker='o', color='teal', linewidth=2)
    ax.set_title('Importe Total por Mes', fontsize=14, fontweight='bold')
    ax.set_ylabel('LineTotal ($)')
    ax.set_xlabel('Mes')
    ax.grid(alpha=.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(GRAFICOS, 'VentasPorMes.png'), dpi=150, bbox_inches='tight')
    return fig


def op_top_importe(ctx):
    df_full = ctx['df_full']
    df = (df_full.groupby('ProductName', as_index=False)['LineTotal'].sum().nlargest(10, 'LineTotal')[['ProductName', 'LineTotal']].sort_values('LineTotal'))
    return crear_grafico(df, 'Top 10 Productos por Importe', 'teal', 'Producto', 'Importe ($)', 'TopImporteProductos.png', vertical=True)


def op_importe_categoria(ctx):
    df_full = ctx['df_full']
    df = (df_full.groupby('CategoryName', as_index=False)['LineTotal'].sum().sort_values('LineTotal'))
    return crear_grafico(df, 'Importe por Categoría', 'coral', 'Categoría', 'Importe ($)', 'ImportePorCategoria.png', vertical=True)


def op_top_paises(ctx):
    df_full = ctx['df_full']
    pedidos = df_full.groupby('Country')['OrderID'].nunique().nlargest(10)
    importes = df_full.groupby('Country')['LineTotal'].sum()
    df = pd.DataFrame({'Pedidos': pedidos, 'Importe': importes.loc[pedidos.index]})
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['Pedidos'], df['Importe'], s=140, color='slateblue', alpha=0.85, edgecolors='white', linewidths=1.5, zorder=3)
    for pais, fila in df.iterrows():
        ax.annotate(pais, (fila['Pedidos'], fila['Importe']), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9) # type: ignore
    ax.set_title('Top 10 Países: Pedidos vs Importe Recaudado', fontsize=14, fontweight='bold')
    ax.set_xlabel('Número de pedidos')
    ax.set_ylabel('Importe recaudado ($)')
    ax.set_ylim(0, df['Importe'].max() * 1.18)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f}')) # type: ignore
    ax.grid(alpha=0.3, zorder=0)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(GRAFICOS, 'TopPaisesPedidos.png'), dpi=150, bbox_inches='tight')
    return fig

def op_importe_empleado(ctx):
    df_full = ctx['df_full']
    df = (df_full.groupby('EmployeeName', as_index=False)['LineTotal'].sum().sort_values('LineTotal'))
    return crear_grafico(df, 'Importe Total por Empleado', 'goldenrod', 'Importe ($)', 'Empleado', 'ImportePorEmpleado.png')

def op_precio_unidades(ctx):
    dfs = ctx['dfs']
    prod = (dfs['order_details'].merge(dfs['products'][['ProductID', 'ProductName', 'Price']], on='ProductID').groupby(['ProductID', 'ProductName'], as_index=False).agg(Unidades=('Quantity', 'sum'), Precio=('Price', 'first')))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(prod['Precio'], prod['Unidades'], color='darkorange', s=60, alpha=0.85, edgecolors='white', label='Productos')
    z = np.polyfit(prod['Precio'], prod['Unidades'], 1)
    x_linea = np.linspace(prod['Precio'].min(), prod['Precio'].max(), 50)
    ax.plot(x_linea, np.polyval(z, x_linea), color='navy', linewidth=2, label='Línea de tendencia')
    for _, fila in prod.nlargest(1, 'Unidades').iterrows():
        ax.annotate(fila['ProductName'], (fila['Precio'], fila['Unidades']), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9)
    for _, fila in prod.nlargest(1, 'Precio').iterrows():
        ax.annotate(fila['ProductName'], (fila['Precio'], fila['Unidades']), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9)
    ax.set_title('Precio vs Unidades Vendidas por Producto', fontsize=14, fontweight='bold')
    ax.set_xlabel('Precio unitario ($)')
    ax.set_ylabel('Unidades vendidas')
    ax.legend()
    ax.grid(alpha=0.3)
    _hint(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(GRAFICOS, 'PrecioVsUnidades.png'), dpi=150, bbox_inches='tight')
    return fig

def op_dias_semana(ctx):
    df_full = ctx['df_full'].dropna(subset=['OrderDate'])
    nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    serie = (df_full.groupby(df_full['OrderDate'].dt.weekday)['OrderID'].nunique().reindex(range(7), fill_value=0))
    df = pd.DataFrame({'Día': nombres, 'Pedidos': serie.values})
    return crear_grafico(df, 'Pedidos por Día de la Semana', 'mediumseagreen', 'Día', 'Pedidos', 'PedidosPorDia.png', vertical=True)

def op_unidades_categoria(ctx):
    df_full = ctx['df_full']
    df = (df_full.groupby('CategoryName', as_index=False)['Quantity'].sum().sort_values('Quantity'))
    df.columns = ['Categoría', 'Unidades']
    return crear_grafico(df, 'Unidades Vendidas por Categoría', 'mediumpurple', 'Categoría', 'Unidades vendidas', 'UnidadesPorCategoria.png', vertical=True)
