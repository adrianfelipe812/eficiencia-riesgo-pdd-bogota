"""Ajuste de la tabla «Metas para focalizar» en tablero/plantilla_foco.html (diseño compilado).

1. Encabezados con el texto completo: Meta producto, Avance de vigencia, Comprometido, Girado,
   Relato y Alerta (antes «Avance», «Comprom.», «Efic.»). La columna de eficiencia se reemplaza
   por «Girado»: porcentaje de recursos girados sobre lo programado del año (pct_giros).
2. Al bajar se quedan visibles el encabezado de la tarjeta («Metas para focalizar» y «Exportar CSV»)
   y, debajo, los títulos de columna: quedan fijos justo debajo del recuadro superior (título y
   filtros), cuyo alto la aplicación ya mide en --filter-bar-h; el del encabezado de la tarjeta se
   mide en --enc-cab-h.
   Para que funcione, la tarjeta recorta con overflow:clip (no crea zona de desplazamiento) y,
   en pantallas medianas y grandes, la tabla deja de tener desplazamiento horizontal propio.
3. Anchos fijos para las columnas de cifras, relato y alerta, para que la meta tenga más espacio.
   Para que los encabezados completos quepan sin cortar columnas: márgenes de celda más compactos
   y, desde 1280 px, la tabla ocupa más ancho frente al panel de detalle (1,45 : 1 en vez de 1,18 : 1).

Como la plantilla es una aplicación compilada, el cambio reemplaza fragmentos exactos. Si la plantilla
ya tiene el ajuste, no hace nada.

    python scripts/ajustar_bandeja.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* bandeja-encabezado-fijo */"

CSS = MARCA + """
.enc-bandeja{overflow:clip}
@media (min-width:640px){.enc-bandeja-tabla{overflow:visible}}
.enc-bandeja-cab{position:sticky;top:0;z-index:6;background:#fff}
.enc-bandeja thead th{position:sticky;top:var(--enc-cab-h,0px);z-index:5;background:#f8fafc;box-shadow:inset 0 -1px 0 #e2e8f0;white-space:normal;vertical-align:bottom;line-height:1.25}
.enc-bandeja thead th button{text-align:right}
.enc-bandeja thead th button span{min-width:0}
.enc-bandeja th:not(:first-child),.enc-bandeja td:not(:first-child){padding-left:6px;padding-right:6px}
.enc-bandeja th:first-child,.enc-bandeja td:first-child{padding-left:14px;padding-right:8px}
.enc-bandeja th:last-child,.enc-bandeja td:last-child{padding-right:14px}
@media (min-width:1280px){.enc-bandeja-grid{grid-template-columns:minmax(0,1.45fr) minmax(0,1fr)}}
.enc-bandeja th:nth-child(2){width:76px}.enc-bandeja th:nth-child(3){width:76px}.enc-bandeja th:nth-child(4){width:68px}
.enc-bandeja th:nth-child(5){width:94px}.enc-bandeja th:nth-child(6){width:70px}
.enc-bandeja thead th span{-webkit-hyphens:auto;hyphens:auto}
.enc-bandeja thead th button{gap:3px}
.enc-bandeja td:nth-child(5) .font-medium{line-height:1.35}
@media (min-width:768px){.enc-bandeja-cab{top:var(--filter-bar-h,0px)}.enc-bandeja thead th{top:calc(var(--filter-bar-h,0px) + var(--enc-cab-h,0px))}}
"""

CAMBIOS = [
    # Se mide el alto del encabezado de la tarjeta para fijar los títulos de columna justo debajo.
    ('let T=(0,$.useRef)(null),z=Math.max(1,Math.ceil(o.length/Fu))',
     'let T=(0,$.useRef)(null),encCab=(0,$.useRef)(null),z=Math.max(1,Math.ceil(o.length/Fu))'),
    ('"aria-hidden":"true"});return(0,u.jsxs)("div",{className:"grid grid-cols-1 items-start gap-5 xl:grid-cols-[minmax(0,1.18fr)_minmax(0,1fr)]"',
     '"aria-hidden":"true"});(0,$.useLayoutEffect)(()=>{let e=encCab.current;if(!e)return;'
     'let f=()=>e.parentElement&&e.parentElement.style.setProperty("--enc-cab-h",Math.ceil(e.getBoundingClientRect().height)+"px");'
     'if(f(),typeof ResizeObserver>"u")return;let r=new ResizeObserver(f);return r.observe(e),()=>r.disconnect()});'
     'return(0,u.jsxs)("div",{className:"grid grid-cols-1 items-start gap-5 xl:grid-cols-[minmax(0,1.18fr)_minmax(0,1fr)]"'),
    # Más ancho para la tabla frente al panel de detalle (en pantallas de 1280 px o más).
    ('"grid grid-cols-1 items-start gap-5 xl:grid-cols-[minmax(0,1.18fr)_minmax(0,1fr)]",children:[(0,u.jsxs)("section",{className:"overflow-hidden rounded-xl',
     '"enc-bandeja-grid grid grid-cols-1 items-start gap-5 xl:grid-cols-[minmax(0,1.18fr)_minmax(0,1fr)]",children:[(0,u.jsxs)("section",{className:"overflow-hidden rounded-xl'),
    # Tarjeta y contenedor de la tabla.
    ('(0,u.jsxs)("section",{className:"overflow-hidden rounded-xl border border-slate-200/85 bg-white",children:[(0,u.jsxs)("div",{className:"flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4",children:[(0,u.jsxs)("div",{children:[(0,u.jsx)("h2",{className:"font-display text-base font-semibold text-slate-900",children:"Metas para focalizar"})',
     '(0,u.jsxs)("section",{className:"enc-bandeja rounded-xl border border-slate-200/85 bg-white",children:[(0,u.jsxs)("div",{ref:encCab,className:"enc-bandeja-cab flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4",children:[(0,u.jsxs)("div",{children:[(0,u.jsx)("h2",{className:"font-display text-base font-semibold text-slate-900",children:"Metas para focalizar"})'),
    ('(0,u.jsx)("div",{className:"overflow-x-auto",children:(0,u.jsxs)("table",{className:"w-full border-collapse text-left text-xs",children:[(0,u.jsx)("thead",{className:"border-b border-slate-200 bg-slate-50/80 text-[11px] font-semibold text-slate-600",children:(0,u.jsxs)("tr",{children:[(0,u.jsx)("th",{className:"px-4 py-3",children:"Meta producto"})',
     '(0,u.jsx)("div",{className:"enc-bandeja-tabla overflow-x-auto",children:(0,u.jsxs)("table",{className:"w-full border-collapse text-left text-xs",children:[(0,u.jsx)("thead",{className:"border-b border-slate-200 bg-slate-50/80 text-[11px] font-semibold text-slate-600",children:(0,u.jsxs)("tr",{children:[(0,u.jsx)("th",{className:"px-4 py-3",children:"Meta producto"})'),
    # Texto completo de los encabezados.
    ('onClick:()=>G("av"),className:"inline-flex items-center gap-1 hover:text-red-800",children:[(0,u.jsx)("span",{children:"Avance"})',
     'onClick:()=>G("av"),className:"inline-flex items-center gap-1 hover:text-red-800",children:[(0,u.jsx)("span",{children:"Avance de vigencia"})'),
    # Metas sin recursos comprometidos (regla «sc» de generar_tablero.py): «Sin alerta / sin compromiso».
    ('(0,u.jsx)("div",{className:"font-mono-tabular mt-0.5 text-[11px] text-slate-400",children:"0 %"})',
     '(0,u.jsx)("div",{className:"mt-0.5 text-[11px] text-slate-400",children:ot.sc?"sin compromiso":"0 %"})'),
    # Guion opcional (\xAD): «Compro-metido» solo se parte cuando la columna es angosta.
    ('(0,u.jsx)("span",{children:"Comprom."})', '(0,u.jsx)("span",{children:"Compro\\xADmetido"})'),
    # La columna «Eficiencia» se reemplaza por «Girado»: recursos girados ÷ programados del año (pct_giros).
    ('onClick:()=>G("ef"),className:"inline-flex items-center gap-1 hover:text-red-800",children:[(0,u.jsx)("span",{children:"Efic."}),$t("ef")]',
     'onClick:()=>G("pg"),className:"inline-flex items-center gap-1 hover:text-red-800",children:[(0,u.jsx)("span",{children:"Girado"}),$t("pg")]'),
    ('font-medium text-slate-700 whitespace-nowrap",children:jn(ot.ef)})', 'font-medium text-slate-700 whitespace-nowrap",children:Ne(ot.pg)})'),
]


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene la bandeja ajustada; no se cambia nada.")
        return
    for viejo, nuevo in CAMBIOS:
        html = una_vez(html, viejo, nuevo)
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Bandeja ajustada en {PLANTILLA}")


if __name__ == "__main__":
    main()
