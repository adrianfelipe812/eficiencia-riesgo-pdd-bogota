"""Normalización de entidades (capa Silver).

La fuente es data/raw/Normalizacion_Entidades.xlsx (hoja «Entidades»): nombre oficial con sigla
(Nombre_entidad_sigla), nombre, sigla, códigos SIGEP y de Hacienda, NIT y sector. El código de
Hacienda es el mismo «entidad_codigo» de Gestión-Inversión y de los relatos, pero sin los ceros a la
izquierda (102 ↔ 0102), así que se rellena a cuatro dígitos para cruzarlos.

Resultado: data/silver/entidades/entidad.csv, una fila por entidad. Gold toma de ahí
entidad_nombre_sigla, que es el nombre que muestra el tablero.
"""
from pathlib import Path

import pandas as pd

from pdd.comun import RAIZ

RELATIVA = "entidades/entidad.csv"
COLUMNAS = {
    "Nombre_entidad_sigla": "entidad_nombre_sigla", "Nombre_entidad": "entidad_nombre_oficial",
    "Sigla": "entidad_sigla_oficial", "Codigo_SIGEP": "codigo_sigep", "Codigo_Hacienda": "codigo_hacienda",
    "NIT": "nit", "Digito_verificacion": "digito_verificacion", "Sector": "sector_oficial",
}


def _texto_entero(serie: pd.Series) -> pd.Series:
    """Códigos numéricos como texto sin decimales (el Excel los trae como 230.0); vacío se queda vacío."""
    return pd.to_numeric(serie, errors="coerce").astype("Int64").astype("string").fillna("")


def tabla_entidades(config: dict) -> pd.DataFrame:
    origen = Path(config["rutas"].get("normalizacion_entidades", "data/raw/Normalizacion_Entidades.xlsx"))
    origen = origen if origen.is_absolute() else RAIZ / origen
    crudo = pd.read_excel(origen, sheet_name="Entidades", dtype=str)
    faltan = set(COLUMNAS) - set(crudo.columns)
    if faltan:
        raise ValueError(f"A {origen.name} le faltan columnas: {sorted(faltan)}")
    t = crudo[list(COLUMNAS)].rename(columns=COLUMNAS)
    for columna in ["codigo_sigep", "codigo_hacienda", "nit", "digito_verificacion"]:
        t[columna] = _texto_entero(t[columna])
    for columna in ["entidad_nombre_sigla", "entidad_nombre_oficial", "entidad_sigla_oficial", "sector_oficial"]:
        t[columna] = t[columna].fillna("").astype("string").str.strip()
    # Clave de cruce con Gestión-Inversión y con los relatos: el código de Hacienda a cuatro dígitos.
    t.insert(0, "entidad_codigo", t["codigo_hacienda"].where(t["codigo_hacienda"] == "", t["codigo_hacienda"].str.zfill(4)))
    con_codigo = t[t["entidad_codigo"] != ""]
    repetidos = con_codigo["entidad_codigo"][con_codigo["entidad_codigo"].duplicated()].tolist()
    if repetidos:
        raise ValueError(f"Códigos de Hacienda repetidos en {origen.name}: {repetidos}")
    return t.sort_values(["entidad_codigo", "entidad_nombre_sigla"]).reset_index(drop=True)


def guardar_silver_entidades(config: dict) -> Path:
    destino = Path(config["rutas"]["silver"]) / RELATIVA
    destino.parent.mkdir(parents=True, exist_ok=True)
    tabla_entidades(config).to_csv(destino, sep="|", index=False, encoding="utf-8-sig", lineterminator="\n")
    return destino


def nombres_normalizados(config: dict) -> dict:
    """entidad_codigo (cuatro dígitos) → Nombre_entidad_sigla, leído de Silver."""
    ruta = Path(config["rutas"]["silver"]) / RELATIVA
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}. Ejecute primero: python scripts/normalizar_entidades.py")
    t = pd.read_csv(ruta, sep="|", encoding="utf-8-sig", dtype="string", keep_default_na=False)
    t = t[t["entidad_codigo"] != ""]
    return dict(zip(t["entidad_codigo"], t["entidad_nombre_sigla"]))
