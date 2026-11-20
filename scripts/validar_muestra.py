"""Valida una muestra de metas y actividades del tablero contra los Excel originales de la SDP.

Uso, desde la raíz del repositorio:
    python scripts/validar_muestra.py                          # 25 metas y 25 actividades
    python scripts/validar_muestra.py --metas 50 --actividades 100 --semilla 7

Toma los datos que lleva dentro tablero/index.html (lo mismo que ve el usuario) para el último corte y
los compara con los archivos originales de ese corte en data/raw, sin pasar por Silver ni Gold:

  - Avance del Plan (hoja «MetaProducto»): avance de vigencia, transcurrido y cuatrienio de cada meta.
  - Gestión-Inversión (hoja «datos»): cada actividad, y las sumas por meta con las que se calculan
    % comprometido, % girado, recursos programados y actividades sin entrega.
  - Normalizacion_Entidades.xlsx: el nombre de entidad que muestra el tablero.

Por meta revisa 9 datos; por actividad, 26 (incluidos los 15 de la gráfica de avance por año). Además
recalcula, con todas las metas, los tres promedios de las tarjetas del Panorama. La muestra es al azar
con semilla fija, así que se puede repetir. Termina con código 1 si encuentra alguna diferencia.
"""
import argparse
import base64
import gzip
import json
import random
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
P = "PROYECTO_ACTIVIDAD_"
TOL_PCT, TOL_MILLONES = 0.011, 0.06      # el tablero redondea porcentajes a 2 decimales y millones a 1


def datos_del_tablero() -> dict:
    html = (RAIZ / "tablero" / "index.html").read_text(encoding="utf-8")
    carga = re.search(r'foco-pdd-payload" type="text/plain">(.*?)</script>', html, re.S).group(1)
    return json.loads(gzip.decompress(base64.b64decode(carga)))


def excel_del_corte(fuente: str, corte: str) -> Path:
    archivos = sorted((RAIZ / "data" / "raw" / fuente).glob(f"*/{corte}/*.xlsx"))
    if not archivos:
        sys.exit(f"No hay Excel original de {fuente} para el corte {corte} en data/raw.")
    return archivos[0]


def numeros(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.astype(str).str.replace(",", "."), errors="coerce")


