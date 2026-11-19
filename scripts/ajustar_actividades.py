"""Gráfica emergente en «Detalle operativo de actividades» (tablero/plantilla_foco.html).

Al pasar el cursor sobre una actividad aparece una gráfica con su avance de vigencia año por año del
Plan (2024–2027), equivalente a la tabla «Año / Programación / Ejecución vigencia / Avance de la
vigencia» de los reportes de la SDP:
  - Barras por año: programado (gris) y ejecutado (color de semáforo).
  - Encima de cada año, el % de avance de la vigencia; debajo, «entregado de programado».
  - Semáforo: los años cerrados se comparan con 100 %; el año del corte, con lo esperado al corte
    (parte del año transcurrida); verde ≥ 90 % de lo esperado, ámbar 60–90 %, rojo < 60 %.
    Los años siguientes al del corte se muestran como «por ejecutar».
  - Al pie, el total «Al plan de desarrollo» (las actividades de tipo constante no traen total).
  - Leyenda abajo y centrada.

Además, como en la bandeja de metas, al bajar quedan fijos el encabezado de la tarjeta («Actividades
registradas», «Todas / Sin entrega», «Exportar CSV») y, debajo, los títulos de columna; «% entr.»
pasa a «% entregado». Los títulos de columna quedan fijos desde 1200 px de ancho, donde la tabla cabe
entera; en pantallas más angostas la tabla se desplaza de lado y solo queda fijo el encabezado.

Los datos vienen de gold_actividad_corte (columnas fisico_*_<año> y fisico_total_*): ver
serie_por_vigencia() en scripts/generar_tablero.py. Van en la posición 12 de cada actividad.

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_actividades.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* actividades-grafica-emergente */"

CSS = MARCA + """
.enc-pop{position:fixed;z-index:60;pointer-events:none;background:#fff;border:1px solid #e2e8f0;border-radius:.75rem;box-shadow:0 16px 40px -12px rgba(15,23,42,.28),0 4px 12px -6px rgba(15,23,42,.12);padding:.75rem .875rem .625rem}
.enc-pop-cab{font-size:11px;line-height:1.4;color:#64748b}
.enc-pop-meta{font-weight:600;color:#991b1b}
.enc-pop-tit{margin-top:.125rem;font-size:12px;font-weight:600;line-height:1.35;color:#0f172a;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.enc-pop-sub{margin:.375rem 0 .125rem;font-size:11px;color:#64748b}
.enc-pop svg{display:block;width:100%;height:auto}
.enc-pop-tot{margin-top:.125rem;text-align:center;font-size:11.5px;color:#334155}
.enc-pop-tot b{font-weight:700;color:#0f172a}
.enc-pop-ley{display:flex;flex-wrap:wrap;justify-content:center;gap:.25rem .875rem;margin-top:.375rem;font-size:11px;color:#64748b}
.enc-pop-ley span{display:inline-flex;align-items:center;gap:.3rem}
.enc-pop-ley i{display:inline-block;width:10px;height:10px;border-radius:2px}
.enc-acts{overflow:clip}
@media (min-width:1200px){.enc-acts-tabla{overflow:visible}}   /* más angosto, la tabla conserva su desplazamiento horizontal */
.enc-acts-cab{position:sticky;top:0;z-index:6;background:#fff}
.enc-acts thead th{position:sticky;top:var(--enc-cab-h,0px);z-index:5;background:#f8fafc;box-shadow:inset 0 -1px 0 #e2e8f0;vertical-align:bottom}
@media (min-width:768px){.enc-acts-cab{top:var(--filter-bar-h,0px)}.enc-acts thead th{top:calc(var(--filter-bar-h,0px) + var(--enc-cab-h,0px))}}
"""

COMPONENTE = (
    # Mide el alto del encabezado de la tarjeta para fijar los títulos de columna justo debajo.
    'function encCabFija(){let r=(0,$.useRef)(null);(0,$.useLayoutEffect)(()=>{let e=r.current;if(!e)return;'
    'let f=()=>e.parentElement&&e.parentElement.style.setProperty("--enc-cab-h",Math.ceil(e.getBoundingClientRect().height)+"px");'
    'if(f(),typeof ResizeObserver>"u")return;let o=new ResizeObserver(f);return o.observe(e),()=>o.disconnect()});return r}'
    'function encActGraf({h,cut:c}){let s=h.r[11];if(!s)return null;'
    'let V=window.__encVig||[2024,2025,2026,2027],n=V.length,yc=Number(c.slice(0,4)),eA=Number(c.slice(5,7))/12*100,'
    'Y=V.map((a,i)=>({a,p:s[i*3],e:s[i*3+1],q:s[i*3+2]})),T={p:s[n*3],e:s[n*3+1],q:s[n*3+2]},'
    'col={v:"#047857",a:"#b45309",r:"#b91c1c",n:"#94a3b8"},'
    'sem=y=>{if(y.a>yc||!(y.p>0))return"n";let r=(y.q??0)/(y.a<yc?100:eA);return r>=.9?"v":r>=.6?"a":"r"},'
    'mx=Math.max(1,...Y.map(y=>Math.max(y.p??0,y.e??0))),W=360,H=152,x0=10,gw=(W-2*x0)/n,base=116,tp=28,'
    'sc=v=>(base-tp)*Math.max(0,v??0)/mx,w=Math.min(24,gw*.27),'
    'PW=380,PH=290,vw=window.innerWidth,vh=window.innerHeight,'
    'L=h.x+18+PW>vw?Math.max(8,h.x-18-PW):h.x+18,Tp=Math.min(Math.max(8,h.y-PH/2),Math.max(8,vh-PH-8));'
    'return ex.createPortal((0,u.jsxs)("div",{className:"enc-pop",role:"tooltip",style:{left:L,top:Tp,width:PW},children:['
    '(0,u.jsxs)("div",{className:"enc-pop-cab",children:[(0,u.jsxs)("span",{className:"enc-pop-meta font-mono-tabular",children:["Meta ",h.r[0]]})," \\xB7 ",h.r[2]," \\xB7 ",h.r[4]]}),'
    '(0,u.jsx)("div",{className:"enc-pop-tit",children:h.r[3]}),'
    '(0,u.jsx)("div",{className:"enc-pop-sub",children:"Avance de vigencia por a\\xF1o del Plan"}),'
    '(0,u.jsxs)("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":"Avance de vigencia por a\\xF1o",children:['
    'Y.map((y,i)=>{let cx=x0+gw*i+gw/2,k=sem(y),fut=y.a>yc,sp=!(y.p>0),ac=y.a===yc;return(0,u.jsxs)("g",{children:['
    'ac&&(0,u.jsx)("rect",{x:x0+gw*i+2,y:2,width:gw-4,height:H-4,rx:6,fill:"#f8fafc"}),'
    '!sp&&(0,u.jsx)("rect",{x:cx-w-2,y:base-sc(y.p),width:w,height:sc(y.p),rx:2,fill:"#cbd5e1"}),'
    '!sp&&!fut&&(0,u.jsx)("rect",{x:cx+2,y:base-Math.max(sc(y.e),y.e>0?1.5:0),width:w,height:Math.max(sc(y.e),y.e>0?1.5:0),rx:2,fill:col[k]}),'
    '(0,u.jsx)("text",{x:cx,y:18,textAnchor:"middle",fontSize:"11.5",fontWeight:"700",fill:col[k],children:sp?"\\u2014":fut?"por ejecutar":`${ce(y.q)} %`}),'
    '(0,u.jsx)("text",{x:cx,y:base+15,textAnchor:"middle",fontSize:"10.5",fontWeight:ac?"700":"500",fill:"#334155",children:ac?`${y.a} \\xB7 corte`:y.a}),'
    '(0,u.jsx)("text",{x:cx,y:base+29,textAnchor:"middle",fontSize:"9.5",fill:"#64748b",children:sp?"sin programar":fut?`prog. ${ce(y.p)}`:`${ce(y.e)} de ${ce(y.p)}`})]},y.a)}),'
    '(0,u.jsx)("line",{x1:x0,x2:W-x0,y1:base,y2:base,stroke:"#e2e8f0"})]}),'
    '(0,u.jsx)("div",{className:"enc-pop-tot",children:T.p>0?(0,u.jsxs)(u.Fragment,{children:["Al plan de desarrollo: ",(0,u.jsxs)("b",{children:[ce(T.q)," %"]})," \\xB7 ",ce(T.e)," de ",ce(T.p)]}):'
    '"Actividad de tipo "+String(h.r[4]||"").toLowerCase()+": sin total del cuatrienio"}),'
    '(0,u.jsxs)("div",{className:"enc-pop-ley",children:['
    '(0,u.jsxs)("span",{children:[(0,u.jsx)("i",{style:{background:"#cbd5e1"}}),"Programado"]}),'
    '(0,u.jsxs)("span",{children:[(0,u.jsx)("i",{style:{background:"linear-gradient(90deg,#047857 0 33%,#b45309 33% 66%,#b91c1c 66%)"}}),"Ejecutado (sem\\xE1foro)"]})]})'
    ']}),document.body)}'
)
ANCLA_COMPONENTE = "function Fv({cut:f,"

CAMBIOS = [
    # Años del Plan disponibles para la gráfica (vienen en los datos: «vigencias»).
    ('S(r),C(w=>({...w,cut:w.cut||r.ultimo}))', 'window.__encVig=r.vigencias,S(r),C(w=>({...w,cut:w.cut||r.ultimo}))'),
    # Estado de la fila bajo el cursor.
    ('function Fv({cut:f,hasActivities:S,actividades:O,nombres:R,activityMetaId:o,onClearMetaFilter:q,onBackToMeta:U}){let[X,b]=(0,$.useState)(!1),',
     'function Fv({cut:f,hasActivities:S,actividades:O,nombres:R,activityMetaId:o,onClearMetaFilter:q,onBackToMeta:U}){let[encHv,encSetHv]=(0,$.useState)(null),encCabAct=encCabFija(),[X,b]=(0,$.useState)(!1),'),
    # Encabezado de la tarjeta y títulos de columna fijos al bajar.
    ('(0,u.jsxs)("section",{className:"overflow-hidden rounded-xl border border-slate-200/85 bg-white",children:[(0,u.jsxs)("div",{className:"flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4",children:[(0,u.jsxs)("div",{children:[(0,u.jsx)("h2",{className:"font-display text-base font-semibold text-slate-900",children:"Actividades registradas"})',
     '(0,u.jsxs)("section",{className:"enc-acts rounded-xl border border-slate-200/85 bg-white",children:[(0,u.jsxs)("div",{ref:encCabAct,className:"enc-acts-cab flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4",children:[(0,u.jsxs)("div",{children:[(0,u.jsx)("h2",{className:"font-display text-base font-semibold text-slate-900",children:"Actividades registradas"})'),
    ('(0,u.jsx)("div",{className:"overflow-x-auto",children:(0,u.jsxs)("table",{className:"w-full border-collapse text-left text-xs",children:[(0,u.jsx)("thead",{className:"border-b border-slate-200 bg-slate-50/80 text-[11px] font-semibold text-slate-600",children:(0,u.jsxs)("tr",{children:[(0,u.jsx)("th",{className:"px-4 py-3",children:"Meta"})',
     '(0,u.jsx)("div",{className:"enc-acts-tabla overflow-x-auto",children:(0,u.jsxs)("table",{className:"w-full border-collapse text-left text-xs",children:[(0,u.jsx)("thead",{className:"border-b border-slate-200 bg-slate-50/80 text-[11px] font-semibold text-slate-600",children:(0,u.jsxs)("tr",{children:[(0,u.jsx)("th",{className:"px-4 py-3",children:"Meta"})'),
    ('(0,u.jsx)("th",{className:"px-3 py-3 text-right",children:"% entr."})', '(0,u.jsx)("th",{className:"px-3 py-3 text-right",children:"% entregado"})'),
    # La gráfica (en un portal) y las filas que la activan.
    ('(0,u.jsx)("tbody",{className:"divide-y divide-slate-100",children:ft.length?ft.map((B,et)=>{let ht=ea(B);return(0,u.jsxs)("tr",{className:"hover:bg-slate-50/80",children:[',
     'encHv&&(0,u.jsx)(encActGraf,{h:encHv,cut:f}),'
     '(0,u.jsx)("tbody",{className:"divide-y divide-slate-100",onMouseLeave:()=>encSetHv(null),children:ft.length?ft.map((B,et)=>{let ht=ea(B);return(0,u.jsxs)("tr",{className:"hover:bg-slate-50/80",'
     'onMouseEnter:T=>encSetHv({r:B,x:T.clientX,y:T.clientY}),onMouseMove:T=>encSetHv({r:B,x:T.clientX,y:T.clientY}),children:['),
]


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene la gráfica de actividades; no se cambia nada.")
        return
    for viejo, nuevo in CAMBIOS:
        html = una_vez(html, viejo, nuevo)
    html = una_vez(html, ANCLA_COMPONENTE, COMPONENTE + ANCLA_COMPONENTE)
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Gráfica de actividades agregada en {PLANTILLA}")


if __name__ == "__main__":
    main()
