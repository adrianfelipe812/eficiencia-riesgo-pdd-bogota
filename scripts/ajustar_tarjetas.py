"""Ajuste de las tarjetas del Panorama en tablero/plantilla_foco.html (diseño compilado).

Tarjetas, en este orden: Metas en el alcance, Porcentaje programado, Porcentaje de recursos girados,
Porcentaje comprometido, Rezagadas en el corte y Alerta alta. Se quitan «Narran un problema» y
«Eficiencia mediana». El contenido va centrado y el ícono queda a la derecha del número.

Los tres porcentajes son promedios simples por meta (suma de los porcentajes ÷ número de metas con dato)
sobre las metas del alcance filtrado:
  - Porcentaje programado: avance_vigencia (avance físico frente a lo programado del año).
  - Porcentaje de recursos girados: pct_giros (recursos girados ÷ programados del año).
  - Porcentaje comprometido: pct_compromisos (recursos comprometidos ÷ programados del año).

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_tarjetas.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* tarjetas-panorama */"

CSS = MARCA + """
.kpi-grid{display:grid;gap:.75rem;grid-template-columns:repeat(2,minmax(0,1fr))}
@media (min-width:768px){.kpi-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (min-width:1280px){.kpi-grid{grid-template-columns:repeat(6,minmax(0,1fr))}}
.kpi{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.4rem;min-width:0;min-height:112px;padding:.875rem .625rem;border:1px solid rgba(226,232,240,.85);border-radius:.75rem;background:#fff;text-align:center;font:inherit;color:inherit;transition:border-color .15s}
button.kpi{cursor:pointer}
button.kpi:hover:not(:disabled){border-color:#cbd5e1}
button.kpi:disabled{cursor:default}
button.kpi:focus-visible{outline:2px solid #b91c1c;outline-offset:2px}
.kpi-l{font-size:12px;font-weight:500;line-height:1.25;color:#64748b}
.kpi-v{display:flex;align-items:center;justify-content:center;gap:.5rem}
.kpi-n{font-size:28px;font-weight:600;line-height:1;letter-spacing:-.02em;white-space:nowrap}
.kpi-v svg{width:1.125rem;height:1.125rem;flex-shrink:0}
.kpi-s{font-size:11px;line-height:1.3;color:#64748b}
.kpi-slate .kpi-n{color:#0f172a}.kpi-slate svg{color:#94a3b8}
.kpi-teal .kpi-n{color:#115e59}.kpi-teal svg{color:#0f766e}
.kpi-indigo .kpi-n{color:#3730a3}.kpi-indigo svg{color:#4f46e5}
.kpi-sky .kpi-n{color:#075985}.kpi-sky svg{color:#0284c7}
.kpi-amber .kpi-n{color:#b45309}.kpi-amber svg{color:#d97706}
.kpi-red .kpi-n{color:#b91c1c}.kpi-red svg{color:#b91c1c}
"""

# Íconos nuevos (lucide), creados con la misma fábrica que usa la aplicación.
ICONO_ANCLA = 'Bv=wt("gauge",[["path",{d:"m12 14 4-4",key:"9kzdfg"}],["path",{d:"M3.34 19a10 10 0 1 1 17.32 0",key:"19p75a"}]])'
ICONOS = (ICONO_ANCLA +
          ',encBk=wt("banknote",[["rect",{width:"20",height:"12",x:"2",y:"6",rx:"2",key:"9lu3g6"}],["circle",{cx:"12",cy:"12",r:"2",key:"1c9p78"}],["path",{d:"M6 12h.01M18 12h.01",key:"113zkx"}]])'
          ',encFc=wt("file-check",[["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",key:"1rqfz7"}],["path",{d:"M14 2v4a2 2 0 0 0 2 2h4",key:"tnqrlb"}],["path",{d:"m9 15 2 2 4-4",key:"1grp1n"}]])')

# Componente de tarjeta y promedio simple.
TARJETA = ('function encKpi({label:l,value:v,sub:s,icon:I,tone:t,onClick:c,disabled:d}){'
           'let h=[(0,u.jsx)("span",{className:"kpi-l",children:l}),'
           '(0,u.jsxs)("span",{className:"kpi-v",children:[(0,u.jsx)("span",{className:"kpi-n font-mono-tabular",children:v}),(0,u.jsx)(I,{"aria-hidden":"true"})]}),'
           '(0,u.jsx)("span",{className:"kpi-s",children:s})];'
           'return c?(0,u.jsx)("button",{type:"button",onClick:c,disabled:d,className:`kpi kpi-${t}`,children:h}):(0,u.jsx)("div",{className:`kpi kpi-${t}`,children:h})}'
           'function encProm(a){let v=a.filter(x=>x!=null&&!Number.isNaN(x));return v.length?v.reduce((s,x)=>s+x,0)/v.length:null}'
           'function encPct(v){return v==null?"\\u2014":`${ce(v)} %`}')
FUNCION_ANCLA = "function cx({cut:f,"

CALCULO_VIEJO = 'y=jn(bi(U.map(D=>D.ef)));return(0,u.jsxs)("div",{className:"space-y-4"'
CALCULO_NUEVO = ('y=jn(bi(U.map(D=>D.ef))),encAv=encProm(U.map(D=>D.av)),encPc=encProm(U.map(D=>D.pc)),encPg=encProm(U.map(D=>D.pg)),'
                 'encSinFin=encPc==null&&encPg==null;return(0,u.jsxs)("div",{className:"space-y-4"')

GRID_INICIO = '(0,u.jsxs)("div",{className:"grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",children:['
GRID_FIN = '"Frente a comparables (0 a 1)"})]})]})'
GRID_NUEVO = (
    '(0,u.jsxs)("div",{className:"kpi-grid",children:['
    '(0,u.jsx)(encKpi,{label:"Metas en el alcance",value:U.length,sub:(0,u.jsxs)(u.Fragment,{children:["de ",(0,u.jsx)("b",{className:"font-medium text-slate-700",children:q.length})," del corte"]}),icon:xm,tone:"slate",onClick:()=>b({senal:"",estado:""})}),'
    '(0,u.jsx)(encKpi,{label:"Porcentaje programado",value:encPct(encAv),sub:"Promedio de avance f\\xEDsico del a\\xF1o",icon:Rv,tone:"teal"}),'
    '(0,u.jsx)(encKpi,{label:"Porcentaje de recursos girados",value:encPct(encPg),sub:encSinFin?"Corte sin datos financieros":"Promedio girado / programado",icon:encBk,tone:"indigo"}),'
    '(0,u.jsx)(encKpi,{label:"Porcentaje comprometido",value:encPct(encPc),sub:encSinFin?"Corte sin datos financieros":"Promedio comprometido / programado",icon:encFc,tone:"sky"}),'
    '(0,u.jsx)(encKpi,{label:"Rezagadas en el corte",value:C,sub:"20 % m\\xE1s bajo de su tipo",icon:gm,tone:"amber",onClick:()=>b({senal:"rezago",estado:""})}),'
    '(0,u.jsx)(encKpi,{label:"Alerta alta",value:A??0,sub:S?"Riesgo en pr\\xF3ximo corte":"Solo en \\xFAltimo corte",icon:Zv,tone:"red",onClick:()=>b({senal:"alta",estado:""}),disabled:!S})]})'
)


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:80]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene las tarjetas ajustadas; no se cambia nada.")
        return
    html = una_vez(html, ICONO_ANCLA, ICONOS)
    html = una_vez(html, FUNCION_ANCLA, TARJETA + FUNCION_ANCLA)
    html = una_vez(html, CALCULO_VIEJO, CALCULO_NUEVO)
    i = html.index(GRID_INICIO)
    j = html.index(GRID_FIN, i) + len(GRID_FIN)
    html = html[:i] + GRID_NUEVO + html[j:]
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Tarjetas ajustadas en {PLANTILLA}")


if __name__ == "__main__":
    main()
