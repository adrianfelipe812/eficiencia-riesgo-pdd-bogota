"""Ubicación de la carpeta del proyecto, aunque cambie de nombre o equipo."""
from pathlib import Path


def raiz_proyecto() -> Path:
    """Devuelve la carpeta donde se encuentra este archivo."""
    return Path(__file__).resolve().parent


def corte_local_comun(raiz: Path, fuentes=("avance_plan", "gestion_inversion")) -> str:
    """Selecciona la fecha más reciente con Excel en todas las fuentes indicadas."""
    from datetime import date
    base = Path(raiz) / "Capa Bronce"
    disponibles = []
    for carpeta in base.iterdir():
        if not carpeta.is_dir():
            continue
        try:
            fecha = date.fromisoformat(carpeta.name)
        except ValueError:
            continue
        if all(any(p.is_file() and not p.name.startswith("~$")
                   for p in (carpeta / fuente).glob("*.xlsx")) for fuente in fuentes):
            disponibles.append(fecha)
    if not disponibles:
        raise FileNotFoundError("No hay un corte local con Excel para las fuentes requeridas.")
    return max(disponibles).isoformat()
