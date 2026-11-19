"""Genera el tablero tablero/index.html a partir de las tablas Gold.

Uso, desde la raíz del repositorio:
    python scripts/generar_tablero.py              # escribe tablero/index.html
    python scripts/generar_tablero.py OTRA_RUTA    # escribe el tablero en otra ruta (lo usa reproducir.py)

El resultado es un solo archivo que se abre con doble clic: lleva dentro los datos y el programa.
El diseño definitivo (tablero/plantilla_foco.html) es una aplicación ya compilada; el script solo le
inyecta los datos Gold, comprimidos con gzip y en base64, en el bloque <script id="foco-pdd-payload">.
La plantilla sale de tablero/plantilla_foco_base.html (diseño original, sin datos) con los ajustes del
equipo aplicados por scripts/construir_plantilla.py (scripts/ajustar_*.py, en orden).

Las entidades se muestran con su nombre normalizado (entidad_nombre_sigla, de Normalizacion_Entidades.xlsx).
Todo sale de Gold: el avance de cada actividad año por año del Plan (gráfica emergente de Actividades)
y los compromisos en vigencias futuras son columnas de gold_actividad_corte.

Regla de alerta del tablero: en el último corte, una meta sin recursos comprometidos en el año
(0 % o sin dato) y sin compromisos en vigencias futuras no lleva alerta ni puntaje de riesgo; se marca
«sc» y el tablero la muestra como «Sin alerta · sin compromiso». Gold no cambia.
"""
import base64
import gzip
import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
GOLD, TABLERO = RAIZ / "data" / "gold", RAIZ / "tablero"
RECORTE_AVANCES = 1500      # los relatos de avances son largos; el texto completo está en Gold
VIGENCIAS_PLAN = [2024, 2025, 2026, 2027]   # años del Plan (columnas fisico_*_<año> de gold_actividad_corte)
FIABLES = ["contratacion", "tramites_y_permisos", "talento_y_capacidad", "demanda_y_poblacion", "factores_externos"]


def leer(nombre: str) -> pd.DataFrame:
    texto = {c: str for c in ["texto", "frase_evidencia", "meta_producto_codigo", "entidad_codigo", "indicador_codigo",
                              "proyecto_codigo", "proyecto_actividad_codigo"]}
    t = pd.read_csv(GOLD / f"{nombre}.csv", sep="|", decimal=",", encoding="utf-8-sig", converters=texto, low_memory=False)
    if "fecha_corte" in t:
        t["corte"] = pd.to_datetime(t["fecha_corte"], dayfirst=True).dt.strftime("%Y-%m-%d")
    return t


def num(v, dec=2):
    return None if pd.isna(v) else round(float(v), dec)


