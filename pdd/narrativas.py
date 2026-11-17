"""Extrae de los PDF "Reporte de gestión e inversión por Entidad" los dos textos que
cada entidad escribe por indicador: "Retrasos y soluciones" y "Avances y Logros".

El PDF es una tabla muy ancha. Leerlo como texto corrido mezcla cifras con relatos,
así que se usa la POSICIÓN de cada línea en la página:

  - margen izquierdo, en negrita, "NNNN - ..."  -> empieza una meta producto
  - sangría corta, sin negrita, "NNNN - ..."    -> indicador de esa meta
  - margen izquierdo, "Retrasos y soluciones:"  -> empieza ese relato
  - margen izquierdo, "Avances y Logros:"       -> empieza ese relato
  - columna de relato (a la derecha del rótulo) -> líneas del relato en curso

Un relato puede continuar en la página siguiente; termina cuando aparece el
siguiente título en negrita (proyecto, meta, programa) u otro rótulo.
"""
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import pymupdf

# Posiciones horizontales (en puntos del PDF) medidas sobre los reportes de la SDP.
MARGEN_IZQUIERDO = 30          # títulos y rótulos empiezan antes de este punto
COLUMNA_RELATO = (135, 160)    # las líneas de relato empiezan dentro de este rango
SANGRIA_INDICADOR = (40, 60)

RE_CODIGO = re.compile(r"^(\d{4}) - (.+)")
RE_ENTIDAD = re.compile(r"^(\d{4})\s*-\s*(.+)")
RE_CORTE = re.compile(r"Fecha de Corte:\s*(\d{2}/\d{2}/\d{4})")
ROTULOS = {"retrasos y soluciones": "retrasos_y_soluciones", "avances y logros": "avances_y_logros"}


def _lineas_visuales(pagina) -> list[dict]:
    """Líneas de la página con coordenadas tal como se ven (el PDF viene girado 90°)."""
    giro = pagina.rotation_matrix
    lineas = []
    for bloque in pagina.get_text("dict")["blocks"]:
        for linea in bloque.get("lines", []):
            texto = "".join(t["text"] for t in linea["spans"]).strip()
            if not texto:
                continue
            caja = pymupdf.Rect(linea["bbox"]) * giro
            lineas.append({
                "fila": caja.y0, "izq": caja.x0, "texto": texto,
                "negrita": "Bold" in linea["spans"][0]["font"],
            })
    lineas.sort(key=lambda l: (round(l["fila"]), l["izq"]))
    return lineas


