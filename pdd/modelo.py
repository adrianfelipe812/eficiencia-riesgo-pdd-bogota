"""Variable de riesgo y modelo predictivo (objetivo específico 3).

Pregunta: con lo que se sabe de una meta en un corte, ¿se puede anticipar que en el
corte SIGUIENTE estará rezagada?

Reglas que protegen el resultado:
  - Partición temporal: se entrena con los cortes antiguos, se elige el modelo con un
    corte intermedio y se mide con los más recientes. Nunca se mezclan al azar.
  - Las variables explicativas son solo las conocidas en el corte; lo que pasa después
    está únicamente en las columnas de riesgo.
  - Se comparan cuatro conjuntos de variables, cada uno añade algo al anterior. Así se
    ve cuánto aporta lo físico, la eficiencia DEA y el texto frente a lo financiero.
  - Las probabilidades se calibran (para que "30 %" signifique 30 de cada 100) y el umbral de
    alerta se elige por costos: omitir un rezago cuesta más que una falsa alarma.
  - Cada alerta lleva su explicación: las variables que más suben o bajan su riesgo (SHAP).
"""
import numpy as np
import pandas as pd
import shap
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, f1_score, fbeta_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from pdd.barreras import ESTADOS_CON_PROBLEMA

FINANCIERAS = ["pct_compromisos", "pct_giros", "log_recursos_programados", "trimestre"]
FISICAS = ["avance_vigencia", "avance_transcurrido", "avance_plan", "brecha_fisico_financiera",
           "pct_actividades_entrega_cero", "n_actividades", "n_entidades", "en_rezago_actual",
           "es_suma", "es_constante", "es_creciente"]
EFICIENCIA = ["eficiencia_dea", "holgura_insumo_pct"]
TEXTO = ["narra_problema", "menciona_dificultad_num", "n_relatos_retraso", "barrera_contratacion",
         "barrera_tramites_y_permisos", "barrera_talento_y_capacidad", "barrera_demanda_y_poblacion",
         "barrera_factores_externos"]
CONJUNTOS = {
    "1. Solo financiero (línea base)": FINANCIERAS,
    "2. Financiero + físico": FINANCIERAS + FISICAS,
    "3. Financiero + físico + DEA": FINANCIERAS + FISICAS + EFICIENCIA,
    "4. Integrado (+ texto)": FINANCIERAS + FISICAS + EFICIENCIA + TEXTO,
}
BASE, INTEGRADO = list(CONJUNTOS)[0], list(CONJUNTOS)[-1]


