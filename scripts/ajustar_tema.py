"""Modo oscuro activable y desactivable en tablero/plantilla_foco.html (diseño compilado).

Un botón con luna / sol a la izquierda de «Fecha de corte» activa o desactiva el modo oscuro. La elección
se recuerda en el navegador (localStorage «focoTema»); por defecto el tablero abre en modo claro.

Paleta oscura: fondos cálidos tomados del tema oscuro de Claude (#1f1e1d página, #262624 tarjetas,
#30302e campos) y textos claros; se conservan los colores de la entidad (rojo institucional, ámbar,
verde azulado, azul), aclarados lo necesario para que se lean sobre fondo oscuro.

Cómo funciona: la clase «enc-oscuro» en <html> redefine las variables de color de Tailwind (grises
invertidos y tonos de la entidad) y sobrescribe los colores fijos de las piezas propias y de las
gráficas SVG. Se aplica antes de pintar la página para que no parpadee.

Va después de los demás ajustes (encabezado, tarjetas, gráficas, bandeja, detalle, actividades y
descargas). Si la plantilla ya tiene el ajuste, no hace nada.

    python scripts/ajustar_tema.py
"""
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parents[1] / "tablero" / "plantilla_foco.html"
MARCA = "/* modo-oscuro */"

O = "html.enc-oscuro"
CSS = MARCA + f"""
.enc-tema{{display:inline-flex;align-items:center;justify-content:center;width:2.5rem;height:2.5rem;flex-shrink:0;border:1px solid #e2e8f0;border-radius:.5rem;background:#fff;color:#475569;cursor:pointer;transition:background-color .15s,border-color .15s,color .15s}}
.enc-tema:hover{{border-color:#cbd5e1;background:#f8fafc;color:#0f172a}}
.enc-tema svg{{width:1rem;height:1rem}}
{O}{{color-scheme:dark;
  --color-slate-50:#2b2a28;--color-slate-100:#34332f;--color-slate-200:#3a3936;--color-slate-300:#4a4844;
  --color-slate-400:#8a867e;--color-slate-500:#a29e96;--color-slate-600:#bcb8b0;--color-slate-700:#d3cfc7;
  --color-slate-800:#e4e1da;--color-slate-900:#f0eee9;
  --color-red-50:#3a2120;--color-red-100:#4a2523;--color-red-200:#6b2b28;--color-red-300:#8f3330;
  --color-red-700:#d84040;--color-red-800:#f07272;--color-red-900:#f8a5a5;
  --color-amber-50:#3a2f1c;--color-amber-200:#5c4520;--color-amber-300:#7a5a22;--color-amber-600:#d99a2b;
  --color-amber-700:#e9a93c;--color-amber-800:#f2bf5c;--color-amber-900:#f6cf80;--color-amber-950:#f8d99a;
  --color-teal-50:#18302d;--color-teal-100:#1d3a36;--color-teal-200:#265049;--color-teal-700:#2bb3a0;
  --color-teal-800:#5fd1c0;--color-teal-900:#8fe0d3;
  --color-sky-50:#182a36;--color-sky-200:#23465b;--color-sky-600:#38a3e0;--color-sky-800:#8fd0f5}}
{O} body,{O} .bg-\\[\\#f7f8fa\\]{{background-color:#1f1e1d!important}}
{O} .bg-white,{O} .hover\\:bg-white:hover,{O} .focus\\:bg-white:focus,{O} .disabled\\:hover\\:bg-white:disabled:hover{{background-color:#262624}}
{O} aside img{{background:#fff;border-radius:.5rem;padding:.375rem}}
{O} .enc-tema{{background:#262624;border-color:#3a3936;color:#f2bf5c}}
{O} .enc-tema:hover{{background:#30302e;border-color:#4a4844;color:#f6cf80}}
/* Encabezado y filtros */
{O} .enc-fijo{{background:rgba(31,30,29,.95)}}
{O} .enc-caja,{O} .enc-panel{{background:#262624;border-color:#3a3936}}
{O} .enc-panel{{box-shadow:0 16px 40px -12px rgba(0,0,0,.6)}}
{O} .enc-boton,{O} .enc-sec{{background:#262624;border-color:#3a3936;color:#d3cfc7}}
{O} .enc-boton:hover,{O} .enc-sec:hover:not(:disabled){{background:#30302e;border-color:#4a4844;color:#f0eee9}}
{O} .enc-boton.activo{{background:#3a2120;border-color:#8f3330;color:#f8a5a5}}
{O} .enc-acciones{{border-top-color:#34332f}}
/* Tarjetas del Panorama */
{O} .kpi{{background:#262624;border-color:#3a3936}}
{O} button.kpi:hover:not(:disabled){{border-color:#4a4844}}
{O} .kpi-l,{O} .kpi-s{{color:#a29e96}}
{O} .kpi-slate .kpi-n{{color:#f0eee9}}{O} .kpi-slate svg{{color:#8a867e}}
{O} .kpi-teal .kpi-n{{color:#5fd1c0}}{O} .kpi-teal svg{{color:#2bb3a0}}
{O} .kpi-indigo .kpi-n{{color:#a5b4fc}}{O} .kpi-indigo svg{{color:#818cf8}}
{O} .kpi-sky .kpi-n{{color:#8fd0f5}}{O} .kpi-sky svg{{color:#38a3e0}}
{O} .kpi-amber .kpi-n{{color:#f2bf5c}}{O} .kpi-amber svg{{color:#e9a93c}}
{O} .kpi-red .kpi-n,{O} .kpi-red svg{{color:#f07272}}
/* Tablas con encabezado fijo */
{O} .enc-bandeja-cab,{O} .enc-acts-cab,{O} .enc-det-cab{{background:#262624}}
{O} .enc-bandeja thead th,{O} .enc-acts thead th{{background:#2b2a28;box-shadow:inset 0 -1px 0 #3a3936}}
/* Detalle de la meta: tarjetas con semáforo */
{O} .enc-met-c{{border-color:#34332f}}
{O} .enc-met-l{{color:#a29e96}}
{O} .enc-met-bar{{background:#34332f}}
{O} .enc-sem-v{{color:#34c58f}}{O} .enc-sem-a{{color:#e9a93c}}{O} .enc-sem-r{{color:#f07272}}{O} .enc-sem-n{{color:#bcb8b0}}
{O} .enc-sem-n .enc-met-bar i{{background:#6b6862}}
{O} .enc-met-ley,{O} .enc-ley{{color:#a29e96}}
{O} .enc-met-ley b{{color:#bcb8b0}}
/* Gráfica emergente de actividades */
{O} .enc-pop{{background:#262624;border-color:#3a3936;box-shadow:0 16px 40px -12px rgba(0,0,0,.7)}}
{O} .enc-pop-cab,{O} .enc-pop-sub,{O} .enc-pop-ley{{color:#a29e96}}
{O} .enc-pop-meta{{color:#f07272}}
{O} .enc-pop-tit,{O} .enc-pop-tot b{{color:#f0eee9}}
{O} .enc-pop-tot{{color:#d3cfc7}}
{O} .enc-pop-ley i[style*="203, 213, 225"]{{background:#6b6862!important}}
/* Descargas de la barra lateral */
{O} .enc-desc{{border-bottom-color:#34332f}}
{O} .enc-desc-tit,{O} .enc-desc-lbl,{O} .enc-desc-sdp{{color:#a29e96}}
{O} .enc-desc-sel{{background:#30302e;border-color:#3a3936;color:#f0eee9}}
{O} .enc-desc-btn{{background:#2b2a28;border-color:#3a3936;color:#d3cfc7}}
{O} .enc-desc-btn:hover{{background:#3a2120;border-color:#8f3330;color:#f8a5a5}}
{O} .enc-desc-btn small,{O} .enc-desc-vacio{{color:#8a867e}}
/* Gráficas SVG: colores fijos de ejes, textos, rejillas y puntos */
{O} svg [fill="#0f172a"]{{fill:#f0eee9}}
{O} svg [fill="#334155"]{{fill:#d3cfc7}}
{O} svg [fill="#64748b"]{{fill:#a29e96}}
{O} svg [stroke="#64748b"]{{stroke:#a29e96}}
{O} svg [fill="#94a3b8"]{{fill:#8a867e}}
{O} svg [stroke="#94a3b8"]{{stroke:#6b6862}}
{O} svg [fill="#cbd5e1"]{{fill:#5a5852}}
{O} svg [stroke="#e2e8f0"],{O} svg [stroke="#eef2f6"]{{stroke:#34332f}}
{O} svg [fill="#f8fafc"]{{fill:#2b2a28}}
{O} svg [fill="#b91c1c"]{{fill:#e04848}}
{O} svg [stroke="#b91c1c"]{{stroke:#e04848}}
{O} svg [stroke="#ffffff"]{{stroke:#262624}}
{O} svg [fill="#047857"]{{fill:#34c58f}}
{O} svg [fill="#b45309"]{{fill:#e9a93c}}
{O} svg [fill="#d97706"]{{fill:#e9a93c}}
{O} svg [stroke="#d97706"]{{stroke:#e9a93c}}
"""

