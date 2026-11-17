"""Mide el acierto del clasificador de barreras contra relatos leídos por una persona.

Las etiquetas están en auditoria/etiquetas_barreras.csv. Cada relato de la muestra se
leyó SIN ver lo que decía el clasificador y se anotó qué barreras narra de verdad.
Hay dos conjuntos:
  desarrollo  sirvió para corregir el diccionario (por eso su resultado es optimista)
  prueba      se sacó después de las correcciones y no se usó para ajustar nada: es
              la medida que se debe citar

Como la muestra tomó más relatos de los grupos escasos (los que tienen barrera), cada
relato lleva un "peso": a cuántos relatos del total representa. Las medidas ponderadas
usan ese peso y por eso valen para el conjunto completo de relatos.

Dos medidas:
  precisión      de lo que el clasificador marcó, qué parte era correcta
  sensibilidad   de lo que había de verdad, qué parte encontró el clasificador
"""
import pandas as pd

from pdd.barreras import ESTADOS_CON_PROBLEMA
from pdd.comun import RAIZ

RUTA_ETIQUETAS = RAIZ / "auditoria" / "etiquetas_barreras.csv"
NO_BARRERA = {"programacion_diferida"}       # categoría que explica el avance pero no es obstáculo
SIN_CATEGORIA = "otra"                        # barrera real que no encaja en ninguna categoría


# Las lecturas se anotaron con nueve categorías. Cuatro resultaron poco fiables por
# separado y se fusionaron en el diccionario; aquí se aplica la misma fusión a las
# lecturas, que conservan el detalle original en el archivo.
FUSION = dict.fromkeys(["presupuesto", "terceros", "tecnico_y_obra", "informacion_y_sistemas"],
                       "coordinacion_recursos_y_tecnica")


def _conjunto(texto) -> set:
    return {FUSION.get(c, c) for c in str(texto).split(";") if c and c != "nan"}


def _medidas(vp: float, fp: float, fn: float) -> dict:
    precision = vp / (vp + fp) if vp + fp else float("nan")
    sensibilidad = vp / (vp + fn) if vp + fn else float("nan")
    f1 = 2 * precision * sensibilidad / (precision + sensibilidad) if precision + sensibilidad else float("nan")
    return {"precision_pct": round(100 * precision, 1), "sensibilidad_pct": round(100 * sensibilidad, 1),
            "f1_pct": round(100 * f1, 1)}


def evaluar_clasificador(fragmentos: pd.DataFrame, barreras: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (detalle relato por relato, resumen de medidas por conjunto)."""
    etiquetas = pd.read_csv(RUTA_ETIQUETAS, sep=";", dtype=str, keep_default_na=False)
    etiquetas["peso"] = etiquetas["peso"].astype(float)
    predichas = barreras.groupby("fragmento_id")["categoria"].agg(lambda s: ";".join(sorted(s)))
    d = etiquetas.merge(fragmentos[["fragmento_id", "estado_retraso", "texto"]], on="fragmento_id", how="left")
    if d["estado_retraso"].isna().any():
        raise ValueError("Hay etiquetas de relatos que ya no existen en la extracción.")
    d["barreras_clasificador"] = d["fragmento_id"].map(predichas).fillna("")

    reales = d["barreras_reales"].map(_conjunto)
    marcadas = d["barreras_clasificador"].map(_conjunto)
    d["hay_barrera_real"] = reales.map(lambda s: bool(s - NO_BARRERA))
    d["hay_barrera_clasificador"] = d["estado_retraso"].isin(ESTADOS_CON_PROBLEMA)
    d["categorias_acertadas"] = [len((r & m) - NO_BARRERA) for r, m in zip(reales, marcadas)]
    d["categorias_sobrantes"] = [len(m - r - NO_BARRERA) for r, m in zip(reales, marcadas)]
    d["categorias_omitidas"] = [len(r - m - NO_BARRERA - {SIN_CATEGORIA}) for r, m in zip(reales, marcadas)]
    d["veredicto"] = [
        "Acierto" if real == marcada and sobran == 0 and faltan == 0
        else "Acierto parcial" if real and marcada
        else "Barrera no detectada" if real
        else "Falsa alarma" if marcada else "Acierto"
        for real, marcada, sobran, faltan in zip(d["hay_barrera_real"], d["hay_barrera_clasificador"],
                                                d["categorias_sobrantes"], d["categorias_omitidas"])]

    filas = []
    for conjunto, g in d.groupby("conjunto"):
        for ponderado, w in [("No (conteo de la muestra)", pd.Series(1.0, index=g.index)), ("Sí (vale para todos los relatos)", g["peso"])]:
            real, marcada = g["hay_barrera_real"], g["hay_barrera_clasificador"]
            filas.append({"conjunto": conjunto, "relatos_leidos": len(g), "ponderado": ponderado,
                          "medida": "¿El relato narra alguna barrera?",
                          **_medidas((w * (real & marcada)).sum(), (w * (~real & marcada)).sum(),
                                     (w * (real & ~marcada)).sum())})
            filas.append({"conjunto": conjunto, "relatos_leidos": len(g), "ponderado": ponderado,
                          "medida": "¿Acertó la categoría de cada barrera?",
                          **_medidas((w * g["categorias_acertadas"]).sum(), (w * g["categorias_sobrantes"]).sum(),
                                     (w * g["categorias_omitidas"]).sum())})
        # Detalle por categoría (conteo simple): muestra cuáles categorías son más y menos fiables.
        for categoria in sorted(set().union(*reales[g.index], *marcadas[g.index]) - NO_BARRERA - {SIN_CATEGORIA}):
            en_real = reales[g.index].map(lambda s: categoria in s)
            en_marcada = marcadas[g.index].map(lambda s: categoria in s)
            filas.append({"conjunto": conjunto, "relatos_leidos": len(g), "ponderado": "No (conteo de la muestra)",
                          "medida": f"Categoría: {categoria} ({int(en_real.sum())} casos reales)",
                          **_medidas((en_real & en_marcada).sum(), (~en_real & en_marcada).sum(),
                                     (en_real & ~en_marcada).sum())})
    detalle = d[["conjunto", "fragmento_id", "veredicto", "barreras_reales", "barreras_clasificador",
                 "estado_retraso", "estrato_muestreo", "peso", "texto"]]
    return detalle, pd.DataFrame(filas)