class Revision:
    def __init__(self):
        self.total, self.diferencias = 0, []

    def igual(self, donde: str, campo: str, tablero, original, tol: float = TOL_PCT) -> bool:
        vacio_t, vacio_o = tablero is None, original is None or pd.isna(original)
        if isinstance(tablero, str) or isinstance(original, str):
            ok = str(tablero) == str(original)
        else:
            ok = (vacio_t and vacio_o) or (not vacio_t and not vacio_o and abs(float(tablero) - float(original)) <= tol)
        self.total += 1
        if not ok:
            self.diferencias.append(f"{donde} · {campo}: tablero={tablero!r} original={original!r}")
        return ok


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--metas", type=int, default=25)
    argumentos.add_argument("--actividades", type=int, default=25)
    argumentos.add_argument("--semilla", type=int, default=2026)
    opciones = argumentos.parse_args()

    d = datos_del_tablero()
    corte = d["ultimo"]
    metas = {m["i"]: m for m in d["metas"][corte]}
    acts = d["actividades"][corte]
    ruta_ap, ruta_gi = excel_del_corte("avance_plan", corte), excel_del_corte("gestion_inversion", corte)
    print(f"Corte {corte}\n  Avance del Plan:   {ruta_ap.relative_to(RAIZ)}\n  Gestión-Inversión: {ruta_gi.relative_to(RAIZ)}\n")

    ap = pd.read_excel(ruta_ap, "MetaProducto", dtype=str).set_index("PLAN_META_PRODUCTO_CODIGO")
    gi = pd.read_excel(ruta_gi, "datos", dtype=str)
    gi = gi[gi["VIGENCIA"].astype(int) == int(corte[:4])]
    for c in [c for c in gi.columns if c.startswith(P + "MAG") or c.startswith(P + "REC")]:
        gi[c] = numeros(gi[c])
    vig = {2024: 1, 2025: 2, 2026: 3, 2027: 4}[int(corte[:4])]
    prog_c, comp_c, giro_c = (f"{P}RECVIG{vig}_{x}" for x in ["PROGRAMADO", "COMPROMISOS_CONTRATADO", "GIROS"])
    mprog, mentr, mpct = (f"{P}MAGVIG{vig}_{x}" for x in ["PROGRAMADO", "ENTREGADO", "PORCENTREGADO"])
    ent = pd.read_excel(RAIZ / "data" / "raw" / "Normalizacion_Entidades.xlsx", dtype=str)
    nombre_entidad = dict(zip(pd.to_numeric(ent["Codigo_Hacienda"], errors="coerce"), ent["Nombre_entidad_sigla"]))
    rev = Revision()

    # ---------------- Metas ----------------
    random.seed(opciones.semilla)
    filas = []
    for i in sorted(random.sample(sorted(metas), min(opciones.metas, len(metas)))):
        m, a, g = metas[i], ap.loc[i], gi[gi["PLAN_META_PRODUCTO_CODIGO"] == i]
        prog, comp, giro = g[prog_c].sum(), g[comp_c].sum(), g[giro_c].sum()
        n0, e0 = rev.total, len(rev.diferencias)
        donde = f"Meta {i}"
        rev.igual(donde, "nombre", d["nombres"][i], a["PLAN_META_PRODUCTO_NOMBRE"])
        rev.igual(donde, "avance de vigencia", m["av"], round(100 * float(a["AVANCE_VIGENCIA"]), 2))
        rev.igual(donde, "transcurrido", m["at"], round(100 * float(a["AVANCE_TRANSCURRIDO"]), 2))
        rev.igual(donde, "cuatrienio", m["ap"], round(100 * float(a["AVANCE_PLAN"]), 2))
        rev.igual(donde, "% comprometido", m["pc"], round(100 * comp / prog, 2) if prog > 0 else None)
        rev.igual(donde, "% girado", m["pg"], round(100 * giro / prog, 2) if prog > 0 else None)
        rev.igual(donde, "recursos programados (M)", m["rp"], round(prog, 1), TOL_MILLONES)
        rev.igual(donde, "actividades programadas", m["na"], int((g[mprog] > 0).sum()))
        rev.igual(donde, "actividades sin entrega", m["nz"], int(((g[mprog] > 0) & (g[mentr] == 0)).sum()))
        filas.append({"meta": i, "avance": m["av"], "comprom.": m["pc"], "girado": m["pg"],
                      "sin entrega": f'{m["nz"] or 0:.0f} de {m["na"] or 0:.0f}', "entidades": g["ENTIDAD_CODIGO"].nunique(),
                      "correctos": f"{rev.total - n0 - (len(rev.diferencias) - e0)}/{rev.total - n0}"})
    pd.set_option("display.width", 220)
    print(f"=== {len(filas)} METAS (9 datos cada una) ===")
    print(pd.DataFrame(filas).to_string(index=False))

    # Promedios de las tarjetas del Panorama, con todas las metas del corte.
    sumas = gi.groupby("PLAN_META_PRODUCTO_CODIGO")[[prog_c, comp_c, giro_c]].sum()
    sumas = sumas[sumas[prog_c] > 0]
    promedio = lambda k: (lambda v: sum(v) / len(v))([m[k] for m in metas.values() if m[k] is not None])
    originales = {"av": (100 * numeros(ap["AVANCE_VIGENCIA"])).round(2).mean(),
                  "pc": (100 * sumas[comp_c] / sumas[prog_c]).round(2).mean(),
                  "pg": (100 * sumas[giro_c] / sumas[prog_c]).round(2).mean()}
    print(f"\n=== Promedios del Panorama ({len(metas)} metas) ===")
    for k, nombre in [("av", "Porcentaje programado"), ("pc", "Porcentaje comprometido"), ("pg", "Porcentaje de recursos girados")]:
        rev.igual("Panorama", nombre, round(promedio(k), 2), round(originales[k], 2))
        print(f"  {nombre:<32} tablero {promedio(k):6.2f} %   original {originales[k]:6.2f} %")

    # ---------------- Actividades ----------------
    # Las actividades del tablero siguen el orden de gold_actividad_corte, que conserva los códigos.
    gold = pd.read_csv(RAIZ / "data" / "gold" / "gold_actividad_corte.csv", sep="|", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    gold = gold[(pd.to_datetime(gold["fecha_corte"], dayfirst=True).dt.strftime("%Y-%m-%d") == corte)
                & (gold["fila_rezagada"] != "True")].reset_index(drop=True)
    if len(gold) != len(acts):
        sys.exit("gold_actividad_corte no corresponde al tablero publicado: regenere el tablero.")
    por_clave = gi.set_index(["ENTIDAD_CODIGO", "PROYECTO_CODIGO", "PROYECTO_ACTIVIDAD_CODIGO"])
    random.seed(opciones.semilla + 1)
    filas = []
    for k in sorted(random.sample(range(len(acts)), min(opciones.actividades, len(acts)))):
        t, gr = acts[k], gold.loc[k]
        o = por_clave.loc[(gr["entidad_codigo"], gr["proyecto_codigo"], gr["proyecto_actividad_codigo"])]
        donde = f'Actividad {gr["proyecto_codigo"]}-{gr["proyecto_actividad_codigo"]}'
        n0, e0 = rev.total, len(rev.diferencias)
        rev.igual(donde, "meta", t[0], o["PLAN_META_PRODUCTO_CODIGO"])
        rev.igual(donde, "nombre", t[3], o["PROYECTO_ACTIVIDAD_NOMBRE"])
        rev.igual(donde, "sector", t[1], o["SECTOR_NOMBRE"])
        rev.igual(donde, "entidad normalizada", t[2], nombre_entidad.get(int(gr["entidad_codigo"])))
        rev.igual(donde, "tipo de anualización", t[4], str(o[P + "TIPO_ANUALIZACION"]).strip())
        rev.igual(donde, "programado", t[5], o[mprog])
        rev.igual(donde, "entregado", t[6], o[mentr])
        rev.igual(donde, "% entregado", t[7], o[mpct])
        rev.igual(donde, "recursos (M)", t[8], o[prog_c], TOL_MILLONES)
        rev.igual(donde, "comprometido (M)", t[9], o[comp_c], TOL_MILLONES)
        rev.igual(donde, "girado (M)", t[10], o[giro_c], TOL_MILLONES)
        for j, bloque in enumerate(["MAGVIG1", "MAGVIG2", "MAGVIG3", "MAGVIG4", "MAGTOTAL"]):
            for x, campo in enumerate(["PROGRAMADO", "ENTREGADO", "PORCENTREGADO"]):
                rev.igual(donde, f"gráfica {bloque} {campo.lower()}", t[11][j * 3 + x], o[f"{P}{bloque}_{campo}"])
        filas.append({"meta": t[0], "actividad": f'{gr["proyecto_codigo"]}-{gr["proyecto_actividad_codigo"]}',
                      "entidad": t[2][:40], "programado": t[5], "entregado": t[6], "%": t[7], "recursos M": t[8],
                      "correctos": f"{rev.total - n0 - (len(rev.diferencias) - e0)}/{rev.total - n0}"})
    print(f"\n=== {len(filas)} ACTIVIDADES (26 datos cada una) ===")
    print(pd.DataFrame(filas).to_string(index=False))

    print(f"\nComprobaciones: {rev.total}   con diferencia: {len(rev.diferencias)}")
    for e in rev.diferencias:
        print("  DIFERENCIA", e)
    print("VALIDADO: el tablero coincide con los archivos originales." if not rev.diferencias else "HAY DIFERENCIAS: revise la lista.")
    sys.exit(1 if rev.diferencias else 0)


if __name__ == "__main__":
    main()
