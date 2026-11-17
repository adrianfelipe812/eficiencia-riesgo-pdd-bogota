"""Eficiencia técnica relativa con Análisis Envolvente de Datos (DEA), objetivo específico 1.

Idea: dentro de un grupo de metas comparables, una meta es eficiente si ninguna otra
(ni una combinación de otras) logró más avance físico con igual o menos dinero.

Decisiones, todas configurables en configs/pdd.yaml:
  - Unidad: la meta producto en un corte. Cada corte y cada grupo tiene su propia frontera.
  - Grupo comparable: mismo tipo de anualización y mismo sector. Los grupos con pocas
    metas se excluyen: con muy pocas unidades casi todas quedarían "eficientes".
  - Insumo: recursos comprometidos del año. Producto: avance físico oficial del año,
    con tope en 100 para que un sobrecumplimiento extremo no deforme la frontera.
  - Modelo BCC (rendimientos variables a escala), orientado al producto: ¿cuánto más
    avance físico podría haberse logrado con el mismo dinero?
  - Sensibilidad: se repite con los giros como insumo. Si el orden de las metas cambia
    mucho entre las dos versiones, el grupo se marca como inestable.
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.stats import spearmanr


def eficiencia_bcc(insumo: np.ndarray, producto: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve, para cada unidad, su eficiencia (0 a 1; 1 = está en la frontera) y la
    holgura del insumo (parte del dinero que, aun en la frontera, no se habría necesitado)."""
    n = len(insumo)
    eficiencia, holgura = np.zeros(n), np.zeros(n)
    for k in range(n):
        if producto[k] <= 0:                 # sin avance físico no hay nada que proyectar
            continue
        # Variables: phi (expansión posible del producto) y un peso lambda por unidad.
        c = np.r_[-1.0, np.zeros(n)]
        desigualdades = np.vstack([np.r_[0.0, insumo],                  # sum(lambda*x) <= x_k
                                   np.r_[producto[k], -producto]])      # phi*y_k <= sum(lambda*y)
        limites = np.array([insumo[k], 0.0])
        suma_uno = np.r_[0.0, np.ones(n)][None, :]
        r = linprog(c, A_ub=desigualdades, b_ub=limites, A_eq=suma_uno, b_eq=[1.0],
                    bounds=[(1, None)] + [(0, None)] * n, method="highs")
        if not r.success:
            eficiencia[k] = np.nan
            continue
        eficiencia[k] = 1.0 / r.x[0]
        holgura[k] = max(insumo[k] - float(insumo @ r.x[1:]), 0.0)
    return eficiencia, holgura


def calcular_dea(meta: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (puntajes por meta y corte, resumen por grupo y corte)."""
    cfg = config["dea"]
    base = meta[meta["tiene_datos_financieros"] & (meta["recursos_comprometidos"] > 0)].copy()
    base["grupo_dea"] = base["tipo_anualizacion_predominante"] + " | " + base["sector_principal"]
    base["producto"] = base["avance_vigencia"].clip(upper=cfg["tope_producto"])

    puntajes, grupos = [], []
    for (corte, grupo), g in base.groupby(["fecha_corte", "grupo_dea"]):
        if len(g) < cfg["minimo_metas_por_grupo"]:
            continue
        y = g["producto"].to_numpy(float)
        ef, hol = eficiencia_bcc(g["recursos_comprometidos"].to_numpy(float), y)
        girado = g["recursos_girados"].to_numpy(float)
        ef_alt = np.full(len(g), np.nan)
        con_giros = girado > 0
        if con_giros.sum() >= cfg["minimo_metas_por_grupo"]:
            ef_alt[con_giros] = eficiencia_bcc(girado[con_giros], y[con_giros])[0]
        ambos = ~np.isnan(ef_alt) & ~np.isnan(ef)
        # El acuerdo solo se puede medir si los puntajes varían dentro del grupo.
        medible = ambos.sum() >= 3 and np.ptp(ef[ambos]) > 0 and np.ptp(ef_alt[ambos]) > 0
        rho = spearmanr(ef[ambos], ef_alt[ambos]).statistic if medible else np.nan

        puntajes.append(pd.DataFrame({
            "fecha_corte": corte, "meta_producto_codigo": g["meta_producto_codigo"].to_numpy(),
            "grupo_dea": grupo, "metas_en_grupo": len(g),
            "eficiencia_dea": ef.round(4), "brecha_eficiencia": (1 - ef).round(4),
            "en_frontera": ef >= 0.9999,
            "holgura_insumo_pct": (100 * hol / g["recursos_comprometidos"].to_numpy(float)).round(2),
            "eficiencia_dea_con_giros": ef_alt.round(4)}))
        grupos.append({"fecha_corte": corte, "grupo_dea": grupo, "metas_en_grupo": len(g),
                       "metas_en_frontera": int((ef >= 0.9999).sum()),
                       "eficiencia_media": round(float(np.nanmean(ef)), 4),
                       "eficiencia_mediana": round(float(np.nanmedian(ef)), 4),
                       "acuerdo_entre_versiones": round(float(rho), 3) if not np.isnan(rho) else np.nan,
                       "grupo_estable": bool(rho >= cfg["acuerdo_minimo"]) if not np.isnan(rho) else False})
    puntajes, grupos = pd.concat(puntajes, ignore_index=True), pd.DataFrame(grupos)
    estables = grupos.set_index(["fecha_corte", "grupo_dea"])["grupo_estable"]
    puntajes["grupo_estable"] = estables.reindex(
        pd.MultiIndex.from_frame(puntajes[["fecha_corte", "grupo_dea"]])).to_numpy()
    return puntajes, grupos
