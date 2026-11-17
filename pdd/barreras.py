"""Clasifica cada relato "Retrasos y soluciones" según las barreras que menciona.

El método es deliberadamente transparente: un diccionario de expresiones
(configs/barreras.yaml) aplicado frase por frase. Cada clasificación guarda la
frase que la originó, para que un analista pueda comprobarla leyendo el texto.
"""
import re
import unicodedata

import pandas as pd
import yaml

from pdd.comun import RAIZ

ESTADOS = {  # de menor a mayor prioridad cuando se resume una meta
    "sin_retraso": "Sin retraso declarado",
    "programado": "Avance programado para más adelante",
    "sin_clasificar": "Texto sin clasificar",
    "retraso": "Retraso sin causa clasificada",
    "barrera": "Barrera identificada",
}
ORDEN_ESTADOS = list(ESTADOS.values())
ESTADOS_CON_PROBLEMA = [ESTADOS["retraso"], ESTADOS["barrera"]]

# Conectores que separan "no hubo retrasos" de la salvedad que viene después.
_CORTES_FRASE = re.compile(r"(?<=[.;:\n])\s+|\b(?:sin embargo|no obstante|aunque|pero)\b")
# Rótulo que muchas entidades escriben dentro del mismo campo: lo que sigue son soluciones.
_ROTULO_SOLUCION = re.compile(r"\bsoluci[oó]n(?:es)?\b[^.:]{0,40}:", re.IGNORECASE)


def _unir(expresiones: list[str]) -> re.Pattern:
    return re.compile("|".join(f"(?:{e})" for e in expresiones))


def cargar_diccionario() -> dict:
    with open(RAIZ / "configs" / "barreras.yaml", encoding="utf-8") as f:
        dic = yaml.safe_load(f)
    for cat in dic["categorias"].values():
        cat["regex"] = _unir(cat["expresiones"])
        cat.setdefault("es_barrera", True)
    for lista in ["sin_retraso", "solucion", "senal_de_problema", "retraso_reconocido"]:
        dic["regex_" + lista] = _unir(dic[lista])
    return dic


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para que 'contratación' y 'CONTRATACION' cuenten igual."""
    sin_tildes = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")


def _frases(texto: str) -> list[tuple[str, bool]]:
    """Divide el relato en frases y marca las que están después de un rótulo 'Soluciones:'."""
    corte = _ROTULO_SOLUCION.search(texto)
    partes = [(texto[:corte.start()], False), (texto[corte.end():], True)] if corte else [(texto, False)]
    return [(f.strip(), es_solucion) for parte, es_solucion in partes
            for f in _CORTES_FRASE.split(parte) if f and f.strip()]


def clasificar_texto(texto: str, dic: dict) -> dict:
    """Devuelve estado, si declara no tener retrasos, si reconoce un retraso y,
    por cada categoría encontrada, la primera frase que la sustenta."""
    declara_sin_retraso = menciona_dificultad = False
    evidencia: dict[str, str] = {}
    for frase, tras_rotulo_solucion in _frases(texto):
        norm = normalizar(frase)
        if dic["regex_sin_retraso"].search(norm):
            declara_sin_retraso = True
            continue
        es_solucion = tras_rotulo_solucion or bool(dic["regex_solucion"].search(norm))
        hay_senal = bool(dic["regex_senal_de_problema"].search(norm))
        # Un rótulo suelto como "Retrasos:" no es una frase: se exigen al menos tres palabras.
        if not es_solucion and len(norm.split()) >= 3 and dic["regex_retraso_reconocido"].search(norm):
            menciona_dificultad = True
        for clave, cat in dic["categorias"].items():
            if clave in evidencia or not cat["regex"].search(norm):
                continue
            # Una barrera exige frase de problema; "programado para más adelante" no.
            if not cat["es_barrera"] or (hay_senal and not es_solucion):
                evidencia[clave] = frase[:400]

    barreras = [c for c in evidencia if dic["categorias"][c]["es_barrera"]]
    if barreras:
        estado = ESTADOS["barrera"]
    elif menciona_dificultad:
        estado = ESTADOS["retraso"]
    elif evidencia:
        estado = ESTADOS["programado"]
    elif declara_sin_retraso:
        estado = ESTADOS["sin_retraso"]
    else:
        estado = ESTADOS["sin_clasificar"]
    return {"estado": estado, "declara_sin_retraso": declara_sin_retraso,
            "menciona_dificultad": menciona_dificultad, "evidencia": evidencia}


def clasificar_fragmentos(fragmentos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Agrega la clasificación a los relatos de retrasos y arma la tabla larga
    relato x barrera con su frase de evidencia."""
    dic = cargar_diccionario()
    fragmentos = fragmentos.copy()
    es_retraso = fragmentos["campo"] == "retrasos_y_soluciones"
    resultados = fragmentos.loc[es_retraso, "texto"].map(lambda t: clasificar_texto(t, dic))

    fragmentos["estado_retraso"] = resultados.map(lambda r: r["estado"])
    fragmentos["declara_sin_retraso"] = resultados.map(lambda r: r["declara_sin_retraso"])
    fragmentos["menciona_dificultad"] = resultados.map(lambda r: r["menciona_dificultad"])
    fragmentos["n_barreras"] = resultados.map(
        lambda r: sum(dic["categorias"][c]["es_barrera"] for c in r["evidencia"])).astype("Int64")

    filas = []
    for idx, res in resultados.items():
        base = fragmentos.loc[idx, ["fragmento_id", "fecha_corte", "entidad_codigo",
                                    "meta_producto_codigo", "indicador_codigo"]].to_dict()
        for clave, frase in res["evidencia"].items():
            cat = dic["categorias"][clave]
            filas.append({**base, "categoria": clave, "categoria_nombre": cat["nombre"],
                          "es_barrera": cat["es_barrera"], "frase_evidencia": frase})
    return fragmentos, pd.DataFrame(filas)


def catalogo_barreras() -> pd.DataFrame:
    dic = cargar_diccionario()
    return pd.DataFrame([
        {"categoria": clave, "categoria_nombre": cat["nombre"], "es_barrera": cat["es_barrera"],
         "descripcion": cat["descripcion"], "expresiones_buscadas": " ; ".join(cat["expresiones"])}
        for clave, cat in dic["categorias"].items()])