def agregar_objetivos(meta: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Calcula tres definiciones de riesgo. Todas miran un momento posterior al corte."""
    cfg = config["riesgo"]
    t = meta.sort_values(["meta_producto_codigo", "fecha_corte"]).reset_index(drop=True)
    # Rezago relativo: la meta está en el 20 % más bajo de avance entre las metas de su
    # mismo tipo de anualización en ese corte. Compara con metas que se comportan parecido,
    # así una meta que entrega por hitos no queda marcada solo por estar a mitad de año.
    grupo = t.groupby(["fecha_corte", *cfg["grupo_relativo"]])["avance_vigencia"]
    limite = grupo.transform(lambda s: s.quantile(cfg["cuantil_relativo"]))
    # Si el límite coincide con el avance más alto del grupo (pasa en diciembre, cuando la
    # mayoría llega a 100 %), solo quedan rezagadas las que están por debajo de ese máximo.
    t["en_rezago_actual"] = ((t["avance_vigencia"] <= limite) & (t["avance_vigencia"] < grupo.transform("max"))
                             ).astype("Int64").where(limite.notna())

    por_meta = t.groupby("meta_producto_codigo")
    t["fecha_corte_siguiente"] = por_meta["fecha_corte"].shift(-1)
    t["avance_vigencia_siguiente"] = por_meta["avance_vigencia"].shift(-1)
    t["riesgo_relativo_siguiente"] = por_meta["en_rezago_actual"].shift(-1)
    esperado = 100 * t["fecha_corte_siguiente"].dt.month / 12
    t["riesgo_lineal_siguiente"] = ((t["avance_vigencia_siguiente"] < cfg["fraccion_minima_del_esperado"] * esperado)
                                    .astype("Int64").where(t["fecha_corte_siguiente"].notna()))
    # Riesgo al cierre: en diciembre el avance del año sí es exigible completo.
    cierre = (t[t["fecha_corte"].dt.month == 12].set_index(["meta_producto_codigo", "vigencia"])["avance_vigencia"])
    al_cierre = pd.Series(cierre.reindex(pd.MultiIndex.from_frame(t[["meta_producto_codigo", "vigencia"]])).to_numpy(),
                          index=t.index)
    t["riesgo_cierre_anio"] = ((al_cierre < cfg["umbral_cierre"]).astype("Int64")
                               .where(al_cierre.notna() & (t["fecha_corte"].dt.month != 12)))
    return t.sort_values(["fecha_corte", "meta_producto_codigo"]).reset_index(drop=True)


def _variables(meta: pd.DataFrame) -> pd.DataFrame:
    x = meta.copy()
    x["log_recursos_programados"] = np.log1p(x["recursos_programados"].astype(float))
    x["trimestre"] = x["fecha_corte"].dt.quarter
    for tipo in ["Suma", "Constante", "Creciente"]:
        x[f"es_{tipo.lower()}"] = (x["tipo_anualizacion_predominante"] == tipo).astype(float).where(
            x["tipo_anualizacion_predominante"].notna())
    con_relato = x["n_relatos_retraso"].notna()
    x["narra_problema"] = x["estado_narrativa"].isin(ESTADOS_CON_PROBLEMA).astype(float).where(con_relato)
    x["menciona_dificultad_num"] = x["menciona_dificultad"].astype(float)
    return x[sorted({c for cols in CONJUNTOS.values() for c in cols})].astype(float)


def _candidatos(semilla: int) -> dict:
    # Sin ponderar las clases: así la probabilidad estimada se puede leer como tal
    # (una meta con 0,30 tiene cerca de 30 % de posibilidades de quedar rezagada).
    return {
        "Regresión logística": make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                                             LogisticRegression(max_iter=2000)),
        "Árboles potenciados": HistGradientBoostingClassifier(max_depth=3, learning_rate=0.06, max_iter=150,
                                                              random_state=semilla),
    }


def _umbral_f1(y, p) -> float:
    precision, recall, umbrales = precision_recall_curve(y, p)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-9, None)
    return float(umbrales[np.argmax(f1[:-1])])


# ---------------------------------------------------------------------------------------
# Costos de error asimétricos
#
# Omitir una meta que sí se rezaga (falso negativo) cuesta más que revisar una que al final
# no se rezagó (falsa alarma): la primera pierde la ventana de corrección; la segunda, unas
# horas de análisis. Por eso el umbral de alerta no se elige maximizando F1 (que trata ambos
# errores igual), sino minimizando  Costo = C_FN · omitidos + C_FP · falsas alarmas.
# ---------------------------------------------------------------------------------------
def umbral_bayes(costo_fn: float, costo_fp: float) -> float:
    """Umbral que minimiza el costo esperado cuando las probabilidades están calibradas.

    Para una meta con probabilidad p de rezagarse, no alertar cuesta en promedio p·C_FN y
    alertar cuesta (1 − p)·C_FP. Conviene alertar cuando p·C_FN ≥ (1 − p)·C_FP, es decir,
    cuando p ≥ C_FP / (C_FP + C_FN). Con C_FN = 5 y C_FP = 1, el umbral es 1/6 ≈ 0,167.
    """
    return costo_fp / (costo_fp + costo_fn)


def umbral_minimo_costo(y, p, costo_fn: float, costo_fp: float) -> float:
    """Umbral que minimiza el costo observado en unos datos (se alerta si p ≥ umbral).
    Si varios empatan, se queda con el más alto: igual costo con menos alertas."""
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    candidatos = np.unique(np.r_[p, 1.0 + 1e-9])
    costos = np.array([costo_total(y, p >= t, costo_fn, costo_fp) for t in candidatos])
    return float(candidatos[np.flatnonzero(costos == costos.min())[-1]])


def costo_total(y, alerta, costo_fn: float, costo_fp: float) -> float:
    y, alerta = np.asarray(y).astype(bool), np.asarray(alerta).astype(bool)
    return float(costo_fn * (y & ~alerta).sum() + costo_fp * (~y & alerta).sum())


# ---------------------------------------------------------------------------------------
# Calibración de probabilidades
#
# Si el tablero dice "30 % de riesgo", de cada 100 metas con ese valor deberían rezagarse
# cerca de 30. Se prueban tres opciones y se elige, en el corte de validación, la de menor
# error de Brier (promedio de (probabilidad − resultado)²): dejar el modelo como está,
# escalamiento de Platt (una curva sigmoide) o regresión isotónica (una escalera creciente).
# ---------------------------------------------------------------------------------------
ETIQUETA_CALIBRACION = {"ninguna": "Sin calibrar", "sigmoid": "Platt (sigmoide)", "isotonic": "Isotónica"}


def _ajustar(algoritmo: str, metodo: str, X: pd.DataFrame, y: pd.Series, grupos: pd.Series, semilla: int):
    """Entrena el algoritmo y, si se pide, calibra sus probabilidades.

    La calibración usa 5 pliegues agrupados por meta: una misma meta nunca queda a la vez
    en la parte que entrena y en la que calibra (sus cortes se parecen entre sí, y mezclarlos
    haría la calibración demasiado optimista). Luego el modelo se reentrena con todos los datos.
    """
    base = _candidatos(semilla)[algoritmo]
    if metodo == "ninguna":
        return base.fit(X, y)
    pliegues = list(GroupKFold(n_splits=5).split(X, y, grupos))
    return CalibratedClassifierCV(base, method=metodo, cv=pliegues, ensemble=False).fit(X, y)


def _base(modelo):
    """El clasificador original, sin la capa de calibración."""
    return modelo.calibrated_classifiers_[0].estimator if isinstance(modelo, CalibratedClassifierCV) else modelo


# ---------------------------------------------------------------------------------------
# Explicaciones con SHAP
#
# La importancia por permutación dice qué variables pesan en general. SHAP reparte, para
# cada meta, su predicción entre las variables: cuánto sube o baja el riesgo cada una frente
# a una meta promedio. Las contribuciones se calculan sobre el clasificador original, en
# escala de log-odds; la calibración es creciente, así que no cambia qué variable empuja
# hacia arriba ni el orden de importancia.
# ---------------------------------------------------------------------------------------
NOMBRES = {
    "pct_compromisos": "Dinero comprometido", "pct_giros": "Dinero girado",
    "log_recursos_programados": "Recursos programados", "trimestre": "Época del año del corte",
    "avance_vigencia": "Avance del año", "avance_transcurrido": "Avance transcurrido",
    "avance_plan": "Avance del cuatrienio", "brecha_fisico_financiera": "Dinero por delante del avance",
    "pct_actividades_entrega_cero": "Actividades sin entrega", "n_actividades": "Número de actividades",
    "n_entidades": "Número de entidades", "en_rezago_actual": "Ya rezagada en este corte",
    "es_suma": "Anualización tipo Suma", "es_constante": "Anualización tipo Constante",
    "es_creciente": "Anualización tipo Creciente", "eficiencia_dea": "Eficiencia DEA",
    "holgura_insumo_pct": "Holgura de recursos", "narra_problema": "La entidad narra un problema",
    "menciona_dificultad_num": "La entidad reconoce una dificultad", "n_relatos_retraso": "Relatos de retraso",
    "barrera_contratacion": "Narra barrera de contratación",
    "barrera_tramites_y_permisos": "Narra barrera de trámites y permisos",
    "barrera_talento_y_capacidad": "Narra barrera de talento humano",
    "barrera_demanda_y_poblacion": "Narra barrera de demanda",
    "barrera_factores_externos": "Narra factores externos",
}


def _contribuciones(modelo, X_fondo: pd.DataFrame, X: pd.DataFrame) -> np.ndarray:
    """Contribución SHAP de cada variable (filas = metas, columnas = variables), en log-odds."""
    base = _base(modelo)
    if isinstance(base, HistGradientBoostingClassifier):
        return np.asarray(shap.TreeExplainer(base).shap_values(X))       # exacto para árboles

    def logit(datos):
        p = np.clip(base.predict_proba(pd.DataFrame(datos, columns=X.columns))[:, 1], 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p))
    masker = shap.maskers.Independent(X_fondo, max_samples=100)
    return shap.explainers.Permutation(logit, masker, seed=0)(X).values


def _valor_legible(variable: str, v: float) -> str:
    if pd.isna(v):
        return "sin dato"
    if variable.startswith(("es_", "en_rezago", "narra_", "menciona_", "barrera_")):
        return "sí" if v >= 0.5 else "no"
    if variable == "log_recursos_programados":
        return f"${np.expm1(v):,.0f} millones".replace(",", ".")
    if variable == "eficiencia_dea":
        return f"{v:.2f}".replace(".", ",")
    if variable == "trimestre":
        return ["marzo", "junio", "septiembre", "diciembre"][int(v) - 1]
    if variable in ("n_actividades", "n_entidades", "n_relatos_retraso"):
        return f"{v:.0f}"
    if variable == "brecha_fisico_financiera":
        return f"{v:+.1f} puntos".replace(".", ",")
    return f"{v:.1f} %".replace(".", ",")


def _explicar(valores: pd.Series, contribuciones: np.ndarray, n: int = 3) -> str:
    """Las n variables que más mueven el riesgo de una meta, en una frase."""
    orden = np.argsort(-np.abs(contribuciones))[:n]
    return "; ".join(f"{NOMBRES[valores.index[i]]}: {_valor_legible(valores.index[i], valores.iloc[i])} "
                     f"({'sube' if contribuciones[i] > 0 else 'baja'} el riesgo)" for i in orden)


def entrenar_y_evaluar(meta: pd.DataFrame, config: dict, completo: bool = True) -> dict[str, pd.DataFrame]:
    """Entrena, calibra, elige el umbral por costos, evalúa y explica.

    Con completo=False solo calcula las métricas, sin calibrar ni explicar (lo usa la
    comparación de definiciones de riesgo, que se juzga con medidas de orden como ROC-AUC).
    """
    cfg = config["modelo"]
    semilla, objetivos = cfg["semilla"], cfg["objetivos"]
    c_fn, c_fp, beta = cfg["costo_rezago_no_detectado"], cfg["costo_falsa_alarma"], cfg["beta"]
    metodos = cfg["calibracion_candidatas"] if completo else ["ninguna"]
    X_todo, grupos = _variables(meta), meta["meta_producto_codigo"]
    cortes = sorted(meta.loc[meta["tiene_datos_financieros"], "fecha_corte"].unique())
    metricas, importancias, predicciones, particion, calibracion, costos, explicaciones = [], [], [], [], [], [], []

    for objetivo in objetivos:
        usable = meta["tiene_datos_financieros"] & meta[objetivo].notna()
        con_objetivo = [c for c in cortes if (usable & (meta["fecha_corte"] == c)).any()]
        n_prueba, n_val = cfg["cortes_prueba"], cfg["cortes_validacion"]
        c_ent, c_val, c_pru = (con_objetivo[:-(n_prueba + n_val)], con_objetivo[-(n_prueba + n_val):-n_prueba],
                               con_objetivo[-n_prueba:])
        partes = {"entrenamiento": c_ent, "validacion": c_val, "prueba": c_pru}
        filas = {k: usable & meta["fecha_corte"].isin(v) for k, v in partes.items()}
        y = meta[objetivo].astype(float)
        for k, v in partes.items():
            particion.append({"objetivo": objetivo, "parte": k, "cortes": ", ".join(pd.Timestamp(c).strftime("%d/%m/%Y") for c in v),
                              "filas": int(filas[k].sum()), "pct_en_riesgo": round(100 * y[filas[k]].mean(), 1),
                              "filas_con_relato": int((filas[k] & meta["n_relatos_retraso"].notna()).sum())})
        ent, val, pru = filas["entrenamiento"], filas["validacion"], filas["prueba"]
        ent_val, y_v, y_p = ent | val, y[val].to_numpy(), y[pru].to_numpy()

        # Se usa el MISMO algoritmo para los cuatro conjuntos de variables, de modo que la
        # diferencia entre ellos se deba a las variables y no al algoritmo. Se elige el que
        # mejor ordena las metas en promedio en el corte de validación.
        validacion = {}
        for algoritmo in _candidatos(semilla):
            for nombre, columnas in CONJUNTOS.items():
                modelo = _candidatos(semilla)[algoritmo].fit(X_todo.loc[ent, columnas], y[ent])
                validacion[algoritmo, nombre] = average_precision_score(y_v, modelo.predict_proba(X_todo.loc[val, columnas])[:, 1])
        algoritmo = max(_candidatos(semilla), key=lambda a: np.mean([validacion[a, n] for n in CONJUNTOS]))

        probabilidades, elegido = {}, {}
        for nombre, columnas in CONJUNTOS.items():
            # 1. Calibración: entre las candidatas, la de menor error de Brier en validación.
            p_val = {m: _ajustar(algoritmo, m, X_todo.loc[ent, columnas], y[ent], grupos[ent], semilla)
                        .predict_proba(X_todo.loc[val, columnas])[:, 1] for m in metodos}
            metodo = min(metodos, key=lambda m: brier_score_loss(y_v, p_val[m]))
            # 2. Umbral de decisión según la regla configurada.
            umbrales = {"bayes": umbral_bayes(c_fn, c_fp), "f1": _umbral_f1(y_v, p_val[metodo]),
                        "costo_validacion": umbral_minimo_costo(y_v, p_val[metodo], c_fn, c_fp)}
            umbral = umbrales[cfg["regla_umbral"]]
            # 3. Modelo de evaluación (entrenamiento + validación) medido en los cortes de prueba.
            modelo = _ajustar(algoritmo, metodo, X_todo.loc[ent_val, columnas], y[ent_val], grupos[ent_val], semilla)
            p = modelo.predict_proba(X_todo.loc[pru, columnas])[:, 1]
            p_sin = (p if metodo == "ninguna" or not completo else
                     _ajustar(algoritmo, "ninguna", X_todo.loc[ent_val, columnas], y[ent_val], grupos[ent_val], semilla)
                     .predict_proba(X_todo.loc[pru, columnas])[:, 1])
            alerta = p >= umbral
            # La capacidad de ORDENAR las metas (PR-AUC, ROC-AUC y la prueba de H1) se mide con las
            # probabilidades sin calibrar: la regresión isotónica convierte la curva en escalera, crea
            # empates y bajaría el PR-AUC de forma artificial. Si cada conjunto quedara con un método
            # de calibración distinto, la comparación entre conjuntos mediría la calibración y no las
            # variables. Las medidas que dependen del umbral (alertas, costos, Brier) usan las calibradas.
            probabilidades[nombre], elegido[nombre] = p_sin, (umbral, modelo, metodo, p_sin, p)
            metricas.append({
                "objetivo": objetivo, "conjunto_de_variables": nombre, "algoritmo_elegido": algoritmo,
                "n_variables": len(columnas), "calibracion": ETIQUETA_CALIBRACION[metodo],
                "pr_auc_validacion": round(validacion[algoritmo, nombre], 3),
                "pr_auc_prueba": round(average_precision_score(y_p, p_sin), 3),
                "roc_auc_prueba": round(roc_auc_score(y_p, p_sin), 3), "pr_auc_al_azar": round(float(y_p.mean()), 3),
                "brier_prueba": round(brier_score_loss(y_p, p), 4),
                "brier_prueba_sin_calibrar": round(brier_score_loss(y_p, p_sin), 4),
                "umbral_decision": round(umbral, 4), "metas_senaladas": int(alerta.sum()),
                "rezagos_detectados": int((alerta & (y_p == 1)).sum()), "rezagos_omitidos": int((~alerta & (y_p == 1)).sum()),
                "falsas_alarmas": int((alerta & (y_p == 0)).sum()),
                "precision_prueba": round(precision_score(y_p, alerta, zero_division=0), 3),
                "sensibilidad_prueba": round(recall_score(y_p, alerta), 3),
                "f1_prueba": round(f1_score(y_p, alerta), 3), "fbeta_prueba": round(fbeta_score(y_p, alerta, beta=beta), 3),
                "costo_total_prueba": costo_total(y_p, alerta, c_fn, c_fp),
                "costo_con_umbral_f1": costo_total(y_p, p >= umbrales["f1"], c_fn, c_fp)})

        # ¿La mejora sobre la línea base es verificable? (hipótesis H1 frente a H0)
        # Se repite la medición 2.000 veces remuestreando las metas de prueba.
        rng = np.random.default_rng(semilla)
        remuestras = [i for i in (rng.integers(0, len(y_p), len(y_p)) for _ in range(2000)) if 0 < y_p[i].sum() < len(i)]
        ap = {n: np.array([average_precision_score(y_p[i], probabilidades[n][i]) for i in remuestras]) for n in CONJUNTOS}
        for fila in metricas:
            if fila["objetivo"] == objetivo:
                # El intervalo dice si la mejora es verificable (no incluye el cero) o podría deberse al azar.
                difs = ap[fila["conjunto_de_variables"]] - ap[BASE]
                bajo, alto = np.percentile(difs, [2.5, 97.5])
                es_base = fila["conjunto_de_variables"] == BASE
                fila["mejora_sobre_base"] = np.nan if es_base else round(float(difs.mean()), 3)
                fila["mejora_ic95_bajo"] = np.nan if es_base else round(float(bajo), 3)
                fila["mejora_ic95_alto"] = np.nan if es_base else round(float(alto), 3)
                fila["mejora_verificable"] = "" if es_base else ("Sí" if bajo > 0 else "No")
        # ¿Y la eficiencia DEA y el texto aportan algo más allá de lo financiero y lo físico?
        extra = ap[INTEGRADO] - ap[list(CONJUNTOS)[1]]
        bajo, alto = np.percentile(extra, [2.5, 97.5])
        metricas[-1]["aporte_dea_y_texto"] = round(float(extra.mean()), 3)
        metricas[-1]["aporte_ic95"] = f"{bajo:.3f} a {alto:.3f}"
        metricas[-1]["aporte_verificable"] = "Sí" if bajo > 0 else "No"
        if not completo:
            continue

        umbral, modelo, metodo, p_sin, p = elegido[INTEGRADO]
        columnas = CONJUNTOS[INTEGRADO]

        # Confiabilidad: en cada décimo de metas ordenadas por probabilidad, ¿la probabilidad
        # media se parece a la proporción que de verdad se rezagó?
        versiones = [("Sin calibrar", p_sin)] + ([(ETIQUETA_CALIBRACION[metodo], p)] if metodo != "ninguna" else [])
        for version, probs in versiones:
            tramos = pd.qcut(pd.Series(probs).rank(method="first"), 10, labels=False)
            for k, g in pd.DataFrame({"p": probs, "y": y_p, "t": tramos}).groupby("t"):
                calibracion.append({"objetivo": objetivo, "version": version, "tramo": int(k) + 1, "metas": len(g),
                                    "probabilidad_media": round(float(g["p"].mean()), 4),
                                    "proporcion_rezagada": round(float(g["y"].mean()), 4)})

        # Sensibilidad a la razón de costos: qué pasaría si omitir un rezago costara 1, 2, 3, 5 o 10 veces una falsa alarma.
        for razon in [1, 2, 3, 5, 10]:
            t = umbral_bayes(razon, 1)
            a = p >= t
            costos.append({"objetivo": objetivo, "costo_omitir_frente_a_falsa_alarma": razon, "umbral": round(t, 4),
                           "metas_senaladas": int(a.sum()), "rezagos_detectados": int((a & (y_p == 1)).sum()),
                           "rezagos_omitidos": int((~a & (y_p == 1)).sum()), "falsas_alarmas": int((a & (y_p == 0)).sum()),
                           "precision": round(precision_score(y_p, a, zero_division=0), 3),
                           "sensibilidad": round(recall_score(y_p, a), 3), "costo_total": costo_total(y_p, a, razon, 1),
                           "es_la_configurada": "Sí" if razon == c_fn / c_fp else "No"})

        # Importancia global: por permutación y por SHAP (contribución media absoluta), en los cortes de prueba.
        imp = permutation_importance(modelo, X_todo.loc[pru, columnas], y_p, n_repeats=10,
                                     random_state=semilla, scoring="average_precision")
        shap_prueba = np.abs(_contribuciones(modelo, X_todo.loc[ent_val, columnas], X_todo.loc[pru, columnas])).mean(axis=0)
        grupo = lambda c: ("Financiera" if c in FINANCIERAS else "Física" if c in FISICAS
                           else "Eficiencia DEA" if c in EFICIENCIA else "Texto")
        importancias += [{"objetivo": objetivo, "variable": c, "nombre": NOMBRES[c], "tipo": grupo(c),
                          "importancia": round(float(m), 4), "shap_medio_abs": round(float(s), 4)}
                         for c, m, s in zip(columnas, imp.importances_mean, shap_prueba)]

        # Alerta para el corte más reciente: se entrena con todo lo que tiene resultado conocido.
        ultimo = meta["fecha_corte"] == meta["fecha_corte"].max()
        final = _ajustar(algoritmo, metodo, X_todo.loc[usable, columnas], y[usable], grupos[usable], semilla)
        X_ult = X_todo.loc[ultimo, columnas]
        prob = final.predict_proba(X_ult)[:, 1]
        contrib = _contribuciones(final, X_todo.loc[usable, columnas], X_ult)
        pred = meta.loc[ultimo, ["fecha_corte", "meta_producto_codigo", "meta_producto_nombre", "sector_principal",
                                 "entidad_principal", "avance_vigencia", "pct_compromisos", "eficiencia_dea",
                                 "estado_narrativa"]].copy()
        pred.insert(2, "objetivo", objetivo)
        pred["probabilidad_riesgo"] = prob.round(4)
        # Alta: probabilidad igual o mayor que la configurada. Media: supera el umbral de
        # decisión por costos (revisarla cuesta menos, en promedio, que omitirla). Baja: el resto.
        pred["nivel_alerta"] = np.select([prob >= cfg["alerta_alta"], prob >= umbral], ["Alta", "Media"], "Baja")
        pred["umbral_alerta_alta"] = cfg["alerta_alta"]
        pred["umbral_decision"] = round(umbral, 4)
        pred["explicacion"] = [_explicar(X_ult.iloc[k], contrib[k]) for k in range(len(X_ult))]
        predicciones.append(pred.sort_values("probabilidad_riesgo", ascending=False))
        for k, codigo in enumerate(meta.loc[ultimo, "meta_producto_codigo"]):
            for j in np.argsort(-np.abs(contrib[k]))[:5]:
                explicaciones.append({"objetivo": objetivo, "meta_producto_codigo": codigo, "variable": columnas[j],
                                      "nombre": NOMBRES[columnas[j]], "valor": _valor_legible(columnas[j], X_ult.iloc[k, j]),
                                      "contribucion_log_odds": round(float(contrib[k, j]), 4),
                                      "efecto": "Sube el riesgo" if contrib[k, j] > 0 else "Baja el riesgo"})

    if not completo:
        return {"gold_modelo_metricas": pd.DataFrame(metricas)}
    importancias = pd.DataFrame(importancias).sort_values(["objetivo", "importancia"], ascending=[True, False])
    return {"gold_modelo_particion": pd.DataFrame(particion), "gold_modelo_metricas": pd.DataFrame(metricas),
            "gold_modelo_importancia": importancias, "gold_modelo_calibracion": pd.DataFrame(calibracion),
            "gold_modelo_costos": pd.DataFrame(costos), "gold_modelo_explicacion": pd.DataFrame(explicaciones),
            "gold_prediccion_riesgo": pd.concat(predicciones, ignore_index=True)}


def asociacion_barreras_eficiencia(meta: pd.DataFrame) -> pd.DataFrame:
    """Objetivo 2: ¿las metas que narran un problema tienen menor eficiencia DEA?
    Prueba de Mann-Whitney (compara dos grupos sin suponer forma de la distribución)."""
    from scipy.stats import mannwhitneyu
    d = meta[meta["eficiencia_dea"].notna() & meta["n_relatos_retraso"].notna()].copy()
    d["narra_problema"] = d["estado_narrativa"].isin(ESTADOS_CON_PROBLEMA).astype(int)
    # Se prueba dentro de cada corte: la eficiencia cambia mucho según la época del año,
    # y mezclar cortes haría parecer asociación lo que es solo calendario.
    filas = []
    for corte, d in d.groupby("fecha_corte"):
      for nombre in ["narra_problema", "menciona_dificultad", "barrera_contratacion", "barrera_tramites_y_permisos",
                   "barrera_talento_y_capacidad", "barrera_demanda_y_poblacion", "barrera_factores_externos"]:
        con, sin = d.loc[d[nombre].astype(float) == 1, "eficiencia_dea"], d.loc[d[nombre].astype(float) == 0, "eficiencia_dea"]
        if len(con) < 8:
            continue
        p = mannwhitneyu(con, sin, alternative="two-sided").pvalue
        filas.append({"fecha_corte": corte, "caracteristica": nombre, "metas_con": len(con), "metas_sin": len(sin),
                      "eficiencia_mediana_con": round(con.median(), 3), "eficiencia_mediana_sin": round(sin.median(), 3),
                      "diferencia": round(con.median() - sin.median(), 3), "valor_p": round(float(p), 4),
                      "diferencia_significativa": "Sí" if p < 0.05 else "No"})
    return pd.DataFrame(filas)


GRUPOS_DE_COMPARACION = {"Todas las metas": [], "Mismo tipo de anualización": ["tipo_anualizacion_predominante"],
                         "Mismo tipo y sector": ["tipo_anualizacion_predominante", "sector_principal"]}
COLUMNAS_DE_OBJETIVO = ["en_rezago_actual", "fecha_corte_siguiente", "avance_vigencia_siguiente",
                        "riesgo_relativo_siguiente", "riesgo_lineal_siguiente", "riesgo_cierre_anio"]


def comparar_definiciones_riesgo(meta: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Compara nueve variantes del rezago relativo para sustentar cuál se usa.

    Una variante combina qué fracción de metas se considera rezagada (20, 25 o 33 %) y con
    qué metas se compara cada una. Se juzga con dos preguntas:
      VALIDEZ       ¿la etiqueta señala subejecución real? En diciembre el avance del año es
                    exigible completo: de las metas marcadas en diciembre, cuántas cerraron
                    bajo 90 % (precisión), y de las que cerraron bajo 90 %, cuántas quedaron
                    marcadas (cobertura).
      ANTICIPACIÓN  ¿el modelo logra anticiparla? ROC-AUC en los cortes de prueba (0,5 = azar;
                    permite comparar variantes que marcan fracciones distintas).
    """
    import copy
    base = meta.drop(columns=COLUMNAS_DE_OBJETIVO)
    actual = (config["riesgo"]["cuantil_relativo"], config["riesgo"]["grupo_relativo"])
    filas = []
    for nombre, columnas in GRUPOS_DE_COMPARACION.items():
        for cuantil in [0.20, 0.25, 0.33]:
            cfg = copy.deepcopy(config)
            cfg["riesgo"].update(cuantil_relativo=cuantil, grupo_relativo=columnas)
            cfg["modelo"]["objetivos"] = ["riesgo_relativo_siguiente"]
            t = agregar_objetivos(base, cfg)
            dic = t[(t["fecha_corte"].dt.month == 12) & t["en_rezago_actual"].notna()]
            marcada, bajo = dic["en_rezago_actual"] == 1, dic["avance_vigencia"] < cfg["riesgo"]["umbral_cierre"]
            p, c = (marcada & bajo).sum() / marcada.sum(), (marcada & bajo).sum() / bajo.sum()
            m = entrenar_y_evaluar(t, cfg, completo=False)["gold_modelo_metricas"]
            m = m[m["conjunto_de_variables"] == INTEGRADO].iloc[0]
            por_corte = t.groupby("fecha_corte")["riesgo_relativo_siguiente"].mean().dropna()
            filas.append({
                "comparada_con": nombre, "fraccion_rezagada": cuantil,
                "pct_marcado_min": round(100 * por_corte.min(), 1), "pct_marcado_max": round(100 * por_corte.max(), 1),
                "validez_precision_pct": round(100 * p, 1), "validez_cobertura_pct": round(100 * c, 1),
                "validez_f1_pct": round(100 * 2 * p * c / (p + c), 1),
                "roc_auc_prueba": m["roc_auc_prueba"], "pr_auc_prueba": m["pr_auc_prueba"],
                "veces_mejor_que_azar": round(m["pr_auc_prueba"] / m["pr_auc_al_azar"], 2),
                "es_la_configurada": "Sí" if (cuantil, columnas) == actual else "No"})
    return pd.DataFrame(filas)
