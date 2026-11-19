"""Ajuste del encabezado en tablero/plantilla_foco.html (diseño compilado).

El título de cada vista y los filtros quedan en un solo recuadro fijo arriba: el título a la
izquierda y, a la derecha, un botón «Filtros» que despliega los filtros de sector, entidad y meta. Como la plantilla es
una aplicación ya compilada (sin código fuente), el cambio se aplica reemplazando fragmentos exactos.
El selector de fecha de corte queda junto al botón. Se ejecuta una sola vez; si la plantilla ya tiene el ajuste, no hace nada.

    python scripts/ajustar_encabezado.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* encabezado-fijo */"

CSS = MARCA + """
.enc-fijo{position:relative;z-index:30;margin:0 -1rem;padding:.5rem 1rem .75rem;background:rgba(247,248,250,.95);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
@media (min-width:640px){.enc-fijo{margin:0 -1.5rem;padding-left:1.5rem;padding-right:1.5rem}}
@media (min-width:768px){.enc-fijo{position:sticky;top:0}}
@media (min-width:1024px){.enc-fijo{margin:0 -2rem;padding-left:2rem;padding-right:2rem}}
.enc-caja{display:flex;flex-direction:column;gap:.875rem;border:1px solid rgba(226,232,240,.85);border-radius:.75rem;background:#fff;padding:1rem 1.25rem}
@media (min-width:768px){.enc-caja{flex-direction:row;align-items:center;justify-content:space-between;gap:1.5rem}}
.enc-titulo{min-width:0}
.enc-filtros{position:relative;display:flex;align-items:flex-end;gap:.625rem;flex-shrink:0}
.enc-corte{width:210px}
.enc-boton{display:inline-flex;align-items:center;gap:.5rem;height:2.5rem;padding:0 .875rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#fff;color:#334155;font-size:.75rem;font-weight:600;white-space:nowrap;cursor:pointer;transition:background-color .15s,border-color .15s}
.enc-boton:hover{border-color:#cbd5e1;background:#f8fafc}
.enc-boton.activo{border-color:#fca5a5;background:rgba(254,242,242,.7);color:#7f1d1d}
.enc-boton svg{width:.875rem;height:.875rem}
.enc-boton .enc-flecha{transition:transform .15s}
.enc-boton.abierto .enc-flecha{transform:rotate(180deg)}
.enc-num{display:inline-flex;align-items:center;justify-content:center;min-width:1.25rem;height:1.25rem;padding:0 .35rem;border-radius:999px;background:#b91c1c;color:#fff;font-size:10px;font-weight:700}
.enc-panel{position:absolute;right:0;top:calc(100% + .5rem);width:min(380px,calc(100vw - 2rem));border:1px solid rgba(226,232,240,.9);border-radius:.75rem;background:#fff;padding:1rem;box-shadow:0 12px 32px -8px rgba(15,23,42,.18),0 4px 10px -4px rgba(15,23,42,.08)}
@media (max-width:767px){.enc-corte{flex:1;width:auto}.enc-panel{left:0;right:auto;width:100%}}
.enc-grid{display:grid;grid-template-columns:1fr;gap:.75rem}
.enc-acciones{display:flex;justify-content:flex-end;gap:.5rem;margin-top:1rem;padding-top:.875rem;border-top:1px solid #f1f5f9}
.enc-sec,.enc-pri{display:inline-flex;align-items:center;gap:.375rem;height:2.25rem;padding:0 .875rem;border-radius:.5rem;font-size:.75rem;font-weight:600;cursor:pointer}
.enc-sec{border:1px solid #e2e8f0;background:#fff;color:#475569}
.enc-sec:hover:not(:disabled){background:#f8fafc;color:#0f172a}
.enc-sec:disabled{opacity:.4;cursor:default}
.enc-pri{border:1px solid #b91c1c;background:#b91c1c;color:#fff}
.enc-pri:hover{background:#991b1b}
.enc-sec svg{width:.875rem;height:.875rem}
"""

# 1) El componente de filtros recibe el título y decide si muestra los filtros.
FIRMA_VIEJA = "onResetFilters:y,onHeightChange:D}){let[I,k]=(0,$.useState)(!1),ft=(0,$.useRef)(null);"
FIRMA_NUEVA = ("onResetFilters:y,onHeightChange:D,title:encT,subtitle:encS,showFilters:encF=!0}){let[I,k]=(0,$.useState)(!1),ft=(0,$.useRef)(null),encR=(0,$.useRef)(null);"
               "(0,$.useEffect)(()=>{if(!I)return;let h=e=>{encR.current&&!encR.current.contains(e.target)&&k(!1)},"
               "t=e=>{e.key===\"Escape\"&&!(e.target&&e.target.getAttribute&&e.target.getAttribute(\"aria-expanded\")===\"true\")&&k(!1)};"
               "return document.addEventListener(\"mousedown\",h),document.addEventListener(\"keydown\",t),"
               "()=>{document.removeEventListener(\"mousedown\",h),document.removeEventListener(\"keydown\",t)}},[I]);")

# 2) Lo que dibuja: un recuadro con título a la izquierda y el desplegable de filtros a la derecha.
INICIO_RETORNO = 'T=[f.sector,f.entity,f.metaId].filter(Boolean).length+it;return(0,u.jsx)("div",{ref:ft,className:"no-print md:sticky'
FIN_RETORNO = '(0,u.jsx)(Bf,{className:"h-3.5 w-3.5"})})]})]})]})]})})}'

SELECTS = ('(0,u.jsx)(_a,{id:"f-sector",label:"Sector",value:f.sector,options:B,placeholder:b?"Todos los sectores":"Corte sin actividades",disabled:!b,onChange:z=>A("sector",z)}),'
           '(0,u.jsx)(_a,{id:"f-entity",label:"Entidad",value:f.entity,options:et,placeholder:"Todas las entidades",disabled:!b,onChange:z=>A("entity",z)}),'
           '(0,u.jsx)(_a,{id:"f-meta",label:"Meta",value:f.metaId,options:q,placeholder:"Todas las metas",onChange:z=>A("metaId",z)})')

RETORNO_NUEVO = (
    'T=[f.sector,f.entity,f.metaId].filter(Boolean).length+it;'
    'return(0,u.jsx)("div",{ref:ft,className:"enc-fijo",children:(0,u.jsxs)("section",{"aria-label":"Encabezado de la vista",className:"enc-caja",children:['
    '(0,u.jsxs)("header",{className:"enc-titulo",children:['
    '(0,u.jsx)("div",{className:"text-xs font-semibold text-red-800",children:"Bogot\\xE1 Camina Segura \\xB7 Plan 17"}),'
    '(0,u.jsx)("h1",{className:"font-display mt-1 text-2xl font-bold tracking-tight text-slate-900 text-balance sm:text-[28px]",children:encT}),'
    '(0,u.jsx)("p",{className:"mt-1 text-xs leading-relaxed text-slate-500 sm:text-sm",children:encS})]}),'
    'encF&&(0,u.jsxs)("div",{ref:encR,className:"enc-filtros no-print",children:['
    '(0,u.jsx)("div",{className:"enc-corte",children:(0,u.jsx)(_a,{id:"f-cut",label:"Fecha de corte",value:f.cut,options:G,placeholder:"Seleccionar corte",searchable:!1,allowClear:!1,onChange:z=>A("cut",z)})}),'
    '(0,u.jsxs)("button",{type:"button","aria-expanded":I,"aria-haspopup":"dialog",onClick:()=>k(z=>!z),'
    'className:`enc-boton${I?" abierto":""}${T>0?" activo":""}`,children:['
    '(0,u.jsx)(Kv,{"aria-hidden":"true"}),(0,u.jsx)("span",{children:"Filtros"}),'
    'T>0&&(0,u.jsx)("span",{className:"enc-num",children:T}),'
    '(0,u.jsx)(cm,{className:"enc-flecha","aria-hidden":"true"})]}),'
    'I&&(0,u.jsxs)("div",{role:"dialog","aria-label":"Filtros de an\\xE1lisis",className:"enc-panel",children:['
    '(0,u.jsxs)("div",{className:"enc-grid",children:[' + SELECTS +
    ']}),'
    '(0,u.jsxs)("div",{className:"enc-acciones",children:['
    '(0,u.jsxs)("button",{type:"button",onClick:y,disabled:T===0,className:"enc-sec",children:[(0,u.jsx)(Xv,{"aria-hidden":"true"}),(0,u.jsx)("span",{children:"Limpiar filtros"})]}),'
    '(0,u.jsx)("button",{type:"button",onClick:()=>k(!1),className:"enc-pri",children:"Listo"})]})]})]})]})})}'
)

# 3) La página usa ese recuadro en todas las vistas y deja de dibujar el título aparte.
USO_VIEJO = 'b.view!=="ficha"&&(0,u.jsx)(tx,{'
USO_NUEVO = '(0,u.jsx)(tx,{title:he.title,subtitle:he.subtitle,showFilters:b.view!=="ficha",'
CABECERA_VIEJA = ('(0,u.jsxs)("header",{className:`border-b border-slate-200/80 pb-4 ${b.view==="ficha"?"pt-6":""}`,children:['
                  '(0,u.jsx)("div",{className:"text-xs font-semibold text-red-800",children:"Bogot\\xE1 Camina Segura \\xB7 Plan 17"}),'
                  '(0,u.jsx)("h1",{className:"font-display mt-1 text-2xl font-bold tracking-tight text-slate-900 text-balance sm:text-[28px]",children:he.title}),'
                  '(0,u.jsx)("p",{className:"mt-1 text-xs leading-relaxed text-slate-500 sm:text-sm",children:he.subtitle})]}),')


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:80]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene el encabezado fijo; no se cambia nada.")
        return
    html = una_vez(html, FIRMA_VIEJA, FIRMA_NUEVA)
    i = html.index(INICIO_RETORNO)
    j = html.index(FIN_RETORNO, i) + len(FIN_RETORNO)
    html = html[:i] + RETORNO_NUEVO + html[j:]
    html = una_vez(html, USO_VIEJO, USO_NUEVO)
    html = una_vez(html, CABECERA_VIEJA, "")
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Encabezado ajustado en {PLANTILLA}")


if __name__ == "__main__":
    main()