def descargas_por_corte() -> dict:
    """Archivos originales de la SDP disponibles en el repositorio, por corte (data/FUENTES.csv).

    Tipos: «informe» (PDF por entidad, de Gestión-Inversión), «avance» (Excel de Avance del Plan) y
    «gestion» (Excel de Gestión-Inversión). El tablero los enlaza con una ruta relativa a data/raw
    (funciona al abrir tablero/index.html dentro del repositorio) y, si existe, con la URL oficial."""
    import re
    fuentes = pd.read_csv(RAIZ / "data" / "FUENTES.csv", sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    salida = {}
    for f in fuentes.itertuples():
        m = re.fullmatch(r"data/raw/(avance_plan|gestion_inversion)/\d{4}/(\d{4}-\d{2}-\d{2})/([^/]+)", f.archivo)
        if not m or not (RAIZ / f.archivo).exists():
            continue
        fuente, corte, nombre = m.groups()
        tipo = "avance" if fuente == "avance_plan" else "informe" if nombre.lower().endswith(".pdf") else "gestion"
        salida.setdefault(corte, []).append({"t": tipo, "n": nombre, "r": "../" + f.archivo,
                                             "u": f.url_origen or None, "b": int(f.bytes)})
    return salida


def compromisos_vigencias_futuras(act: pd.DataFrame, corte: str) -> dict:
    """Recursos ya comprometidos para años posteriores al del corte (vigencias futuras), por meta.
    Columna recursos_comprometidos_vigencias_futuras de gold_actividad_corte."""
    vigentes = act[(act["corte"] == corte) & ~act["fila_rezagada"]]
    return vigentes.groupby("meta_producto_codigo")["recursos_comprometidos_vigencias_futuras"].sum().to_dict()


def serie_por_vigencia(r) -> list:
    """Avance físico de una actividad año por año del Plan, como lo reporta el corte (columnas
    fisico_*_<año> de gold_actividad_corte) y el total del cuatrienio: es la tabla «Año / Programación /
    Ejecución / Avance de la vigencia» de los reportes de la SDP. Lista plana: [programado, entregado,
    % de cada año …, programado total, entregado total, % total]."""
    valores = [getattr(r, f"{campo}_{anio}") for anio in VIGENCIAS_PLAN
               for campo in ["fisico_programado", "fisico_entregado", "pct_fisico_entregado"]]
    valores += [r.fisico_total_programado, r.fisico_total_entregado, r.pct_fisico_total_entregado]
    return [num(v) for v in valores]


def sin_compromiso(pct_compromisos, futuro: float) -> bool:
    """Regla del tablero: una meta que no comprometió recursos en el año (0 % o sin dato) y tampoco
    tiene compromisos en vigencias futuras no se marca con alerta: no hay nada comprometido que vigilar."""
    return (pd.isna(pct_compromisos) or float(pct_compromisos) == 0) and not futuro > 0


def construir_datos() -> dict:
    meta, act = leer("gold_meta_corte"), leer("gold_actividad_corte")
    frag, bar = leer("gold_narrativa_fragmento"), leer("gold_barrera_fragmento")
    pred, cat = leer("gold_prediccion_riesgo"), leer("gold_catalogo_barreras")
    aud = leer("gold_auditoria_nlp_resumen")
    pred = pred[pred["objetivo"] == "riesgo_relativo_siguiente"].set_index("meta_producto_codigo")
    cortes = sorted(meta["corte"].unique(), reverse=True)
    ultimo = cortes[0]
    barreras = [c for c in meta.columns if c.startswith("barrera_")]
    futuras = compromisos_vigencias_futuras(act, ultimo)

    metas_por_corte = {}
    for corte, g in meta.groupby("corte"):
        filas = []
        for r in g.itertuples():
            p = pred.loc[r.meta_producto_codigo] if corte == ultimo and r.meta_producto_codigo in pred.index else None
            sc = p is not None and sin_compromiso(r.pct_compromisos, futuras.get(r.meta_producto_codigo, 0))
            if sc:
                p = None        # sin alerta ni puntaje de riesgo: «sc» explica por qué en el tablero
            filas.append({
                "i": r.meta_producto_codigo, "av": num(r.avance_vigencia), "at": num(r.avance_transcurrido),
                "ap": num(r.avance_plan), "pc": num(r.pct_compromisos), "pg": num(r.pct_giros),
                "ef": num(r.eficiencia_dea, 3), "br": num(r.brecha_fisico_financiera),
                "na": num(r.n_actividades_programadas, 0), "nz": num(r.n_actividades_entrega_cero, 0),
                "rp": num(r.recursos_programados, 1), "rz": num(r.en_rezago_actual, 0), "es": r.estado_narrativa,
                "ba": [c[8:] for c in barreras if getattr(r, c) == 1],
                "sp": None if pd.isna(r.sector_principal) else r.sector_principal,
                "ti": None if pd.isna(r.tipo_anualizacion_predominante) else r.tipo_anualizacion_predominante,
                "gd": None if pd.isna(r.grupo_dea) else r.grupo_dea,
                "pr": None if p is None else num(p.probabilidad_riesgo, 3), "nv": None if p is None else p.nivel_alerta,
                "ex": None if p is None else p.explicacion, **({"sc": 1} if sc else {})})
        metas_por_corte[corte] = filas

    actividades = {}
    for corte, g in act[~act["fila_rezagada"]].groupby("corte"):
        actividades[corte] = [[r.meta_producto_codigo, r.sector_nombre, r.entidad_nombre_sigla, r.proyecto_actividad_nombre,
                               r.tipo_anualizacion, num(r.fisico_programado), num(r.fisico_entregado),
                               num(r.pct_fisico_entregado), num(r.recursos_programados, 1),
                               num(r.recursos_comprometidos, 1), num(r.recursos_girados, 1),
                               serie_por_vigencia(r)]
                              for r in g.itertuples()]

    evidencia = {k: g[["categoria", "frase_evidencia"]].values.tolist() for k, g in bar.groupby("fragmento_id")}
    avances = frag[frag["campo"] == "avances_y_logros"].set_index(
        ["corte", "entidad_codigo", "meta_producto_codigo", "indicador_codigo"])["texto"].to_dict()
    relatos = {}
    for r in frag[frag["campo"] == "retrasos_y_soluciones"].itertuples():
        av = avances.get((r.corte, r.entidad_codigo, r.meta_producto_codigo, r.indicador_codigo), "")
        relatos.setdefault(r.corte, {}).setdefault(r.meta_producto_codigo, []).append({
            "e": r.entidad_nombre if pd.isna(r.entidad_nombre_sigla) else r.entidad_nombre_sigla, "in": r.indicador_nombre, "es": r.estado_retraso,
            "ev": evidencia.get(r.fragmento_id, []), "r": r.texto, "pg": int(r.pagina_inicio), "f": r.archivo_fuente,
            "a": av[:RECORTE_AVANCES] + (" […]" if len(av) > RECORTE_AVANCES else "")})

    prueba = aud[(aud["conjunto"] == "prueba") & aud["ponderado"].str.startswith("Sí")]
    return {
        "cortes": cortes, "ultimo": ultimo, "vigencias": VIGENCIAS_PLAN, "descargas": descargas_por_corte(),
        "nombres": meta.drop_duplicates("meta_producto_codigo").set_index("meta_producto_codigo")["meta_producto_nombre"].to_dict(),
        "categorias": {r.categoria: {"n": r.categoria_nombre, "fiable": r.categoria in FIABLES}
                       for r in cat.itertuples() if r.es_barrera},
        "metas": metas_por_corte, "actividades": actividades, "relatos": relatos,
        "acierto": {"problema": float(prueba["precision_pct"].iloc[0]), "categoria": float(prueba["precision_pct"].iloc[1])},
    }


def generar_foco(destino: Path) -> None:
    """Tablero con el diseño definitivo: la plantilla compilada recibe los datos Gold comprimidos."""
    crudo = json.dumps(construir_datos(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    carga = base64.b64encode(gzip.compress(crudo, mtime=0)).decode("ascii")
    html = (TABLERO / "plantilla_foco.html").read_text(encoding="utf-8")
    assert html.count("/*DATOS_GZIP*/") == 1, "plantilla_foco.html debe tener una sola marca /*DATOS_GZIP*/"
    html = html.replace("/*DATOS_GZIP*/", carga)
    destino.write_text(html, encoding="utf-8", newline="\n")
    print(f"Tablero generado: {destino} ({len(html) / 1e6:.1f} MB)")


if __name__ == "__main__":
    generar_foco(Path(sys.argv[1]) if len(sys.argv) > 1 else TABLERO / "index.html")
