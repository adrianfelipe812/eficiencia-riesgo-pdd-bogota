"""Construye las tablas Gold con todos los cortes trimestrales de Silver y su narrativa.

Tablas:
  gold_meta_corte             una fila por meta producto y corte (panel para DEA y para el modelo)
  gold_actividad_corte        una fila por actividad y corte (lo físico y lo financiero del año en curso)
  gold_narrativa_fragmento    cada relato extraído de los PDF, con su clasificación
  gold_barrera_fragmento      cada barrera encontrada en un relato, con la frase que la sustenta
  gold_catalogo_barreras      qué significa cada categoría de barrera
  gold_diccionario            qué significa cada columna
  gold_control_calidad        comprobaciones hechas al construir las tablas
  gold_auditoria_extraccion   por cada PDF: rótulos encontrados, relatos obtenidos y celdas vacías
  gold_auditoria_nlp_resumen  precisión y sensibilidad del clasificador de barreras
  gold_auditoria_nlp          relatos leídos por una persona, comparados uno a uno con el clasificador
"""
import pandas as pd

from pdd.auditoria import evaluar_clasificador
from pdd.barreras import ORDEN_ESTADOS, catalogo_barreras, clasificar_fragmentos
from pdd.comun import a_fecha, a_numero, guardar_csv, leer_silver, razon, ruta_gold
from pdd.dea import calcular_dea
from pdd.diccionario import DICCIONARIO
from pdd.modelo import (agregar_objetivos, asociacion_barreras_eficiencia, comparar_definiciones_riesgo,
                        entrenar_y_evaluar)
from pdd.narrativas import extraer_narrativas

ID_ACTIVIDAD = ["entidad_codigo", "proyecto_codigo", "proyecto_actividad_codigo"]
CLAVE_META = ["fecha_corte", "meta_producto_codigo"]
CONTEXTO = ["sector_codigo", "sector_nombre", "entidad_codigo", "entidad_sigla", "entidad_nombre",
            "objetivo_codigo", "programa_codigo", "meta_producto_codigo",
            "proyecto_codigo", "proyecto_nombre", "proyecto_actividad_codigo", "proyecto_actividad_nombre"]


def _valor_de_la_vigencia(gi: pd.DataFrame, plantilla: str) -> pd.Series:
    """Gestión-Inversión trae un bloque de columnas por año (VIG1..VIG4). Para cada
    fila toma el bloque que corresponde al año que se está reportando."""
    salida = pd.Series(pd.NA, index=gi.index, dtype="Float64")
    for indice in sorted(gi["indice_vigencia"].unique()):
        filas = gi["indice_vigencia"] == indice
        salida[filas] = a_numero(gi.loc[filas, plantilla.format(i=indice)])
    return salida


def tabla_actividad_corte(config: dict) -> pd.DataFrame:
    gi = leer_silver(config, "gestion_inversion/gestion_inversion.csv")
    anio_a_indice = {anio: i for i, anio in config["plan"]["vigencias"].items()}
    gi["vigencia"] = gi["vigencia"].astype(int)
    gi["indice_vigencia"] = gi["vigencia"].map(anio_a_indice)

    p = "proyecto_actividad_"
    t = gi[CONTEXTO].copy()
    t.insert(0, "fecha_corte", a_fecha(gi["fecha_corte"]))
    t.insert(1, "vigencia", gi["vigencia"])
    t["tipo_anualizacion"] = gi[p + "tipo_anualizacion"].str.strip()
    # Una fila es "rezagada" cuando el archivo de un corte trae el seguimiento de un año anterior.
    t["fila_rezagada"] = t["vigencia"] != t["fecha_corte"].dt.year

    t["fisico_programado"] = _valor_de_la_vigencia(gi, p + "magvig{i}_programado")
    t["fisico_entregado"] = _valor_de_la_vigencia(gi, p + "magvig{i}_entregado")
    t["pct_fisico_entregado"] = _valor_de_la_vigencia(gi, p + "magvig{i}_porcentregado").round(2)
    t["recursos_programados"] = _valor_de_la_vigencia(gi, p + "recvig{i}_programado")
    t["recursos_comprometidos"] = _valor_de_la_vigencia(gi, p + "recvig{i}_compromisos_contratado")
    t["recursos_girados"] = _valor_de_la_vigencia(gi, p + "recvig{i}_giros")
    t["pct_compromisos"] = razon(t["recursos_comprometidos"], t["recursos_programados"])
    t["pct_giros"] = razon(t["recursos_girados"], t["recursos_programados"])

    t["fisico_total_programado"] = a_numero(gi[p + "magtotal_programado"])
    t["fisico_total_entregado"] = a_numero(gi[p + "magtotal_entregado"])
    t["pct_fisico_total_entregado"] = a_numero(gi[p + "magtotal_porcentregado"]).round(2)
    t["recursos_total_programados_constantes"] = a_numero(gi[p + "recktotal_programado"])
    t["recursos_total_girados_constantes"] = a_numero(gi[p + "recktotal_giros"])

    t["entrega_cero_con_programacion"] = (t["fisico_programado"] > 0) & (t["fisico_entregado"] == 0)
    return t.sort_values(["fecha_corte", *ID_ACTIVIDAD]).reset_index(drop=True)


