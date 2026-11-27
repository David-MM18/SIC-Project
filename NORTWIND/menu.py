import os
from utils import mostrar_grafico
from subprocess import run

# 1. Importamos tus indicadores económicos
from indicadores import (
    obtener_historico_dolar, obtener_inflacion,
    obtener_formacion_fija_capital_fijo, obtener_consumo_familiar, 
    obtener_consumo_hogares, obtener_consumo_gobierno, 
    obtener_pib_real, obtener_importaciones, importaciones_pbi
)

# 2. Importamos Northwind
from northwind import (
    cargar_datos, enriquecer_order_details, construir_df_full,
    op_top_ordenes, op_top_productos, op_top_beneficio, op_top_recaudado,
    op_enriquecer, op_df_maestro, op_histogramas, op_boxplots, op_matriz,
    op_ventas_mes, op_top_importe, op_importe_categoria, op_top_paises,
    op_importe_empleado, op_precio_unidades, op_dias_semana, op_unidades_categoria
)


def limpiar_pantalla():
    run(['cls' if os.name == 'nt' else 'clear'], shell=True)
    # os.system('cls' if os.name == 'nt' else 'clear')


def imprimir_menu(secciones):
    limpiar_pantalla()
    ancho = 78
    print('=' * ancho)
    print('SISTEMA DE VISUALIZACIÓN DE DATOS'.center(ancho))
    print('=' * ancho)
    for nombre, items in secciones:
        print(f'  {nombre}')
        print('-' * ancho)
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
        ('INDICADORES ECONÓMICOS (Venezuela)', [
            ('Histórico del dólar', obtener_historico_dolar),
            ('Inflación', obtener_inflacion),
            ('Formación bruta de capital', obtener_formacion_fija_capital_fijo),
            ('Consumo familiar', obtener_consumo_familiar),
            ('Consumo hogares (% PIB)', obtener_consumo_hogares),
            ('Consumo gubernamental', obtener_consumo_gobierno),
            ('PIB real per cápita', obtener_pib_real),
            ('Importaciones USD', obtener_importaciones),
            ('Importaciones (% PIB)', importaciones_pbi),
        ]),
        ('NORTHWIND - TOP 4 (Ventas)', [
            ('Top empleados con más órdenes', op_top_ordenes),
            ('Top 10 productos más vendidos', op_top_productos),
            ('Top 10 productos con beneficio', op_top_beneficio),
            ('Top empleados que más recaudaron', op_top_recaudado),
        ]),
        ('NORTHWIND - ANÁLISIS Y GRÁFICAS', [
            ('Enriquecer OrderDetails', op_enriquecer),
            ('Top 10 clientes por importe', op_df_maestro),
            ('Histogramas', op_histogramas),
            ('Box plots', op_boxplots),
            ('Matriz de correlación', op_matriz),
            ('Ventas por mes', op_ventas_mes),
            ('Top 10 productos por importe', op_top_importe),
            ('Importe por categoría', op_importe_categoria),
            ('Top 10 países: pedidos vs importe', op_top_paises),
            ('Importe total por empleado', op_importe_empleado),
            ('Precio vs unidades vendidas', op_precio_unidades),
            ('Pedidos por día de la semana', op_dias_semana),
            ('Unidades vendidas por categoría', op_unidades_categoria),
        ]),
    ]

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
    opciones = {clave: (titulo, funcion) for _, items in secciones for clave, titulo, funcion in items}

    while True:
        try:
            imprimir_menu(secciones)
            opcion = input('  Elige una opción: ').strip()

            if opcion == '0':
                print('\n  ¡Hasta luego!\n')
                break

            if opcion not in opciones:
                input('  ⚠ Opción no válida. Presiona ENTER para intentar de nuevo...')
                continue

            titulo, funcion = opciones[opcion]
            
            print(f'\n  Abriendo "{titulo}"... (Presiona ESC en la ventana para volver)')
            
            # Si la función empieza con "op_", es de Northwind y necesita el contexto (ctx)
            if funcion.__name__.startswith('op_'):
                fig = funcion(ctx)
                mostrar_grafico(fig, titulo=titulo)
            else:
                # Si es de economía, ella misma se encarga de mostrar su gráfico
                funcion()
        except Exception as e:
            print(f'\n  ⚠ Ocurrió un error: {e}')
            input('  Presiona ENTER para continuar...')
