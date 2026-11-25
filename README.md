# SIC-Project
# Proyecto-Sic - Fase 1: Prototipo de Analítica para SaaS de Medición de Puertas

Este repositorio contiene la **Fase 1** del proyecto **Proyecto-Sic**, un sistema SaaS (Software as a Service) diseñado para digitalizar el flujo de trabajo de una fábrica o distribuidora de puertas.

##  La Visión del Proyecto (Fase Final)
El objetivo del SaaS es doble:
1. **Ingreso de Medidas y Pedidos:** Permitir que un cliente (o un vendedor) ingrese las medidas exactas de una puerta (ancho, alto, espesor, tipo de material, sentido de apertura). Estos datos se enviarán a un sistema de órdenes que generará la orden de corte y producción exacta.
2. **Analítica y Business Intelligence (BI):** Un panel de control (dashboard) que analice la frecuencia de los pedidos. ¿Cuáles son las medidas más solicitadas? ¿Qué tipo de puerta se vende más por temporada? Esto ayuda a optimizar el inventario de materia prima y la logística de cortes.

##  ¿Qué es esta Fase 1? (El Prototipo)
Antes de construir la compleja base de datos de medidas y el sistema de cortes, esta Fase 1 se enfoca en **construir y validar la arquitectura modular** del software (lectura de datos, cálculo de KPIs y visualización). 

Para probar este motor sin afectar los datos reales de la fábrica, hemos utilizado dos "campos de pruebas":
*   **Módulo de Economía:** Prueba de consumo de APIs externas y manejo de series de tiempo.
*   **Módulo Northwind (Ventas):** Prueba de cruce de tablas relacionales (simulando clientes, productos y pedidos) para generar los análisis de frecuencia y top ventas que luego aplicaremos a las medidas de las puertas.

---

##  Estructura Modular (Preparada para escalar)

El sistema está diseñado para que, cuando pasemos a la Fase 2, solo tengamos que cambiar los datos de prueba por la base de datos real de las puertas. 

```text
NORTWIND/
│
├── main.py                  # Punto de entrada de la aplicación
├── config.py                # Configuración global (rutas, estilos)
├── utils.py                 # Utilidades (ventanas, conexiones)
├── menu.py                  # Interfaz de consola (en el futuro será una Web App)
│
├── datos/                   # Carpeta de datos
│   └── datos_economicos/    # (Fase 2: Aquí irán los JSON/CSVs de medidas)
│
├── indicadores/             # MÓDULO DE PRUEBA (Economía y Mercado)
│   ├── __init__.py          
│   ├── dolar.py             
│   ├── inflacion.py         
│   └── ... (otros indicadores)
│
└── northwind/               # MÓDULO DE PRUEBA (Simulación del Core del SaaS)
    ├── __init__.py          
    ├── datos.py             # (Fase 2: Conectará a la BD de órdenes de puertas)
    ├── calculos.py          # (Fase 2: Calculará frecuencia de medidas de puertas)
    └── graficos.py          # (Fase 2: Dashboards de producción y cortes)
