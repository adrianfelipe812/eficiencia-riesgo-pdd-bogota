"""Trae al repositorio una descarga nueva del scraper y actualiza data/FUENTES.csv.

Uso, desde la raíz del repositorio:
    python scripts/actualizar_insumos.py "C:/ruta/a/SDP_BCS_Pipeline_Optimizado/data"

Copia los tres consolidados (Silver), los Excel originales del corte más reciente y los
PDF "por entidad" que falten. Después hay que ejecutar construir_gold.py y generar_tablero.py.
"""
import csv
import hashlib
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from pdd.narrativas import es_reporte_por_entidad  # noqa: E402

SILVER = ["avance_plan/meta_producto.csv", "avance_plan/indicador.csv", "gestion_inversion/gestion_inversion.csv"]


def huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


if __name__ == "__main__":
    origen = Path(sys.argv[1])
    inventario = {r["archivo_local"]: r for r in csv.DictReader(
        open(origen / "metadata" / "inventario.csv", encoding="utf-8-sig"), delimiter="|")}
    registro = RAIZ / "data" / "FUENTES.csv"
    previas = {r["archivo"]: r for r in csv.DictReader(open(registro, encoding="utf-8-sig"), delimiter=";")}

    copias = [(origen / "processed" / f, f"data/silver/{f}") for f in SILVER]
    for fuente in ["avance_plan", "gestion_inversion"]:          # Excel originales del último corte
        ultimo = sorted(p for p in (origen / "raw" / fuente).glob("*/*") if p.is_dir())[-1]
        copias += [(x, f"data/raw/{fuente}/{ultimo.parent.name}/{ultimo.name}/{x.name}") for x in ultimo.glob("*.xlsx")]
    for pdf in (origen / "raw" / "gestion_inversion").rglob("*.pdf"):   # relatos: solo el reporte por entidad
        if es_reporte_por_entidad(pdf, "17"):
            copias.append((pdf, "data/" + pdf.relative_to(origen).as_posix()))

    for desde, destino in copias:
        hasta = RAIZ / destino
        if hasta.exists() and huella(hasta) == huella(desde):
            continue
        hasta.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(desde, hasta)
        inv = inventario.get(destino, {})
        previas[destino] = {
            "archivo": destino, "bytes": hasta.stat().st_size, "sha256": huella(hasta),
            "descripcion": previas.get(destino, {}).get("descripcion") or "Archivo original de la SDP",
            "url_origen": inv.get("download_url", ""), "fecha_publicacion": inv.get("fecha_publicacion", ""),
            "fecha_descarga": inv.get("fecha_descarga", "")}
        print("actualizado:", destino)

    campos = ["archivo", "descripcion", "bytes", "sha256", "url_origen", "fecha_publicacion", "fecha_descarga"]
    with open(registro, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(previas[k] for k in sorted(previas))
    print(f"{len(previas)} archivos registrados en data/FUENTES.csv")
