"""Auditoría independiente: compara Gold contra los archivos ORIGINALES (Bronce), no contra Silver."""
import re, sys, glob, random
from pathlib import Path
import pandas as pd, pymupdf, openpyxl, yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from pdd.comun import cargar_config
cfg = cargar_config()
L = lambda n: pd.read_csv(REPO / f"data/gold/{n}.csv", sep="|", decimal=",", encoding="utf-8-sig",
                          dtype={"meta_producto_codigo": str, "entidad_codigo": str, "indicador_codigo": str}, converters={"texto": str, "frase_evidencia": str})
meta, act, frag, bar = L("gold_meta_corte"), L("gold_actividad_corte"), L("gold_narrativa_fragmento"), L("gold_barrera_fragmento")
ok = lambda nombre, cond, det="": print(("OK   " if cond else "FALLA") + " | " + nombre + (" | " + str(det) if det != "" else ""))

# 1. Dinero y filas contra el Excel original de Gestión-Inversión del último corte
CRUDOS = Path(cfg["rutas"]["silver"]).parent / "raw"      # carpeta de originales del scraper
ULTIMO = pd.to_datetime(act.fecha_corte, dayfirst=True).max()
U, CARPETA = ULTIMO.strftime("%d/%m/%Y"), ULTIMO.strftime("%Y/%Y-%m-%d")
IV = {v: k for k, v in cfg["plan"]["vigencias"].items()}[ULTIMO.year]      # bloque VIG del año del corte
raw = glob.glob(str(CRUDOS / f"gestion_inversion/{CARPETA}/*.xlsx"))[0]
ws = openpyxl.load_workbook(raw, read_only=True, data_only=True)["datos"]
filas = ws.iter_rows(values_only=True); cab = [str(c).upper() for c in next(filas)]
df = pd.DataFrame(filas, columns=cab); df = df[df["PLAN_CODIGO"].astype(str).str.strip().isin(["17", "17.0"])]
u = act[act.fecha_corte == U]
ok("Excel original del último corte: número de actividades", len(df) == len(u), f"{len(df)} vs {len(u)}")
for col_raw, col_gold in [(f"PROYECTO_ACTIVIDAD_RECVIG{IV}_PROGRAMADO", "recursos_programados"),
                          (f"PROYECTO_ACTIVIDAD_RECVIG{IV}_COMPROMISOS_CONTRATADO", "recursos_comprometidos"),
                          (f"PROYECTO_ACTIVIDAD_RECVIG{IV}_GIROS", "recursos_girados"),
                          (f"PROYECTO_ACTIVIDAD_MAGVIG{IV}_ENTREGADO", "fisico_entregado")]:
    a, b = pd.to_numeric(df[col_raw], errors="coerce").sum(), u[col_gold].sum()
    ok(f"Excel original del último corte: suma de {col_gold}", abs(a - b) < 0.01, f"{a:,.2f} vs {b:,.2f}")

# 2. Avance oficial contra el Excel original de Avance del Plan (último corte)
rawa = glob.glob(str(CRUDOS / f"avance_plan/{CARPETA}/*.xlsx"))[0]
wb = openpyxl.load_workbook(rawa, read_only=True, data_only=True)
hoja = next(n for n in wb.sheetnames if "meta" in n.lower() and "dic" not in n.lower())
it = wb[hoja].iter_rows(values_only=True); cab = [str(c).upper() for c in next(it)]
da = pd.DataFrame(it, columns=cab)
cod = next(c for c in cab if "META_PRODUCTO_CODIGO" in c)
da[cod] = da[cod].astype(str).str.replace(r"\.0$", "", regex=True)
g = meta[meta.fecha_corte == U].set_index("meta_producto_codigo")
v = pd.to_numeric(da.set_index(cod)["AVANCE_VIGENCIA"], errors="coerce")
escala = 100 if v.max() <= 20 else 1
dif = (v * escala - g["avance_vigencia"]).abs()
ok(f"Excel original del último corte (hoja {hoja}): avance_vigencia de las 425 metas", dif.max() < 0.011 and dif.notna().sum() == 425,
   f"diferencia máxima {dif.max():.4f}, metas comparadas {dif.notna().sum()}")

print("relatos cuyo texto se leería como vacío con opciones por defecto:", int(frag.texto.str.strip().str.upper().isin(["NA","N/A","NAN","NULL","NONE","#N/A"]).sum()))
# 3. Relatos contra el texto plano del PDF (lectura distinta a la del extractor)
random.seed(11)
pdfs = {}
for carpeta in cfg["rutas"]["pdf_narrativas"]:
    for p in Path(carpeta).rglob("*.pdf"):
        pdfs[p.name] = p
norm = lambda s: re.sub(r"\W+", "", s.lower())
muestra = frag.sample(60, random_state=11); bien = 0
for _, r in muestra.iterrows():
    with pymupdf.open(pdfs[r.archivo_fuente]) as d:
        pagina = norm(d[int(r.pagina_inicio) - 1].get_text())
    bien += norm(r.texto.split("\n")[0][:60]) in pagina
ok("PDF: 60 relatos al azar aparecen en la página indicada", bien == 60, f"{bien}/60")

