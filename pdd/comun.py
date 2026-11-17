"""Utilidades compartidas: configuración, lectura de Silver y escritura de Gold."""
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def _ruta(texto: str) -> Path:
    """Una ruta relativa se entiende desde la raíz del repositorio."""
    ruta = Path(texto)
    return ruta if ruta.is_absolute() else RAIZ / ruta


def cargar_config() -> dict:
    """Lee configs/pdd.yaml. Si existe configs/pdd.local.yaml (propio de cada integrante y
    fuera del control de versiones), sus rutas reemplazan a las del archivo general."""
    with open(RAIZ / "configs" / "pdd.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    local = RAIZ / "configs" / "pdd.local.yaml"
    if local.exists():
        with open(local, encoding="utf-8") as f:
            config["rutas"].update((yaml.safe_load(f) or {}).get("rutas", {}))
    config["rutas"]["silver"] = str(_ruta(config["rutas"]["silver"]))
    config["rutas"]["pdf_narrativas"] = [str(_ruta(r)) for r in config["rutas"]["pdf_narrativas"]]
    if not Path(config["rutas"]["silver"]).exists():
        raise FileNotFoundError(
            f"No existe la carpeta de Silver: {config['rutas']['silver']}. Copie configs/pdd.local.ejemplo.yaml "
            "como configs/pdd.local.yaml y escriba ahí las rutas de su equipo.")
    return config


def ruta_gold(config: dict) -> Path:
    ruta = _ruta(config["rutas"]["gold"])
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def leer_silver(config: dict, relativa: str) -> pd.DataFrame:
    """Lee un consolidado Silver. Todo entra como texto: los códigos conservan sus
    ceros y ningún vacío se convierte en cero por accidente."""
    ruta = Path(config["rutas"]["silver"]) / relativa
    return pd.read_csv(ruta, sep="|", encoding="utf-8-sig", dtype="string", keep_default_na=False)


def a_numero(serie: pd.Series) -> pd.Series:
    """Convierte texto con coma decimal a número; un vacío queda como vacío (no cero)."""
    return pd.to_numeric(serie.str.replace(",", ".", regex=False).replace("", pd.NA), errors="coerce")


def a_fecha(serie: pd.Series) -> pd.Series:
    return pd.to_datetime(serie, format="%d/%m/%Y")


def razon(numerador: pd.Series, denominador: pd.Series) -> pd.Series:
    """Porcentaje numerador/denominador; vacío cuando no hay denominador positivo."""
    return (100 * numerador / denominador.where(denominador > 0)).round(2)


def guardar_csv(tabla: pd.DataFrame, carpeta: Path, nombre: str) -> None:
    """Misma convención que Silver: separador |, coma decimal, fechas DD/MM/AAAA."""
    tabla.to_csv(carpeta / f"{nombre}.csv", sep="|", decimal=",", index=False,
                 encoding="utf-8-sig", date_format="%d/%m/%Y")
