import matplotlib
matplotlib.use('TkAgg')
import os
import sys
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(BASE, 'datos')
GRAFICOS = os.path.join(BASE, 'gráficos')

os.makedirs(GRAFICOS, exist_ok=True)

if os.name == 'nt':
    try:
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

plt.rcParams['text.parse_math'] = False