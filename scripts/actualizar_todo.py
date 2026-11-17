"""Actualiza todo el proyecto cuando la SDP publica un corte nuevo.

Uso, desde la raíz del repositorio:
    python scripts/actualizar_todo.py "C:/ruta/a/SDP_BCS_Pipeline_Optimizado/data"

La ruta es la carpeta "data" del scraper, después de haber descargado y consolidado el
corte nuevo. Sin ruta, solo vuelve a generar las tablas y el tablero con los datos que ya
están en el repositorio.

Pasos:
  1. Trae los datos nuevos y actualiza data/FUENTES.csv   (actualizar_insumos.py)
  2. Reconstruye las tablas de data/gold/                 (construir_gold.py)
  3. Regenera el tablero tablero/index.html               (generar_tablero.py)
  4. Audita las tablas contra los archivos originales     (auditar_gold.py)

Al terminar, revise docs/RESULTADOS.md: sus cifras se escriben a mano y hay que
actualizarlas con las de las tablas nuevas.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    pasos = [["scripts/construir_gold.py"], ["scripts/generar_tablero.py"], ["scripts/auditar_gold.py"]]
    if len(sys.argv) > 1:
        pasos.insert(0, ["scripts/actualizar_insumos.py", sys.argv[1]])
    for paso in pasos:
        print(f"\n=== {paso[0]} ===", flush=True)
        if subprocess.run([sys.executable, *paso], cwd=RAIZ).returncode != 0:
            sys.exit(f"Se detuvo en {paso[0]}. Corrija el problema y vuelva a ejecutar.")
    print("\nActualizado. Abra tablero/index.html para ver el resultado.")
