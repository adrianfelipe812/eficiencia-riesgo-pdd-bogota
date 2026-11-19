"""Reconstruye tablero/plantilla_foco.html a partir del diseño original y de los ajustes del equipo.

Uso, desde la raíz del repositorio:
    python scripts/construir_plantilla.py
    python scripts/generar_tablero.py

tablero/plantilla_foco_base.html es el diseño original del tablero (aplicación ya compilada, sin
datos). Cada script scripts/ajustar_*.py le aplica un ajuste reemplazando fragmentos exactos; el orden
importa porque algunos ajustes parten de lo que dejó el anterior. El resultado es
tablero/plantilla_foco.html, que generar_tablero.py llena con los datos Gold.

Para cambiar el diseño: edite (o agregue) un script de ajuste, súmelo a AJUSTES y vuelva a ejecutar.
"""
import importlib.util
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "tablero" / "plantilla_foco_base.html"
PLANTILLA = RAIZ / "tablero" / "plantilla_foco.html"
AJUSTES = [
    "ajustar_encabezado",    # título y filtros en un recuadro fijo; fecha de corte junto a «Filtros»
    "ajustar_tarjetas",      # tarjetas del Panorama: programado, girado, comprometido, rezagadas, alerta
    "ajustar_graficas",      # leyendas abajo, gráficas que llenan su celda, franja del año del corte
    "ajustar_bandeja",       # tabla de metas: títulos completos y fijos, columna «Girado»
    "ajustar_detalle",       # detalle de la meta: tarjetas con semáforo, relatos antes que gráficas
    "ajustar_actividades",   # gráfica de avance por año al pasar el cursor; encabezado fijo
    "ajustar_descargas",     # descarga de archivos fuente por corte en la barra lateral
    "ajustar_tema",          # modo oscuro activable
    "ajustar_movil",         # uso cómodo en celular (Android e iOS)
]


def aplicar(nombre: str) -> None:
    especificacion = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    modulo.main()


if __name__ == "__main__":
    shutil.copyfile(BASE, PLANTILLA)
    for nombre in AJUSTES:
        aplicar(nombre)
    print(f"Plantilla lista: {PLANTILLA.relative_to(RAIZ)} ({len(AJUSTES)} ajustes sobre el diseño original)")