# Se aplica antes de pintar, para que la página no parpadee en claro.
SCRIPT_INICIAL = ('<script>try{if(localStorage.getItem("focoTema")==="oscuro")document.documentElement.classList.add("enc-oscuro")}'
                  'catch(e){}</script>')

# Íconos (lucide) con la misma fábrica de la aplicación; se suman a los de ajustar_tarjetas.py.
ICONO_ANCLA = ',encFc=wt("file-check",'
ICONOS = (',encLuna=wt("moon",[["path",{d:"M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z",key:"a7tn18"}]])'
          ',encSol=wt("sun",[["circle",{cx:"12",cy:"12",r:"4",key:"4exip2"}],["path",{d:"M12 2v2",key:"tus03m"}],'
          '["path",{d:"M12 20v2",key:"1lh1kg"}],["path",{d:"m4.93 4.93 1.41 1.41",key:"149t6j"}],["path",{d:"m17.66 17.66 1.41 1.41",key:"ptbguv"}],'
          '["path",{d:"M2 12h2",key:"1t8f8n"}],["path",{d:"M20 12h2",key:"1q8mjw"}],["path",{d:"m6.34 17.66-1.41 1.41",key:"1m8zz5"}],'
          '["path",{d:"m19.07 4.93-1.41 1.41",key:"1shlcs"}]])' + ICONO_ANCLA)