def _resumen_actividades(act: pd.DataFrame) -> pd.DataFrame:
    """Lleva las actividades al nivel de meta y corte, sin repetir dinero."""
    vigentes = act[~act["fila_rezagada"]]
    resumen = vigentes.groupby(CLAVE_META).agg(
        n_actividades=("proyecto_actividad_codigo", "size"),
        n_entidades=("entidad_codigo", "nunique"),
        n_actividades_programadas=("fisico_programado", lambda s: int((s > 0).sum())),
        n_actividades_entrega_cero=("entrega_cero_con_programacion", "sum"),
        recursos_programados=("recursos_programados", "sum"),
        recursos_comprometidos=("recursos_comprometidos", "sum"),
        recursos_girados=("recursos_girados", "sum"),
        tipo_anualizacion_predominante=("tipo_anualizacion", lambda s: s.mode().iat[0]),
    ).reset_index()
    # Sector y entidad "principal": los que concentran más recursos programados de la meta.
    principal = (vigentes.groupby([*CLAVE_META, "sector_nombre", "entidad_sigla"], as_index=False)
                 ["recursos_programados"].sum()
                 .sort_values("recursos_programados", ascending=False).drop_duplicates(CLAVE_META)
                 .rename(columns={"sector_nombre": "sector_principal", "entidad_sigla": "entidad_principal"})
                 .drop(columns="recursos_programados"))
    resumen = resumen.merge(principal, on=CLAVE_META, how="left")
    resumen["pct_compromisos"] = razon(resumen["recursos_comprometidos"], resumen["recursos_programados"])
    resumen["pct_giros"] = razon(resumen["recursos_girados"], resumen["recursos_programados"])
    resumen["pct_actividades_entrega_cero"] = razon(
        resumen["n_actividades_entrega_cero"], resumen["n_actividades_programadas"])
    return resumen


def _resumen_narrativa(fragmentos: pd.DataFrame, barreras: pd.DataFrame) -> pd.DataFrame:
    """Resume los relatos de retrasos de cada meta y corte. Si varias entidades
    reportan la misma meta, prevalece el estado más delicado."""
    retrasos = fragmentos[fragmentos["campo"] == "retrasos_y_soluciones"].copy()
    retrasos["rango"] = retrasos["estado_retraso"].map(ORDEN_ESTADOS.index)
    resumen = retrasos.groupby(CLAVE_META).agg(
        n_relatos_retraso=("fragmento_id", "size"),
        rango=("rango", "max"),
        menciona_dificultad=("menciona_dificultad", "max"),
    ).reset_index()
    resumen["estado_narrativa"] = resumen.pop("rango").map(lambda r: ORDEN_ESTADOS[r])

    solo_barreras = barreras[barreras["es_barrera"]]
    conteo = solo_barreras.groupby(CLAVE_META)["categoria"].nunique().rename("n_barreras_distintas")
    banderas = (solo_barreras.assign(v=1).pivot_table(index=CLAVE_META, columns="categoria", values="v",
                                                      aggfunc="max", fill_value=0).add_prefix("barrera_"))
    todas = [f"barrera_{c}" for c in catalogo_barreras().query("es_barrera")["categoria"]]
    banderas = banderas.reindex(columns=todas, fill_value=0)
    resumen = resumen.merge(conteo, on=CLAVE_META, how="left").merge(banderas, on=CLAVE_META, how="left")
    columnas = ["n_barreras_distintas", *todas]
    resumen[columnas] = resumen[columnas].fillna(0).astype(int)     # con relato y sin barrera = 0
    return resumen


