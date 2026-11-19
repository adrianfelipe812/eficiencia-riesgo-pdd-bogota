"""Ajuste de las gráficas en tablero/plantilla_foco.html (diseño compilado).

1. Las leyendas salen del dibujo y quedan abajo de cada gráfica, centradas.
2. Cada gráfica llena la celda en la que está: mide su recuadro y estira el área de trazado
   (ejes, barras, puntos y líneas se recalculan; los textos no se deforman). Cuando la celda es
   más baja que la gráfica original, se conserva el tamaño original.
3. En las gráficas por corte, la franja gris marca el año del corte seleccionado.

Gráficas: histograma de avance (lx), dispersión avance/comprometido (ax), evolución del alcance (ix)
y evolución de la meta frente a su tipo en la ficha (nx). Además, la fila de la evolución y los
accesos directos pasa a tener tarjetas de igual alto.

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_graficas.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* graficas-llenan-celda */"

CSS = MARCA + """
.enc-graf{position:relative;flex:1 1 auto;width:100%}
.enc-svg{position:absolute;inset:0;display:block;width:100%;height:100%}
.enc-ley{display:flex;flex-wrap:wrap;justify-content:center;gap:.25rem 1rem;margin-top:.5rem;font-size:11px;line-height:1.4;color:#64748b}
.enc-ley span{display:inline-flex;align-items:center;gap:.375rem;white-space:nowrap}
.enc-ley b{font-weight:600}
.enc-ley i{display:inline-block;flex-shrink:0}
.enc-ley-dot{width:9px;height:9px;border-radius:50%}
.enc-ley-sq{width:8px;height:8px;border-radius:2px}
.enc-ley-dash{width:20px;height:0;border-top:2px dashed}
"""

# Utilidades: alto medido de la celda y leyenda en HTML.
UTILIDADES = (
    'function encAlto(w,h){let r=(0,$.useRef)(null),[H,sH]=(0,$.useState)(h);'
    '(0,$.useLayoutEffect)(()=>{let e=r.current;if(!e)return;let f=()=>{let b=e.getBoundingClientRect();'
    'if(b.width>0&&b.height>0){let n=Math.max(h,Math.round(w*b.height/b.width));sH(p=>Math.abs(p-n)>1?n:p)}};'
    'if(f(),typeof ResizeObserver>"u")return;let o=new ResizeObserver(f);return o.observe(e),()=>o.disconnect()});return[r,H]}'
    'function encLey(a){return(0,u.jsx)("div",{className:"enc-ley",children:a.map((x,i)=>(0,u.jsxs)("span",{style:x.t?{color:x.t}:void 0,'
    'children:[(0,u.jsx)("i",{className:`enc-ley-${x.k}`,style:x.k==="dash"?{borderColor:x.c}:{background:x.c}}),'
    'x.b?(0,u.jsx)("b",{children:x.l}):x.l]},i))})}'
)
ANCLA_UTILIDADES = "function Ca({title:f,"

# Tarjeta contenedora: el área de la gráfica se vuelve columna flexible para poder crecer.
CA_VIEJO = '"mt-2.5 flex-1"'
CA_NUEVO = '"mt-2.5 flex flex-1 flex-col"'
# Fila de evolución + accesos directos: tarjetas del mismo alto.
FILA_VIEJA = '"grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)]"'
FILA_NUEVA = '"grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)]"'

SVG_CLASE = 'className:"w-full h-auto block"'
FIN = ']})]})}'   # cierre del svg, de la tarjeta y de la función

GRAFICAS = {
    # Histograma de avance físico. Visible: y de 30 a 30+H (la leyenda ocupaba y < 30).
    "lx": dict(
        ancho=540, alto=218,
        cambios=[
            ('let{bindTip:O,TooltipOverlay:R}=tc(),', 'let{bindTip:O,TooltipOverlay:R}=tc(),[encRf,encH]=encAlto(540,218),'),
            ('C=540,J=248,A=44,y=208,D=162,', 'C=540,J=encH,A=44,y=30+encH-40,D=y-46,'),
            ('viewBox:`0 0 ${C} ${J}`', 'viewBox:`0 30 ${C} ${J}`'),
            ('(0,u.jsx)("circle",{cx:49,cy:12,r:4.5,fill:fe}),(0,u.jsx)("text",{x:58,y:15.5,fontSize:"10.5",fontWeight:"600",fill:fe,children:"Rezagadas"}),'
             '(0,u.jsx)("circle",{cx:136,cy:12,r:4.5,fill:fm}),(0,u.jsx)("text",{x:145,y:15.5,fontSize:"10.5",fill:Yt,children:"Dem\\xE1s metas"}),', ''),
            ('y:222,', 'y:y+14,'),
            ('y:244,', 'y:y+36,'),
        ],
        leyenda='[{k:"dot",c:fe,l:"Rezagadas",b:1,t:fe},{k:"dot",c:fm,l:"Dem\\xE1s metas"}]'),
    # Dispersión avance físico vs. dinero comprometido. Visible: y de 18 a 18+H.
    "ax": dict(
        ancho=540, alto=218,
        cambios=[
            ('let{bindTip:o,TooltipOverlay:q}=tc(),', 'let{bindTip:o,TooltipOverlay:q}=tc(),[encRf,encH]=encAlto(540,218),'),
            ('A=540,y=236,D=46,I=528,k=196,ft=482,G=168,', 'A=540,y=encH,D=46,I=528,k=18+encH-40,ft=482,G=k-28,'),
            ('viewBox:`0 0 ${A} ${y}`', 'viewBox:`0 18 ${A} ${y}`'),
            ('(0,u.jsx)("circle",{cx:51,cy:12,r:4.5,fill:fe}),(0,u.jsx)("text",{x:60,y:15.5,fontSize:"10.5",fontWeight:"600",fill:fe,children:"Rezagadas"}),'
             '(0,u.jsx)("circle",{cx:138,cy:12,r:3.5,fill:"#94a3b8"}),(0,u.jsx)("text",{x:146,y:15.5,fontSize:"10.5",fill:Yt,children:"Dem\\xE1s metas"}),'
             '(0,u.jsx)("line",{x1:232,y1:12,x2:252,y2:12,stroke:P,strokeWidth:1.5,strokeDasharray:"4 3",opacity:.75}),'
             '(0,u.jsx)("text",{x:258,y:15.5,fontSize:"10.5",fill:P,children:"Equilibrio (avance = comprometido)"}),', ''),
            ('y:112,fontSize:"10",fill:Yt,textAnchor:"middle",transform:"rotate(-90 13 112)"',
             'y:(k+28)/2,fontSize:"10",fill:Yt,textAnchor:"middle",transform:`rotate(-90 13 ${(k+28)/2})`'),
            ('y:210,', 'y:k+14,'),
            ('y:232,', 'y:k+36,'),
        ],
        leyenda='[{k:"dot",c:fe,l:"Rezagadas",b:1,t:fe},{k:"dot",c:"#94a3b8",l:"Dem\\xE1s metas"},{k:"dash",c:P,l:"Equilibrio (avance = comprometido)",t:P}]'),
    # Evolución del alcance por corte. Visible: y de 24 a 24+H.
    "ix": dict(
        ancho=680, alto=162,
        cambios=[
            ('let{bindTip:q,TooltipOverlay:U}=tc(),', 'let{bindTip:q,TooltipOverlay:U}=tc(),[encRf,encH]=encAlto(680,162),'),
            ('A=680,y=186,D=32,I=624,k=140,ft=104,', 'A=680,y=encH,D=32,I=624,k=24+encH-46,ft=k-36,'),
            ('viewBox:`0 0 ${A} ${y}`', 'viewBox:`0 24 ${A} ${y}`'),
            ('(0,u.jsx)("circle",{cx:38,cy:12,r:4.5,fill:fe}),(0,u.jsx)("text",{x:47,y:15.5,fontSize:"11",fontWeight:"600",fill:fe,children:"Avance f\\xEDsico (mediana)"}),'
             '(0,u.jsx)("rect",{x:192,y:8.5,width:7,height:7,rx:1.5,fill:Yt}),(0,u.jsx)("text",{x:204,y:15.5,fontSize:"11",fill:Yt,children:"Dinero comprometido (mediana)"}),', ''),
        ],
        leyenda='[{k:"dot",c:fe,l:"Avance f\\xEDsico (mediana)",b:1,t:fe},{k:"sq",c:Yt,l:"Dinero comprometido (mediana)"}]'),
    # Ficha de la meta: evolución frente a las metas de su tipo. Visible: y de 0 a H; ancho 544 (antes 520) para que no se corte la última cifra.
    "nx": dict(
        ancho=544, alto=178,
        cambios=[
            ('let{bindTip:q,TooltipOverlay:U}=tc(),', 'let{bindTip:q,TooltipOverlay:U}=tc(),[encRf,encH]=encAlto(544,178),'),
            ('A=520,y=200,D=142,I=108,', 'A=544,y=encH,D=encH-36,I=D-34,'),
            (',(0,u.jsx)("circle",{cx:30,cy:189,r:4,fill:fe}),(0,u.jsx)("text",{x:39,y:192.5,fontSize:"10.5",fontWeight:"600",fill:fe,children:"Esta meta"}),'
             '(0,u.jsx)("rect",{x:104,y:185.5,width:7,height:7,rx:1.5,fill:Yt}),(0,u.jsxs)("text",{x:116,y:192.5,fontSize:"10.5",fill:Yt,children:["Mediana de metas tipo ",R||"0"]})', ''),
        ],
        leyenda='[{k:"dot",c:fe,l:"Esta meta",b:1,t:fe},{k:"sq",c:Yt,l:"Mediana de metas tipo "+(R||"0")}]'),
}


def una_vez(texto: str, viejo: str, nuevo: str, donde: str) -> str:
    assert texto.count(viejo) == 1, f"[{donde}] no se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def ajustar_grafica(html: str, nombre: str, g: dict) -> str:
    i = html.index(f"function {nombre}(")
    j = html.index("function ", i + 10)
    cuerpo = html[i:j]
    for viejo, nuevo in g["cambios"]:
        cuerpo = una_vez(cuerpo, viejo, nuevo, nombre)
    # El svg va dentro de un recuadro que crece con la celda; la leyenda queda debajo.
    inicio = '(0,u.jsxs)("svg",{viewBox:'
    cuerpo = una_vez(cuerpo, inicio,
                     f'(0,u.jsx)("div",{{ref:encRf,className:"enc-graf",style:{{aspectRatio:"{g["ancho"]}/{g["alto"]}"}},children:{inicio}', nombre)
    cuerpo = una_vez(cuerpo, SVG_CLASE, 'className:"enc-svg"', nombre)
    assert cuerpo.endswith(FIN), f"[{nombre}] cierre inesperado"
    cuerpo = cuerpo[:-len(FIN)] + "]})})," + f"encLey({g['leyenda']})" + "]})}"
    return html[:i] + cuerpo + html[j:]


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene las gráficas ajustadas; no se cambia nada.")
        return
    for nombre, g in GRAFICAS.items():
        html = ajustar_grafica(html, nombre, g)
    # Franja gris de los ejes por año: marca el año del corte seleccionado (antes, años alternos fijos).
    html = una_vez(html, "function Sm({cortes:f,X:S,x0:O,x1:R,y0:o,yTop:q})", "function Sm({cortes:f,X:S,x0:O,x1:R,y0:o,yTop:q,sel:encSel})", "Sm")
    html = una_vez(html, 'C%2===1&&(0,u.jsx)("rect"',
                   '(encSel!=null&&encSel>=0?b.startIdx<=encSel&&encSel<=b.endIdx:C===X.length-1)&&(0,u.jsx)("rect"', "Sm")
    html = una_vez(html, "(0,u.jsx)(Sm,{cortes:f,X:G,x0:D,x1:I,y0:k,yTop:B(100)})", "(0,u.jsx)(Sm,{cortes:f,X:G,x0:D,x1:I,y0:k,yTop:B(100),sel:X})", "ix")
    html = una_vez(html, "(0,u.jsx)(Sm,{cortes:f,X:Y,x0:G,x1:B,y0:D,yTop:k(100)})", "(0,u.jsx)(Sm,{cortes:f,X:Y,x0:G,x1:B,y0:D,yTop:k(100),sel:X})", "nx")
    html = una_vez(html, ANCLA_UTILIDADES, UTILIDADES + ANCLA_UTILIDADES, "utilidades")
    html = una_vez(html, CA_VIEJO, CA_NUEVO, "Ca")
    html = una_vez(html, FILA_VIEJA, FILA_NUEVA, "fila")
    html = una_vez(html, "</style>", CSS + "</style>", "css")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Gráficas ajustadas en {PLANTILLA}")


if __name__ == "__main__":
    main()
