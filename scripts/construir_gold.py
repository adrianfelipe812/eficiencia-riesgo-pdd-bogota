"""Genera las tablas Gold del PDD (incluye la lectura y clasificación de la narrativa).

Uso, desde la raíz del repositorio:
    python scripts/construir_gold.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pdd.comun import cargar_config
from pdd.gold import construir_gold

if __name__ == "__main__":
    tablas = construir_gold(cargar_config())
    print()
    for nombre, tabla in tablas.items():
        print(f"  {nombre:<28} {len(tabla):>6} filas x {tabla.shape[1]:>2} columnas")
    control = tablas["gold_control_calidad"]
    print(f"\nControles de calidad cumplidos: {(control['cumple'] == 'Sí').sum()} de {len(control)}")
    if (control["cumple"] != "Sí").any():
        print(control[control["cumple"] != "Sí"].to_string(index=False))
