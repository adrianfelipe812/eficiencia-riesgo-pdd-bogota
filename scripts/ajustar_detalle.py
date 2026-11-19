"""Ajuste del detalle de la meta (panel junto a la bandeja) en tablero/plantilla_foco.html.

1. Se quitan las tarjetas «Eficiencia (0 a 1)», «Dinero vs. avance» y «Riesgo de rezago».
   El riesgo sigue a la vista en la cabecera de la meta («Alerta alta (92,9 % riesgo)») y en
   el recuadro «Por qué este riesgo».
2. «Avance del año» pasa a llamarse «Avance de vigencia».
3. Seis tarjetas centradas en dos filas de tres: arriba los avances (vigencia, transcurrido y
   cuatrienio) y abajo el dinero y las entregas (% Comprometido, % Girado y Sin entrega).
   % Girado es nueva: recursos girados ÷ programados del año (pct_giros). Sin dato se muestra 0 %
   (con semáforo gris).
4. Semáforo en el número y la barra de cada tarjeta. Se compara el valor con lo esperado al corte
   si el avance fuera lineal en el tiempo (el Plan se cuenta desde enero de 2024, cuatro años):
     - Avance de vigencia, % Comprometido y % Girado: esperado = parte del año transcurrida
       (marzo 25 %, junio 50 %, septiembre 75 %, diciembre 100 %).
     - Transcurrido: esperado = meses desde enero de 2024 ÷ meses hasta el cierre del año del corte.
     - Cuatrienio: esperado = meses desde enero de 2024 ÷ 48.
   Verde: 90 % o más de lo esperado · Ámbar: entre 60 % y 90 % · Rojo: menos de 60 %.
   Sin entrega: verde si ninguna actividad programada quedó sin entrega, ámbar si menos de la
   mitad, rojo si la mitad o más. Sin dato: gris.
5. La nota de abajo ya no habla de eficiencia; conserva la explicación del riesgo.
6. Se quita el recuadro «Por qué este riesgo».
7. Primero van los relatos de entidad (retrasos, avances y logros) y abajo la gráfica de evolución,
   que ahora muestra «Avance de vigencia» y «Dinero comprometido» como dos gráficas separadas, una
   debajo de la otra y cada una a todo el ancho.
8. La cabecera de la meta (código, nombre, rezago/alerta, actividades y «Ver actividades») queda fija
   al bajar por el detalle, justo debajo del recuadro superior.
9. Si la meta no registra recursos comprometidos (regla «sc» de generar_tablero.py), la cabecera dice
   «Sin alerta: no registra recursos comprometidos».

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_detalle.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* detalle-meta-tarjetas */"

CSS = MARCA + """
.enc-met{display:grid;grid-template-columns:repeat(6,minmax(0,1fr))}
.enc-met-c{grid-column:span 2;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:.375rem;min-width:0;padding:.875rem .75rem;text-align:center;border-right:1px solid #f1f5f9}
.enc-met-c:nth-child(3n){border-right:0}
.enc-met-c:nth-child(n+4){border-top:1px solid #f1f5f9}
.enc-met-l{font-size:11px;font-weight:500;line-height:1.3;color:#64748b}
.enc-met-v{font-size:1.125rem;font-weight:600;line-height:1.2;white-space:nowrap}
.enc-met-bar{width:100%;max-width:150px;height:6px;border-radius:999px;background:#f1f5f9;overflow:hidden}
.enc-met-bar i{display:block;height:100%;border-radius:999px;background:currentColor}
.enc-sem-v{color:#047857}.enc-sem-a{color:#b45309}.enc-sem-r{color:#b91c1c}.enc-sem-n{color:#475569}
.enc-sem-n .enc-met-bar i{background:#94a3b8}
.enc-met-ley{display:flex;flex-wrap:wrap;justify-content:center;gap:.25rem .875rem;font-size:11px;line-height:1.4;color:#64748b}
.enc-met-ley span{display:inline-flex;align-items:center;gap:.3rem;white-space:nowrap}
.enc-met-ley i{display:inline-block;width:8px;height:8px;border-radius:50%;background:currentColor}
"""

# Componente de tarjetas con semáforo (se inserta antes del panel de detalle, función sx).
COMPONENTE = (
    'function encSem(v,e){if(v==null||Number.isNaN(v)||e==null||e<=0)return"n";let r=v/e;return r>=.9?"v":r>=.6?"a":"r"}'
    'function encMetas({f,cut:c}){let m=Number(c.slice(5,7)),y=Number(c.slice(0,4)),t=(y-2024)*12+m,'
    'eA=m/12*100,eT=Math.min(100,t/((y-2024+1)*12)*100),eC=Math.min(100,t/48*100),'
    'sE=(f.na??0)>0?(f.nz??0)===0?"v":(f.nz??0)/f.na<.5?"a":"r":"n",'
    'it=[{l:"Avance de vigencia",v:Ne(f.av),b:f.av,s:encSem(f.av,eA)},{l:"Transcurrido",v:Ne(f.at),b:f.at,s:encSem(f.at,eT)},'
    '{l:"Cuatrienio",v:Ne(f.ap),b:f.ap,s:encSem(f.ap,eC)},{l:"% Comprometido",v:Ne(f.pc),b:f.pc??0,s:encSem(f.pc,eA)},'
    '{l:"% Girado",v:Ne(f.pg),b:f.pg??0,s:encSem(f.pg,eA)},'
    '{l:"Sin entrega",v:`${f.nz??0} de ${f.na??0}`,b:null,s:sE}];'
    'return(0,u.jsxs)(u.Fragment,{children:['
    '(0,u.jsx)("div",{className:"enc-met -mx-5 -mt-5 border-b border-slate-100",children:it.map(x=>(0,u.jsxs)("div",{className:`enc-met-c enc-sem-${x.s}`,children:['
    '(0,u.jsx)("div",{className:"enc-met-l",children:x.l}),(0,u.jsx)("div",{className:"enc-met-v font-mono-tabular",children:x.v}),'
    'x.b!=null&&(0,u.jsx)("div",{className:"enc-met-bar",children:(0,u.jsx)("i",{style:{width:`${Math.max(0,Math.min(100,x.b))}%`}})})]},x.l))}),'
    '(0,u.jsxs)("div",{className:"enc-met-ley",title:`Esperado al corte si el avance fuera lineal: vigencia, comprometido y girado ${ce(eA)} %, transcurrido ${ce(eT)} %, cuatrienio ${ce(eC)} %.`,children:['
    '(0,u.jsx)("span",{children:"Frente a lo esperado al corte:"}),'
    '(0,u.jsxs)("span",{className:"enc-sem-v",children:[(0,u.jsx)("i",{}),(0,u.jsx)("b",{className:"font-medium text-slate-600",children:"al d\\xEDa (\\u2265 90 %)"})]}),'
    '(0,u.jsxs)("span",{className:"enc-sem-a",children:[(0,u.jsx)("i",{}),(0,u.jsx)("b",{className:"font-medium text-slate-600",children:"algo atrasada (60\\u201390 %)"})]}),'
    '(0,u.jsxs)("span",{className:"enc-sem-r",children:[(0,u.jsx)("i",{}),(0,u.jsx)("b",{className:"font-medium text-slate-600",children:"atrasada (< 60 %)"})]})]})]})}'
)
ANCLA_COMPONENTE = "function sx({meta:f,"

TARJETAS_VIEJAS = (
    '(0,u.jsxs)("div",{className:"-mx-5 -mt-5 grid grid-cols-2 divide-x divide-y divide-slate-100 border-b border-slate-100 sm:grid-cols-4",children:['
    '(0,u.jsx)(ta,{label:"Avance del a\\xF1o",value:Ne(f.av),barPercent:f.av,tone:f.rz===1?"red":"teal"}),'
    '(0,u.jsx)(ta,{label:"Transcurrido",value:Ne(f.at),barPercent:f.at}),'
    '(0,u.jsx)(ta,{label:"Cuatrienio",value:Ne(f.ap),barPercent:f.ap}),'
    '(0,u.jsx)(ta,{label:"% Comprometido",value:Ne(f.pc),barPercent:f.pc}),'
    '(0,u.jsx)(ta,{label:"Eficiencia (0 a 1)",value:jn(f.ef),barPercent:f.ef!=null?f.ef*100:null}),'
    '(0,u.jsx)(ta,{label:"Dinero vs. avance",value:`${jn(f.br)} pts`}),'
    '(0,u.jsx)(ta,{label:"Sin entrega",value:`${f.nz??0} de ${f.na??0}`}),'
    '(0,u.jsx)(ta,{label:"Riesgo de rezago",value:Ne(f.pr!=null?f.pr*100:0),barPercent:f.pr!=null?f.pr*100:0,tone:"red"})]}),'
)
TARJETAS_NUEVAS = '(0,u.jsx)(encMetas,{f:f,cut:O}),'

NOTA_VIEJA = ('(0,u.jsxs)("p",{className:"text-xs leading-relaxed text-slate-500",children:[f.ef==null?"Sin puntaje de eficiencia: grupo sin suficientes comparables o sin recursos comprometidos.":`Eficiencia medida frente a: ${f.gd}.`," ",f.pr!=null&&"El riesgo')
NOTA_NUEVA = 'f.pr!=null&&(0,u.jsxs)("p",{className:"text-xs leading-relaxed text-slate-500",children:["El riesgo'

# Se quita el recuadro «Por qué este riesgo».
POR_QUE = ('f.ex&&(0,u.jsxs)("div",{className:"rounded-lg bg-amber-50/55 p-4",children:[(0,u.jsx)("div",{className:"text-xs font-semibold text-amber-950",children:"Por qu\\xE9 este riesgo"}),'
           '(0,u.jsx)("p",{className:"mt-1 text-xs leading-relaxed text-slate-800",children:f.ex}),'
           '(0,u.jsx)("p",{className:"mt-1.5 text-[11px] text-slate-500",children:"Tres variables con mayor aporte en el modelo (SHAP). Explican el puntaje, no causalidad directa."})]}),')

# Primero los relatos y abajo la gráfica de evolución: el contenedor pasa a columna flexible y la
# gráfica (envuelta en .enc-det-graf) se ordena al final.
CONTENEDOR_VIEJO = '(0,u.jsxs)("div",{className:"p-5 space-y-5",children:[(0,u.jsx)(encMetas'
CONTENEDOR_NUEVO = '(0,u.jsxs)("div",{className:"enc-det p-5 space-y-5",children:[(0,u.jsx)(encMetas'
GRAFICA_VIEJA = '(0,u.jsx)(nx,{cortes:b,metaSeries:C,grupoSeries:J,tipo:f.ti,corteActual:O}),'
GRAFICA_NUEVA = '(0,u.jsx)("div",{className:"enc-det-graf",children:(0,u.jsx)(nx,{cortes:b,metaSeries:C,grupoSeries:J,tipo:f.ti,corteActual:O})}),'

# Gráfica de evolución: los dos paneles (avance y dinero) dejan de compartir un solo dibujo; cada
# uno ocupa todo el ancho, uno debajo del otro. (Requiere scripts/ajustar_graficas.py antes.)
PANELES_VIEJOS = ('(0,u.jsx)("div",{ref:encRf,className:"enc-graf",style:{aspectRatio:"544/178"},children:(0,u.jsxs)("svg",{viewBox:`0 0 ${A} ${y}`,className:"enc-svg",role:"img","aria-label":J,'
                  'children:[ft(26,232,"Avance f\\xEDsico del a\\xF1o (%)",S.av,O.av),ft(280,484,"Dinero comprometido (%)",S.pc,O.pc)]})})')
PANELES_NUEVOS = ('(0,u.jsx)("div",{ref:encRf,className:"enc-graf",style:{aspectRatio:"544/178"},children:(0,u.jsx)("svg",{viewBox:`0 0 ${A} ${y}`,className:"enc-svg",role:"img","aria-label":"Avance de vigencia (%)",'
                  'children:ft(34,494,"Avance de vigencia (%)",S.av,O.av)})}),'
                  '(0,u.jsx)("div",{className:"enc-graf enc-graf-2",style:{aspectRatio:"544/178"},children:(0,u.jsx)("svg",{viewBox:`0 0 ${A} ${y}`,className:"enc-svg",role:"img","aria-label":"Dinero comprometido (%)",'
                  'children:ft(34,494,"Dinero comprometido (%)",S.pc,O.pc)})})')
SUBTITULO_VIEJO = 'subtitle:"Misma escala en ambos paneles. Las cifras anuales se reinician en enero."'
SUBTITULO_NUEVO = 'subtitle:"Misma escala en ambas gr\\xE1ficas. Las cifras anuales se reinician en enero."'

CSS_ORDEN = """
.enc-det{display:flex;flex-direction:column}
.enc-det>.enc-det-graf{order:10;margin-top:1.25rem;margin-bottom:0!important}
.enc-graf-2{margin-top:1.25rem}
"""

# Cabecera de la meta (código, nombre, rezago/alerta y «Ver actividades») fija al bajar por el detalle.
CABECERA_VIEJA = '(0,u.jsxs)("div",{className:"border-b border-slate-100 p-5",children:[(0,u.jsxs)("div",{className:"flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500",children:[(0,u.jsxs)("span",{className:"font-mono-tabular font-semibold text-red-800",children:["Meta ",f.i]})'
CABECERA_NUEVA = '(0,u.jsxs)("div",{className:"enc-det-cab border-b border-slate-100 p-5",children:[(0,u.jsxs)("div",{className:"flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500",children:[(0,u.jsxs)("span",{className:"font-mono-tabular font-semibold text-red-800",children:["Meta ",f.i]})'
CSS_CABECERA = """
.enc-det-cab{position:sticky;top:0;z-index:7;background:#fff;border-radius:.75rem .75rem 0 0}
@media (min-width:768px){.enc-det-cab{top:var(--filter-bar-h,0px)}}
"""
# Metas sin recursos comprometidos (regla «sc» de generar_tablero.py): se explica por qué no hay alerta.
ESTADO_VIEJO = '(f.rz===1||f.nv)&&(0,u.jsxs)("div",{className:"mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs",children:[f.rz===1&&'
ESTADO_NUEVO = '(f.rz===1||f.nv||f.sc)&&(0,u.jsxs)("div",{className:"mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs",children:[f.rz===1&&'
ESTADO_FIN_VIEJO = '"(",Ne(f.pr*100)," riesgo)"]})]})]}),(0,u.jsxs)("div",{className:"mt-4 flex'
ESTADO_FIN_NUEVO = ('"(",Ne(f.pr*100)," riesgo)"]})]}),'
                    'f.sc&&(0,u.jsx)("span",{className:"text-slate-500",title:"No registra recursos comprometidos en el a\\xF1o ni en vigencias futuras.",'
                    'children:(f.rz===1?"\\xB7 ":"")+"Sin alerta: no registra recursos comprometidos"})]}),(0,u.jsxs)("div",{className:"mt-4 flex')


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene el detalle ajustado; no se cambia nada.")
        return
    html = una_vez(html, TARJETAS_VIEJAS, TARJETAS_NUEVAS)
    html = una_vez(html, NOTA_VIEJA, NOTA_NUEVA)
    html = una_vez(html, POR_QUE, "")
    html = una_vez(html, CONTENEDOR_VIEJO, CONTENEDOR_NUEVO)
    html = una_vez(html, GRAFICA_VIEJA, GRAFICA_NUEVA)
    html = una_vez(html, PANELES_VIEJOS, PANELES_NUEVOS)
    html = una_vez(html, SUBTITULO_VIEJO, SUBTITULO_NUEVO)
    html = una_vez(html, CABECERA_VIEJA, CABECERA_NUEVA)
    html = una_vez(html, ESTADO_VIEJO, ESTADO_NUEVO)
    html = una_vez(html, ESTADO_FIN_VIEJO, ESTADO_FIN_NUEVO)
    html = una_vez(html, ANCLA_COMPONENTE, COMPONENTE + ANCLA_COMPONENTE)
    html = una_vez(html, "</style>", CSS + CSS_ORDEN + CSS_CABECERA + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Detalle de la meta ajustado en {PLANTILLA}")


if __name__ == "__main__":
    main()
