"""Uso cómodo desde el celular (Android e iOS) en tablero/plantilla_foco.html (diseño compilado).

En pantallas angostas:
  - Menú: las cuatro vistas pasan a una barra fija abajo (como las apps), con espacio para la barra
    de gestos del iPhone. El logo queda arriba y la zona de descargas al final de la página.
  - Encabezado: modo oscuro, fecha de corte y «Filtros» en una sola fila que no se desborda.
  - Tablas («Metas para focalizar» y «Actividades registradas»): cada fila se muestra como una tarjeta,
    con la etiqueta de cada dato; no hay desplazamiento lateral ni encabezados fijos (en el celular
    ocupan demasiado). Lo mismo para la cabecera del detalle de la meta.
  - Gráfica de actividades: se abre al tocar la fila y aparece como panel inferior, con botón de cerrar.
  - iOS: los campos usan letra de 16 px para que el teléfono no acerque la página al tocarlos.

Va después de todos los demás ajustes (usa piezas de ajustar_actividades.py y ajustar_tema.py). Si la
plantilla ya tiene el ajuste, no hace nada.

    python scripts/ajustar_movil.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* uso-movil */"

O = "html.enc-oscuro"
ETIQUETAS_BANDEJA = ["Avance de vigencia", "Comprometido", "Girado", "Relato", "Alerta"]
ETIQUETAS_ACTIVIDADES = ["Programado", "Entregado", "% entregado", "Recursos", "Comprometido", "Girado", "Estado"]
antes = lambda tabla, etiquetas, desde: "\n".join(
    f'  .{tabla} tbody td:nth-child({i})::before{{content:"{e}"}}' for i, e in enumerate(etiquetas, desde))

CSS = MARCA + f"""
@media (max-width:1023px){{
  .enc-lateral{{display:contents}}
  .enc-lateral>div:first-child{{order:1;background:#fff;border-bottom:1px solid #e2e8f0}}
  .enc-lateral~main{{order:2;padding-bottom:calc(84px + env(safe-area-inset-bottom))}}
  .enc-lateral>div:last-child{{display:block!important;order:3;background:#fff;border-top:1px solid #e2e8f0;padding-bottom:calc(92px + env(safe-area-inset-bottom))}}
  .enc-lateral nav{{position:fixed;left:0;right:0;bottom:0;z-index:50;margin:0!important;display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:2px;padding:6px 6px calc(6px + env(safe-area-inset-bottom));overflow:visible!important;background:rgba(255,255,255,.97);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-top:1px solid #e2e8f0;box-shadow:0 -6px 20px -12px rgba(15,23,42,.25)}}
  .enc-lateral nav button{{flex-direction:column;justify-content:center;gap:3px;min-height:52px;padding:6px 2px!important;width:auto}}
  .enc-lateral nav button>span{{text-align:center}}
  .enc-lateral nav button>span>span:first-child{{font-size:11px;white-space:normal;line-height:1.15}}
  .enc-lateral nav button svg{{width:20px;height:20px}}
}}
@media (max-width:767px){{
  input,select,textarea{{font-size:16px!important}}
  .enc-filtros{{display:grid!important;grid-template-columns:auto minmax(0,1fr) auto;align-items:end;gap:.5rem}}
  .enc-corte{{width:auto;min-width:0}}
  .enc-corte button{{min-width:0}}
  .enc-corte button span{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .enc-bandeja-cab,.enc-acts-cab,.enc-det-cab,.enc-bandeja thead th,.enc-acts thead th{{position:static!important}}
}}
@media (max-width:419px){{ .enc-boton>span:not(.enc-num){{display:none}} }}
@media (max-width:639px){{
  .enc-bandeja table,.enc-bandeja tbody,.enc-acts table,.enc-acts tbody{{display:block}}
  .enc-bandeja thead,.enc-acts thead{{display:none}}
  .enc-bandeja-tabla,.enc-acts-tabla{{overflow:visible!important}}
  .enc-bandeja tbody tr,.enc-acts tbody tr{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.625rem .75rem;padding:.875rem 1rem}}
  .enc-bandeja tbody td,.enc-acts tbody td{{display:block;max-width:none;padding:0!important;text-align:left!important;white-space:normal}}
  .enc-bandeja tbody td::before,.enc-acts tbody td::before{{display:block;margin-bottom:2px;font-size:10.5px;font-weight:500;color:#64748b}}
  .enc-bandeja tbody td:first-child,.enc-acts tbody td:first-child,.enc-acts tbody td:nth-child(2),.enc-acts tbody td:nth-child(9){{grid-column:1/-1}}
  .enc-bandeja tbody td:first-child::before,.enc-acts tbody td:first-child::before,.enc-acts tbody td:nth-child(2)::before{{content:none}}
  .enc-bandeja tbody td:nth-child(5){{grid-column:span 2}}
  .enc-bandeja tbody td .ml-auto{{margin-left:0}}
  .enc-bandeja tbody td[colspan],.enc-acts tbody td[colspan]{{grid-column:1/-1}}
  .enc-bandeja tbody td[colspan]::before,.enc-acts tbody td[colspan]::before{{content:none}}
{antes("enc-bandeja", ETIQUETAS_BANDEJA, 2)}
{antes("enc-acts", ETIQUETAS_ACTIVIDADES, 3)}
}}
.enc-pop-movil{{pointer-events:auto;max-height:65vh;overflow:auto}}
.enc-pop-cerrar{{position:absolute;top:4px;right:6px;width:36px;height:36px;border:0;border-radius:.5rem;background:transparent;color:#64748b;font-size:22px;line-height:1;cursor:pointer}}
@media (max-width:1023px){{
  {O} .enc-lateral>div:first-child,{O} .enc-lateral>div:last-child{{background:#262624;border-color:#3a3936}}
  {O} .enc-lateral nav{{background:rgba(38,38,36,.97);border-top-color:#3a3936}}
}}
{O} .enc-bandeja tbody td::before,{O} .enc-acts tbody td::before{{color:#a29e96}}
{O} .enc-pop-cerrar{{color:#a29e96}}
"""

CAMBIOS = [
    # Gráfica de actividades: en el celular, panel inferior con botón de cerrar.
    ('function encActGraf({h,cut:c}){', 'function encActGraf({h,cut:c,onClose:oc}){'),
    ('L=h.x+18+PW>vw?Math.max(8,h.x-18-PW):h.x+18,Tp=Math.min(Math.max(8,h.y-PH/2),Math.max(8,vh-PH-8));',
     'L=h.x+18+PW>vw?Math.max(8,h.x-18-PW):h.x+18,Tp=Math.min(Math.max(8,h.y-PH/2),Math.max(8,vh-PH-8)),mv=vw<640;'),
    ('className:"enc-pop",role:"tooltip",style:{left:L,top:Tp,width:PW},children:[',
     'className:`enc-pop${mv?" enc-pop-movil":""}`,role:mv?"dialog":"tooltip",'
     'style:mv?{left:8,right:8,bottom:"calc(92px + env(safe-area-inset-bottom))",width:"auto"}:{left:L,top:Tp,width:PW},children:['
     'mv&&(0,u.jsx)("button",{type:"button",className:"enc-pop-cerrar","aria-label":"Cerrar gr\\xE1fica",onClick:oc,children:"\\xD7"}),'),
    ('encHv&&(0,u.jsx)(encActGraf,{h:encHv,cut:f})', 'encHv&&(0,u.jsx)(encActGraf,{h:encHv,cut:f,onClose:()=>encSetHv(null)})'),
    # Tocar una fila también abre la gráfica (en pantallas táctiles no hay cursor).
    # En pantallas táctiles (sin cursor) no se abre al «pasar por encima», solo al tocar.
    ('onMouseEnter:T=>encSetHv({r:B,x:T.clientX,y:T.clientY}),onMouseMove:T=>encSetHv({r:B,x:T.clientX,y:T.clientY}),',
     'onClick:T=>encSetHv({r:B,x:T.clientX,y:T.clientY}),'
     'onMouseEnter:T=>{encTactil()||encSetHv({r:B,x:T.clientX,y:T.clientY})},onMouseMove:T=>{encTactil()||encSetHv({r:B,x:T.clientX,y:T.clientY})},'),
    ('onMouseLeave:()=>encSetHv(null),children:ft.length', 'onMouseLeave:()=>{encTactil()||encSetHv(null)},children:ft.length'),
    ('function encActGraf(', 'function encTactil(){return typeof window<"u"&&!!window.matchMedia&&window.matchMedia("(hover: none)").matches}function encActGraf('),
]

# Ajuste del viewport para iPhone (zona segura alrededor de la barra de gestos).
VIEWPORT_VIEJO = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
VIEWPORT_NUEVO = '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />'


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene el ajuste para celular; no se cambia nada.")
        return
    for viejo, nuevo in CAMBIOS:
        html = una_vez(html, viejo, nuevo)
    html = una_vez(html, VIEWPORT_VIEJO, VIEWPORT_NUEVO)
    html = una_vez(html, "</style>", CSS + "</style>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Ajuste para celular agregado en {PLANTILLA}")


if __name__ == "__main__":
    main()
