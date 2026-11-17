"""Muestra la comparación de variantes del "rezago relativo" (objetivo del modelo).

Uso, desde la raíz del repositorio (después de construir_gold.py):
    python scripts/comparar_definiciones_riesgo.py

La comparación se calcula dentro de construir_gold.py y queda en
data/gold/gold_comparacion_riesgo.csv; este script solo la muestra. La explicación de
cada columna está en pdd/modelo.py (comparar_definiciones_riesgo) y en docs/RESULTADOS.md.
"""
from pathlib import Path

import pandas as pd

if __name__ == "__main__":
    ruta = Path(__file__).resolve().parents[1] / "data" / "gold" / "gold_comparacion_riesgo.csv"
    pd.set_option("display.width", 250)
    print(pd.read_csv(ruta, sep="|", decimal=",", encoding="utf-8-sig").to_string(index=False))