def tabla_meta_corte(config: dict, act: pd.DataFrame, fragmentos: pd.DataFrame,
                     barreras: pd.DataFrame) -> pd.DataFrame:
    mp = leer_silver(config, "avance_plan/meta_producto.csv")
    t = mp[["objetivo_codigo", "objetivo_nombre", "programa_codigo", "programa_nombre",
            "meta_producto_codigo", "meta_producto_nombre"]].copy()
    t.insert(0, "fecha_corte", a_fecha(mp["fecha_corte"]))
    t.insert(1, "vigencia", t["fecha_corte"].dt.year)
    for columna in ["avance_vigencia", "avance_transcurrido", "avance_plan"]:
        t[columna] = a_numero(mp[columna])

    t = t.merge(_resumen_actividades(act), on=CLAVE_META, how="left")
    t["tiene_datos_financieros"] = t["n_actividades"].notna()

    # Lectura conjunta físico-financiera.
    t["avance_esperado_lineal"] = (100 * t["fecha_corte"].dt.month / 12).round(2)
    t["brecha_fisico_financiera"] = (t["pct_compromisos"] - t["avance_vigencia"]).round(2)

    # Narrativa: solo existe para los cortes con PDF por entidad.
    cortes_con_pdf = set(fragmentos["fecha_corte"])
    t = t.merge(_resumen_narrativa(fragmentos, barreras), on=CLAVE_META, how="left")
    t["corte_con_narrativa"] = t["fecha_corte"].isin(cortes_con_pdf)
    t["estado_narrativa"] = t["estado_narrativa"].fillna(
        t["corte_con_narrativa"].map({True: "Sin relato para la meta", False: "Corte sin PDF narrativo"}))

    return t.sort_values(CLAVE_META).reset_index(drop=True)


def control_calidad(config: dict, act: pd.DataFrame, meta: pd.DataFrame, fragmentos: pd.DataFrame,
                    extraccion: pd.DataFrame) -> pd.DataFrame:
    """Comprobaciones que deben cumplirse para confiar en las tablas. Cada una compara
    Gold contra una fuente independiente (Silver o el propio PDF)."""
    gi = leer_silver(config, "gestion_inversion/gestion_inversion.csv")
    mp = leer_silver(config, "avance_plan/meta_producto.csv")
    ind = leer_silver(config, "avance_plan/indicador.csv")
    vigentes = act[~act["fila_rezagada"]]

    pares_gi = set(zip(gi["entidad_codigo"], gi["meta_producto_codigo"]))
    entidad_ok = [par in pares_gi for par in zip(fragmentos["entidad_codigo"], fragmentos["meta_producto_codigo"])]
    pares_ind = set(zip(a_fecha(ind["fecha_corte"]), ind["meta_producto_codigo"], ind["indicador_codigo"]))
    indicador_ok = [trio in pares_ind for trio in zip(fragmentos["fecha_corte"], fragmentos["meta_producto_codigo"],
                                                      fragmentos["indicador_codigo"])]
    # El corte siguiente debe ser siempre posterior y de la misma meta.
    orden_ok = (meta["fecha_corte_siguiente"].isna() | (meta["fecha_corte_siguiente"] > meta["fecha_corte"])).all()
    ultimo = meta["fecha_corte"].max()
    futuro_en_ultimo = int(meta.loc[meta["fecha_corte"] == ultimo, "riesgo_relativo_siguiente"].notna().sum())

    pruebas = [
        ("Actividades: mismas filas que Silver", len(gi), len(act)),
        ("Actividades: sin duplicados por actividad y corte", 0,
         int(act.duplicated(["fecha_corte", "vigencia", *ID_ACTIVIDAD]).sum())),
        ("Metas: mismas filas que Silver (meta x corte)", len(mp), len(meta)),
        ("Metas: sin duplicados por meta y corte", 0, int(meta.duplicated(CLAVE_META).sum())),
        ("Metas: cada corte tiene las 425 metas producto", 425, int(meta.groupby("fecha_corte").size().min())),
        ("Dinero: recursos programados no cambian al agregar (millones)",
         round(float(vigentes["recursos_programados"].sum()), 2), round(float(meta["recursos_programados"].sum()), 2)),
        ("Dinero: giros no cambian al agregar (millones)",
         round(float(vigentes["recursos_girados"].sum()), 2), round(float(meta["recursos_girados"].sum()), 2)),
        ("Avance oficial: idéntico al de Silver (suma de avance_vigencia)",
         round(float(a_numero(mp["avance_vigencia"]).sum()), 2), round(float(meta["avance_vigencia"].sum()), 2)),
        ("Narrativa: relatos cuya entidad y meta existen en Gestión-Inversión (%)", 100.0,
         round(100 * sum(entidad_ok) / len(entidad_ok), 2)),
        ("Narrativa: relatos cuyo indicador pertenece a esa meta según Avance del Plan (%)", 100.0,
         round(100 * sum(indicador_ok) / len(indicador_ok), 2)),
        ("Narrativa: rótulos del PDF = relatos con texto + celdas vacías", int(extraccion["rotulos_en_pdf"].sum()),
         int(extraccion["relatos_con_texto"].sum() + extraccion["celdas_vacias"].sum())),
        ("Narrativa: identificadores de relato sin repetir", 0, int(fragmentos["fragmento_id"].duplicated().sum())),
        ("Tiempo: el corte siguiente siempre es posterior", True, bool(orden_ok)),
        ("Tiempo: el último corte no tiene dato del futuro", 0, futuro_en_ultimo),
        ("DEA: toda eficiencia está entre 0 y 1", True,
         bool(meta["eficiencia_dea"].dropna().between(0, 1.0001).all())),
        ("DEA: cada grupo evaluado tiene al menos una meta en la frontera", True,
         bool(meta[meta["eficiencia_dea"].notna()].groupby(["fecha_corte", "grupo_dea"])["en_frontera"].any().all())),
    ]
    tabla = pd.DataFrame(pruebas, columns=["comprobacion", "esperado", "obtenido"])
    tabla["cumple"] = (tabla["esperado"] == tabla["obtenido"]).map({True: "Sí", False: "No"})
    return tabla.astype({"esperado": "string", "obtenido": "string"})


