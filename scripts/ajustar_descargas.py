"""Zona de descargas en la barra lateral de tablero/plantilla_foco.html (diseño compilado).

Encima de «Veeduría Distrital» aparece «Descargar archivos fuente», con su propio selector de fecha de
corte (es el mismo filtro de corte del tablero: cambiar uno cambia el otro) y un botón por cada archivo
original de la SDP disponible en ese corte:
  - Informe por entidad (PDF), del reporte de Gestión-Inversión.
  - Avance del Plan (Excel).
  - Gestión e inversión (Excel).
Si el corte no tiene alguno de los archivos, su botón no aparece. La barra lateral se desplaza sola
si no cabe en la pantalla. Cada botón descarga la copia del
repositorio (data/raw, ruta relativa: funciona al abrir tablero/index.html dentro del repositorio) y, si
se conoce, ofrece también el enlace oficial de la SDP. La lista sale de data/FUENTES.csv
(descargas_por_corte() en scripts/generar_tablero.py).

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_descargas.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* descargas-barra-lateral */"

CSS = MARCA + """
.enc-desc{margin-bottom:.875rem;padding-bottom:.875rem;border-bottom:1px solid #f1f5f9}
.enc-desc-tit{margin-bottom:.5rem;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:#64748b}
.enc-desc-lbl{display:block;margin-bottom:.25rem;font-size:11px;font-weight:500;color:#475569}
.enc-desc-sel{width:100%;height:2.25rem;padding:0 .5rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#fff;font-size:12px;color:#0f172a;cursor:pointer}
.enc-desc-sel:focus{outline:none;border-color:#b91c1c;box-shadow:0 0 0 2px rgba(185,28,28,.1)}
.enc-desc-lista{display:flex;flex-direction:column;gap:.375rem;margin-top:.625rem}
.enc-desc-btn{display:flex;align-items:center;gap:.5rem;padding:.45rem .6rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#f8fafc;color:#334155;font-size:12px;font-weight:500;text-decoration:none;transition:border-color .15s,background-color .15s,color .15s}
.enc-desc-btn:hover{border-color:#fca5a5;background:#fef2f2;color:#7f1d1d}
.enc-desc-btn svg{width:14px;height:14px;flex-shrink:0}
.enc-desc-btn span{display:flex;flex-direction:column;min-width:0;line-height:1.25}
.enc-desc-btn small{font-size:10px;font-weight:400;color:#94a3b8}
.enc-desc-sdp{align-self:flex-end;margin-top:-.125rem;font-size:10px;color:#64748b;text-decoration:underline}
.enc-desc-sdp:hover{color:#7f1d1d}
.enc-desc-vacio{margin-top:.5rem;font-size:11px;line-height:1.4;color:#94a3b8}
.enc-lateral{overflow-y:auto;overscroll-behavior:contain}
"""

COMPONENTE = (
    'function encDescargas({cut:c,cortes:K,ultimo:U,archivos:A,onCut:F}){'
    'let T=[["informe","Informe por entidad","PDF"],["avance","Avance del Plan","Excel"],["gestion","Gesti\\xF3n e inversi\\xF3n","Excel"]],'
    'L=(A&&A[c])||[],mb=b=>`${(b/1e6).toLocaleString("es-CO",{maximumFractionDigits:1})} MB`,'
    'D=T.map(([k,n,x])=>({k,n,x,a:L.find(y=>y.t===k)})).filter(z=>z.a);'
    'return(0,u.jsxs)("div",{className:"enc-desc",children:['
    '(0,u.jsx)("div",{className:"enc-desc-tit",children:"Descargar archivos fuente"}),'
    '(0,u.jsx)("label",{htmlFor:"f-cut-desc",className:"enc-desc-lbl",children:"Fecha de corte"}),'
    '(0,u.jsx)("select",{id:"f-cut-desc",className:"enc-desc-sel",value:c,onChange:e=>F(e.target.value),'
    'children:K.map(z=>(0,u.jsx)("option",{value:z,children:z===U?`${fl(z)} (\\xFAltimo corte)`:fl(z)},z))}),'
    'D.length?(0,u.jsx)("div",{className:"enc-desc-lista",children:D.map(z=>(0,u.jsxs)($.Fragment,{children:['
    '(0,u.jsxs)("a",{href:z.a.r,download:z.a.n,title:z.a.n,className:"enc-desc-btn",children:[(0,u.jsx)(Iu,{"aria-hidden":"true"}),'
    '(0,u.jsxs)("span",{children:[z.n,(0,u.jsx)("small",{children:`${z.x} \\xB7 ${mb(z.a.b)}`})]})]}),'
    'z.a.u&&(0,u.jsx)("a",{href:z.a.u,target:"_blank",rel:"noopener noreferrer",className:"enc-desc-sdp",children:"Enlace oficial SDP"})]},z.k))}):'
    '(0,u.jsx)("p",{className:"enc-desc-vacio",children:"No hay archivos fuente de este corte en el repositorio."})]})}'
)
ANCLA_COMPONENTE = "function ox({activeView:f,onSelectView:S,descargas:encDesc}){"   # ya con el cambio de firma

CAMBIOS = [
    # La barra lateral se desplaza sola si no cabe en la pantalla (así se llega a las descargas).
    ('(0,u.jsxs)("aside",{className:"no-print flex flex-col justify-between', '(0,u.jsxs)("aside",{className:"enc-lateral no-print flex flex-col justify-between'),
    ('function ox({activeView:f,onSelectView:S}){', 'function ox({activeView:f,onSelectView:S,descargas:encDesc}){'),
    ('(0,u.jsxs)("div",{className:"hidden border-t border-slate-100 px-5 py-4 lg:block",children:[!R&&',
     '(0,u.jsxs)("div",{className:"hidden border-t border-slate-100 px-5 py-4 lg:block",children:[encDesc&&(0,u.jsx)(encDescargas,{...encDesc}),!R&&'),
    ('(0,u.jsx)(ox,{activeView:b.view,onSelectView:',
     '(0,u.jsx)(ox,{descargas:{cut:b.cut,cortes:f.cortes,ultimo:f.ultimo,archivos:f.descargas,onCut:r=>ut("cut",r)},activeView:b.view,onSelectView:'),
]


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene la zona de descargas; no se cambia nada.")
        return
    for viejo, nuevo in CAMBIOS:
        html = una_vez(html, viejo, nuevo)
    html = una_vez(html, ANCLA_COMPONENTE, COMPONENTE + ANCLA_COMPONENTE)
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Zona de descargas agregada en {PLANTILLA}")


if __name__ == "__main__":
    main()