# 4. Coherencia interna
ok("Banderas de barrera solo valen 0/1 o vacío", all(meta[c].dropna().isin([0, 1]).all() for c in meta.columns if c.startswith("barrera_")))
ok("Sin narrativa => banderas vacías (no cero)", meta.loc[~meta.corte_con_narrativa, "n_barreras_distintas"].isna().all())
b = bar[bar.es_barrera].groupby(["fecha_corte", "meta_producto_codigo"])["categoria"].nunique()
m2 = meta.set_index(["fecha_corte", "meta_producto_codigo"])["n_barreras_distintas"]
ok("n_barreras_distintas coincide con gold_barrera_fragmento", (m2.reindex(b.index) == b).all() and (m2.fillna(0) > 0).sum() == len(b))
est = frag[frag.campo == "retrasos_y_soluciones"]
ok("Todo relato de retrasos tiene estado", est.estado_retraso.notna().all(), est.estado_retraso.value_counts().to_dict())
ok("'Barrera identificada' <=> tiene alguna barrera", ((est.estado_retraso == "Barrera identificada") == (est.n_barreras > 0)).all())
ok("Evidencia: cada frase está dentro de su relato", all(norm(f) in norm(t) for f, t in
   zip(bar.frase_evidencia, bar.merge(frag[["fragmento_id", "texto"]], on="fragmento_id").texto)))
s = meta.sort_values(["meta_producto_codigo", "fecha_corte"], key=lambda c: pd.to_datetime(c, dayfirst=True) if c.name == "fecha_corte" else c)
sig = s.groupby("meta_producto_codigo")["avance_vigencia"].shift(-1)
ok("avance_vigencia_siguiente = avance del corte posterior", ((s.avance_vigencia_siguiente - sig).abs().fillna(0) < 1e-9).all())
esp = pd.to_datetime(s.fecha_corte_siguiente, dayfirst=True).dt.month / 12 * 100
calc = (s.avance_vigencia_siguiente < 0.70 * esp).astype(float).where(s.fecha_corte_siguiente.notna())
ok("riesgo_lineal_siguiente reproduce la regla del 70 %", (calc.fillna(-1) == s.riesgo_lineal_siguiente.fillna(-1)).all())
rez = s.groupby("meta_producto_codigo")["en_rezago_actual"].shift(-1)
ok("riesgo_relativo_siguiente = rezago del corte posterior", (rez.fillna(-1) == s.riesgo_relativo_siguiente.fillna(-1)).all())
ok("riesgo relativo marca cerca del 25 % en todos los cortes", s.groupby("fecha_corte").riesgo_relativo_siguiente.mean().dropna().between(0.2, 0.3).all())
variables_modelo = set(pd.read_csv(REPO / "data/gold/gold_modelo_importancia.csv", sep="|", decimal=",", encoding="utf-8-sig").variable)
ok("Ninguna variable del modelo contiene información posterior", not any(v.endswith("_siguiente") or v.startswith("riesgo_") for v in variables_modelo), len(variables_modelo))
pred = [c for c in meta.columns if not c.endswith("_siguiente")]
futuras = [c for c in meta.columns if c.endswith("_siguiente") or c == "riesgo_cierre_anio"]
ok("Solo 5 columnas contienen información posterior", len(futuras) == 5, futuras)


# 5. Documentación frente a tablas
guia = (REPO / "docs/GUIA_GOLD_Y_NLP.md").read_text(encoding="utf-8"); inf = (REPO / "docs/AUDITORIA.md").read_text(encoding="utf-8")
res = L("gold_auditoria_nlp_resumen"); p = res[(res.conjunto == "prueba") & res.ponderado.str.startswith("Sí")]
for txt, nombre in [(guia, "guía"), (inf, "informe")]:
    for val in [f"{x:.1f}".replace(".", ",") for x in list(p.precision_pct) + list(p.sensibilidad_pct)]:
        ok(f"{nombre}: cita {val} %", val in txt)
n = meta[meta.corte_con_narrativa & meta.tiene_datos_financieros]
for k, val in n.estado_narrativa.value_counts().items():
    if k != "Sin relato para la meta": ok(f"guía: {k} = {val}", f"| {k} | {val} |" in guia)
for t, filas_ in [("gold_barrera_fragmento", len(bar)), ("gold_narrativa_fragmento", len(frag)), ("gold_diccionario", len(L("gold_diccionario")))]:
    ok(f"guía: filas de {t}", f"{filas_:,}".replace(",", ".") in guia, filas_)

# 6. Estado del repositorio
readme = (REPO / "README.md").read_text(encoding="utf-8")
ok("README describe el proyecto PDD", "PDD" in readme or "Plan Distrital" in readme)
ok("pruebas automáticas (tests/) con contenido", any(f.stat().st_size > 0 for f in (REPO / "tests").glob("test_*.py")))
ok("rutas de configs/pdd.yaml no son absolutas de un equipo", "C:/Users" not in (REPO / "configs/pdd.yaml").read_text(encoding="utf-8"))
lock = (REPO / "poetry.lock").read_text(encoding="utf-8").lower()
ok("poetry.lock incluye pymupdf y openpyxl", "pymupdf" in lock and "openpyxl" in lock)
ok("el repositorio no contiene el ejercicio bancario ni los servicios de MLOps", not any((REPO / c).exists() for c in ["legado_churn", "services", "data/Customer-Churn-Records.csv"]))