DESCRIPCION_TABLAS = {
    "gold_meta_corte": "Tabla principal. Una fila por meta producto y corte: avance físico oficial, dinero, barreras narradas y lo que pasó en el corte siguiente.",
    "gold_actividad_corte": "Detalle. Una fila por actividad y corte, con lo programado y entregado del año en curso.",
    "gold_narrativa_fragmento": "Cada relato 'Retrasos y soluciones' o 'Avances y Logros' leído del PDF, con su página y su clasificación.",
    "gold_barrera_fragmento": "Cada barrera detectada en un relato, con la frase exacta que la sustenta.",
    "gold_catalogo_barreras": "Definición de cada categoría de barrera y las expresiones que se buscan.",
    "gold_diccionario": "Significado, unidad y origen de cada columna.",
    "gold_control_calidad": "Comprobaciones automáticas: deben decir 'Sí' en la columna 'cumple'.",
    "gold_auditoria_extraccion": "Por cada PDF: cuántos rótulos tenía, cuántos relatos se obtuvieron y cuántas celdas estaban vacías.",
    "gold_auditoria_nlp_resumen": "Acierto del clasificador de barreras: precisión y sensibilidad. La fila que se debe citar es la del conjunto 'prueba', ponderada.",
    "gold_auditoria_nlp": "Los 180 relatos leídos por una persona y comparados uno a uno con el clasificador.",
    "gold_dea_grupo": "Eficiencia DEA resumida por grupo comparable y corte, con la prueba de estabilidad del grupo.",
    "gold_asociacion_barreras": "Objetivo 2: comparación de la eficiencia DEA entre metas que narran un problema y las que no.",
    "gold_modelo_particion": "Qué cortes se usaron para entrenar, elegir y probar el modelo predictivo.",
    "gold_modelo_metricas": "Objetivo 3: desempeño del modelo con cada conjunto de variables, frente a la línea base financiera.",
    "gold_modelo_importancia": "Qué variables pesan más en el modelo integrado.",
    "gold_prediccion_riesgo": "Alerta para el corte más reciente: probabilidad de rezago de cada meta en el corte siguiente.",
    "gold_modelo_calibracion": "Confiabilidad de las probabilidades: en cada décimo de metas, la probabilidad media frente a la proporción que de verdad se rezagó.",
    "gold_modelo_costos": "Qué pasaría con otras razones de costo entre omitir un rezago y dar una falsa alarma.",
    "gold_modelo_explicacion": "Para cada meta del último corte, las cinco variables que más suben o bajan su riesgo (SHAP).",
    "gold_comparacion_riesgo": "Nueve variantes de la definición de rezago, comparadas por validez y por capacidad de anticipación.",
}