def es_reporte_por_entidad(ruta: Path, plan_codigo: str) -> str | None:
    """Devuelve la fecha de corte (AAAA-MM-DD) si el PDF es el reporte por entidad del plan."""
    try:
        with pymupdf.open(ruta) as doc:
            portada = doc[0].get_text()
    except Exception:
        return None
    corte = RE_CORTE.search(portada)
    if "por Entidad" not in portada or f"Distrital: {plan_codigo} -" not in portada or not corte:
        return None
    return datetime.strptime(corte.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")


def extraer_pdf(ruta: Path, corte: str) -> tuple[list[dict], dict]:
    """Un registro por (entidad, meta, indicador, campo narrativo) con su texto y páginas.
    Devuelve además un conteo para auditoría: cuántos rótulos tenía el PDF y cuántos
    relatos se obtuvieron, de modo que se note si algún relato se perdió."""
    registros: dict[tuple, dict] = {}
    rotulos_vistos = 0
    entidad = meta = indicador = campo = None
    entidad_nombre = indicador_nombre = ""

    with pymupdf.open(ruta) as doc:
        for numero, pagina in enumerate(doc, start=1):
            lineas = _lineas_visuales(pagina)
            # El encabezado repetido de cada página termina en el título de la primera
            # columna ("Objetivo Estratégico / Programa / ..."), que puede ocupar dos renglones.
            fin_encabezado = next((l["fila"] + 15 for l in lineas
                                   if l["texto"].startswith("Objetivo Estratégico /")), 0)
            for l in lineas:
                texto, izq = l["texto"], l["izq"]
                if l["fila"] <= fin_encabezado:
                    m = RE_ENTIDAD.match(texto)
                    if l["negrita"] and m and izq > 200 and m.group(1) != entidad:
                        entidad, entidad_nombre = m.group(1), m.group(2).strip()
                        meta = indicador = campo = None
                    continue

                if izq < MARGEN_IZQUIERDO:
                    rotulo = ROTULOS.get(texto.rstrip(": ").lower())
                    if rotulo:
                        campo = rotulo
                        rotulos_vistos += 1
                    elif l["negrita"]:
                        campo = None                      # cualquier título cierra el relato
                        m = RE_CODIGO.match(texto)
                        if m:
                            meta, indicador, indicador_nombre = m.group(1), None, ""
                    continue

                if SANGRIA_INDICADOR[0] <= izq <= SANGRIA_INDICADOR[1] and not l["negrita"]:
                    m = RE_CODIGO.match(texto)
                    if m:
                        indicador, indicador_nombre, campo = m.group(1), m.group(2).strip(), None
                    continue

                if campo and meta and COLUMNA_RELATO[0] <= izq <= COLUMNA_RELATO[1] and not l["negrita"]:
                    clave = (entidad, meta, indicador, campo)
                    reg = registros.setdefault(clave, {
                        "fecha_corte": corte, "entidad_codigo": entidad, "entidad_nombre": entidad_nombre,
                        "meta_producto_codigo": meta, "indicador_codigo": indicador or "",
                        "indicador_nombre": indicador_nombre, "campo": campo,
                        "lineas": [], "paginas": [], "archivo_fuente": ruta.name,
                    })
                    reg["lineas"].append(texto)
                    if numero not in reg["paginas"]:
                        reg["paginas"].append(numero)

    salida = []
    for reg in registros.values():
        reg["texto"] = _unir_lineas(reg.pop("lineas"))
        paginas = reg.pop("paginas")
        reg["pagina_inicio"], reg["pagina_fin"] = paginas[0], paginas[-1]
        if re.search(r"[A-Za-zÁ-ú]", reg["texto"]):      # descarta celdas con solo "." o "-"
            salida.append(reg)
    auditoria = {"fecha_corte": corte, "archivo_fuente": ruta.name, "rotulos_en_pdf": rotulos_vistos,
                 "relatos_con_texto": len(salida), "celdas_vacias": rotulos_vistos - len(salida)}
    return salida, auditoria


def _unir_lineas(lineas: list[str]) -> str:
    """Une los renglones de un relato; una viñeta abre párrafo nuevo."""
    parrafos: list[str] = []
    for linea in lineas:
        linea = linea.replace('""', '"').strip()
        if not parrafos or re.match(r"^[•\-\*·]\s", linea):
            parrafos.append(linea)
        else:
            parrafos[-1] += " " + linea
    texto = "\n".join(p.lstrip("•-*· ").strip(' "') for p in parrafos)
    return re.sub(r"[ \t]+", " ", texto).strip()


def extraer_narrativas(config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recorre las carpetas configuradas y extrae los relatos de todos los reportes por
    entidad del plan. Si el mismo corte aparece en dos PDF (versiones), usa el más nuevo.
    Devuelve los relatos y la tabla de auditoría de la extracción (una fila por PDF)."""
    por_corte: dict[str, Path] = {}
    for carpeta in config["rutas"]["pdf_narrativas"]:
        for ruta in sorted(Path(carpeta).rglob("*.pdf")):
            corte = es_reporte_por_entidad(ruta, config["plan"]["codigo"])
            if corte and (corte not in por_corte or ruta.stat().st_mtime > por_corte[corte].stat().st_mtime):
                por_corte[corte] = ruta
    if not por_corte:
        raise FileNotFoundError("No se encontró ningún PDF 'Reporte de gestión e inversión por Entidad'.")

    registros, auditoria = [], []
    for corte, ruta in sorted(por_corte.items()):
        nuevos, conteo = extraer_pdf(ruta, corte)
        print(f"  {corte}: {conteo['rotulos_en_pdf']} rótulos, {len(nuevos)} relatos con texto ({ruta.name})")
        registros.extend(nuevos)
        auditoria.append(conteo)

    tabla = pd.DataFrame(registros)
    # Identificador estable: el mismo relato conserva su código entre ejecuciones.
    tabla.insert(0, "fragmento_id", tabla["fecha_corte"].str.replace("-", "") + "-" + tabla["entidad_codigo"] + "-"
                 + tabla["meta_producto_codigo"] + "-" + tabla["indicador_codigo"] + "-"
                 + tabla["campo"].str[0].str.upper())
    tabla["fecha_corte"] = pd.to_datetime(tabla["fecha_corte"])
    auditoria = pd.DataFrame(auditoria)
    auditoria["fecha_corte"] = pd.to_datetime(auditoria["fecha_corte"])
    return tabla, auditoria