"""Construye la tabla Silver de entidades normalizadas.

Uso, desde la raíz del repositorio:
    python scripts/normalizar_entidades.py

Lee data/raw/Normalizacion_Entidades.xlsx y escribe data/silver/entidades/entidad.csv. Avisa si
alguna entidad de Gestión-Inversión o de los relatos no tiene nombre normalizado: en ese caso hay
que agregarla al Excel (con su código de Hacienda) y volver a ejecutar. Después: construir_gold.py
y generar_tablero.py.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from pdd.comun import cargar_config, leer_silver  # noqa: E402
from pdd.entidades import guardar_silver_entidades, nombres_normalizados  # noqa: E402

if __name__ == "__main__":
    config = cargar_config()
    destino = guardar_silver_entidades(config)
    nombres = nombres_normalizados(config)
    gi = leer_silver(config, "gestion_inversion/gestion_inversion.csv")
    usadas = gi.drop_duplicates("entidad_codigo").set_index("entidad_codigo")["entidad_nombre"]
    faltan = {c: n for c, n in usadas.items() if c not in nombres}
    print(f"Tabla de entidades: {destino.relative_to(RAIZ)} ({len(nombres)} con código de Hacienda)")
    print(f"Entidades de Gestión-Inversión con nombre normalizado: {len(usadas) - len(faltan)} de {len(usadas)}")
    for codigo, nombre in faltan.items():
        print(f"   FALTA {codigo}  {nombre}")
    sys.exit(1 if faltan else 0)