def construir_gold(config: dict, silencioso: bool = False) -> dict[str, pd.DataFrame]:
    if silencioso:                      # misma construcción, sin mensajes de avance
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            return construir_gold(config)
    print("1/5 Leyendo los relatos de los PDF por entidad...")
    crudos, extraccion = extraer_narrativas(config)
    fragmentos, barreras = clasificar_fragmentos(crudos)
    print("2/5 Preparando actividades y metas...")
    act = tabla_actividad_corte(config)
    meta = tabla_meta_corte(config, act, fragmentos, barreras)
    print("    Estimando eficiencia DEA por grupos comparables...")
    puntajes, dea_grupo = calcular_dea(meta, config)
    meta = meta.merge(puntajes.drop(columns=["metas_en_grupo", "eficiencia_dea_con_giros"]), on=CLAVE_META, how="left")
    # El anteproyecto pide no concluir con fronteras inestables: en esos grupos el puntaje
    # se deja vacío en la tabla principal (el detalle sigue en gold_dea_grupo).
    inestable = meta["grupo_estable"] == False  # noqa: E712
    meta.loc[inestable, ["eficiencia_dea", "brecha_eficiencia", "en_frontera", "holgura_insumo_pct"]] = pd.NA
    meta = agregar_objetivos(meta, config)
    print("    Entrenando y evaluando el modelo predictivo...")
    modelo = entrenar_y_evaluar(meta, config)
    print("3/5 Auditando...")
    auditoria_detalle, auditoria_resumen = evaluar_clasificador(fragmentos, barreras)
    tablas = {
        "gold_meta_corte": meta,
        "gold_actividad_corte": act,
        "gold_narrativa_fragmento": fragmentos,
        "gold_barrera_fragmento": barreras,
        "gold_catalogo_barreras": catalogo_barreras(),
        "gold_diccionario": pd.DataFrame(DICCIONARIO, columns=["tabla", "columna", "significado", "unidad", "origen"]),
        "gold_control_calidad": control_calidad(config, act, meta, fragmentos, extraccion),
        "gold_auditoria_extraccion": extraccion,
        "gold_auditoria_nlp_resumen": auditoria_resumen,
        "gold_auditoria_nlp": auditoria_detalle,
        "gold_dea_grupo": dea_grupo,
        "gold_asociacion_barreras": asociacion_barreras_eficiencia(meta),
        **modelo,
        "gold_comparacion_riesgo": comparar_definiciones_riesgo(meta, config),
    }
    documentadas = {(d[0], d[1]) for d in DICCIONARIO}
    sin_documentar = [(n, c) for n in list(tablas)[:4] for c in tablas[n].columns if (n, c) not in documentadas]
    if sin_documentar:
        raise ValueError(f"Columnas sin entrada en el diccionario: {sin_documentar}")

    print("4/5 Guardando CSV...")
    carpeta = ruta_gold(config)
    for viejo in carpeta.glob("gold_*"):          # evita que queden tablas de una versión anterior
        viejo.unlink()
    for nombre, tabla in tablas.items():
        guardar_csv(tabla, carpeta, nombre)
    print("5/5 Guardando el libro de Excel...")
    leame = pd.DataFrame([{"hoja": n.removeprefix("gold_"), "filas": len(t), "contenido": DESCRIPCION_TABLAS[n]}
                          for n, t in tablas.items()])
    with pd.ExcelWriter(carpeta / "gold_pdd.xlsx", engine="openpyxl") as libro:
        leame.to_excel(libro, sheet_name="LEAME", index=False)
        for nombre, tabla in tablas.items():
            hoja = tabla.copy()
            for columna in hoja.select_dtypes(include=["object", "string"]).columns:
                # Una celda de Excel admite hasta 32.767 caracteres; el CSV conserva el texto completo.
                hoja[columna] = hoja[columna].map(lambda v: v[:32000] if isinstance(v, str) else v)
            hoja.to_excel(libro, sheet_name=nombre.removeprefix("gold_")[:31], index=False)
    print(f"Listo: {carpeta}")
    return tablas