BOTON = (
    'function encBotonTema(){let[o,s]=(0,$.useState)(()=>document.documentElement.classList.contains("enc-oscuro"));'
    'return(0,u.jsx)("button",{type:"button",className:"enc-tema","aria-pressed":o,'
    'title:o?"Desactivar modo oscuro":"Activar modo oscuro","aria-label":o?"Desactivar modo oscuro":"Activar modo oscuro",'
    'onClick:()=>{let n=!o;s(n),document.documentElement.classList.toggle("enc-oscuro",n);'
    'try{localStorage.setItem("focoTema",n?"oscuro":"claro")}catch(e){}},'
    'children:(0,u.jsx)(o?encSol:encLuna,{"aria-hidden":"true"})})}'
)
ANCLA_BOTON = "function tx({filters:f,"

CAMBIOS = [
    # Con filtros: el botón va a la izquierda de «Fecha de corte».
    ('className:"enc-filtros no-print",children:[', 'className:"enc-filtros no-print",children:[(0,u.jsx)(encBotonTema,{}),'),
    # Sin filtros (ficha técnica): el botón queda solo a la derecha del título.
    ('encF&&(0,u.jsxs)("div",{ref:encR,', '!encF&&(0,u.jsx)("div",{className:"enc-filtros no-print",children:(0,u.jsx)(encBotonTema,{})}),encF&&(0,u.jsxs)("div",{ref:encR,'),
]


def una_vez(texto: str, viejo: str, nuevo: str) -> str:
    assert texto.count(viejo) == 1, f"No se encontró exactamente una vez: {viejo[:90]}…"
    return texto.replace(viejo, nuevo)


def main() -> None:
    html = PLANTILLA.read_text(encoding="utf-8")
    if MARCA in html:
        print("La plantilla ya tiene el modo oscuro; no se cambia nada.")
        return
    html = una_vez(html, ICONO_ANCLA, ICONOS)
    for viejo, nuevo in CAMBIOS:
        html = una_vez(html, viejo, nuevo)
    html = una_vez(html, ANCLA_BOTON, BOTON + ANCLA_BOTON)
    html = una_vez(html, "</style>", CSS + "</style>")
    html = una_vez(html, "</head>", SCRIPT_INICIAL + "</head>")
    PLANTILLA.write_text(html, encoding="utf-8", newline="\n")
    print(f"Modo oscuro agregado en {PLANTILLA}")


if __name__ == "__main__":
    main()
