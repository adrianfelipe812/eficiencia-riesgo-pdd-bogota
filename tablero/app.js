// Tablero "foco pdd": lee los datos incrustados (capa Gold) y arma tres vistas.
const D = JSON.parse(document.getElementById('data').textContent);
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const pct = v => v == null ? '—' : v.toLocaleString('es-CO', {maximumFractionDigits: 1}) + ' %';
const dec = v => v == null ? '—' : v.toLocaleString('es-CO', {minimumFractionDigits: 2, maximumFractionDigits: 2});
const mill = v => v == null ? '—' : '$' + v.toLocaleString('es-CO', {maximumFractionDigits: 0}) + ' M';
const fecha = iso => { const [a, m, d] = iso.split('-'); return `${d}/${m}/${a}`; };
const mediana = xs => { const v = xs.filter(x => x != null).sort((a, b) => a - b); if (!v.length) return null; const m = v.length >> 1; return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const PROBLEMA = ['Barrera identificada', 'Retraso sin causa clasificada'];
const COLOR_ESTADO = {'Barrera identificada': 'red', 'Retraso sin causa clasificada': 'orange', 'Texto sin clasificar': 'purple',
  'Avance programado para más adelante': 'blue', 'Sin retraso declarado': 'teal'};
const COLOR_ALERTA = {Alta: 'red', Media: 'orange', Baja: 'gray'};
const catNombre = c => D.categorias[c] ? D.categorias[c].n : c;
const catBadge = c => `<span class="badge ${D.categorias[c] && D.categorias[c].fiable ? 'orange' : 'ref'}" title="${D.categorias[c] && D.categorias[c].fiable ? '' : 'Categoría de baja fiabilidad: úsela solo como referencia'}">${esc(catNombre(c))}</span>`;

const S = {cut: D.ultimo, sector: '', entity: '', search: '', estado: '', barrera: '', senal: '', page: 0, selected: null,
  sort: null, asc: true, view: 'metas', grupo: 'sector'};

// Historia: cada meta en cada corte, para las gráficas de evolución.
const CRONO = [...D.cortes].reverse(), HIST = new Map(CRONO.map(c => [c, new Map((D.metas[c] || []).map(m => [m.i, m]))]));
// Mediana por corte de las metas del alcance (sector o entidad elegidos).
function evolucionAlcance(campo) {
  return CRONO.map(c => {
    let ms = [...HIST.get(c).values()];
    if (S.sector || S.entity) { const ids = new Set((D.actividades[c] || []).filter(a => (!S.sector || a[1] === S.sector) && (!S.entity || a[2] === S.entity)).map(a => a[0])); ms = ms.filter(m => ids.has(m.i)); }
    return mediana(ms.map(m => m[campo]));
  });
}

// Mediana por corte de las metas de un mismo tipo de anualización: el contexto contra el que se lee una meta.
const _porTipo = new Map();
function medianasDelTipo(tipo) {
  if (!_porTipo.has(tipo)) _porTipo.set(tipo, {
    av: CRONO.map(c => mediana([...HIST.get(c).values()].filter(m => m.ti === tipo).map(m => m.av))),
    pc: CRONO.map(c => mediana([...HIST.get(c).values()].filter(m => m.ti === tipo).map(m => m.pc)))});
  return _porTipo.get(tipo);
}

// Índices del corte activo: actividades por meta, y sectores y entidades de cada meta.
let ACTS = [], porMeta = new Map();
function indexar() {
  ACTS = D.actividades[S.cut] || []; porMeta = new Map();
  for (const a of ACTS) { if (!porMeta.has(a[0])) porMeta.set(a[0], []); porMeta.get(a[0]).push(a); }
}
const actsFiltradas = id => (porMeta.get(id) || []).filter(a => (!S.sector || a[1] === S.sector) && (!S.entity || a[2] === S.entity));
const sinEntrega = a => a[5] > 0 && a[6] === 0;

// Filtros de alcance (sector, entidad, búsqueda): definen de qué metas se habla en todas las vistas.
function base() {
  const q = S.search.trim().toLowerCase();
  return (D.metas[S.cut] || []).filter(m => {
    if ((S.sector || S.entity) && !actsFiltradas(m.i).length) return false;
    if (q && !(m.i.includes(q) || D.nombres[m.i].toLowerCase().includes(q) || (porMeta.get(m.i) || []).some(a => a[3].toLowerCase().includes(q)))) return false;
    return true;
  });
}
// Filtros de señal (relato, barrera, señal): definen qué entra a la bandeja.
function bandeja() {
  const filas = base().filter(m => {
    if (S.estado === 'problema' ? !PROBLEMA.includes(m.es) : S.estado && m.es !== S.estado) return false;
    if (S.barrera === 'alguna' ? !m.ba.length : S.barrera && !m.ba.includes(S.barrera)) return false;
    if (S.senal === 'rezago' && m.rz !== 1) return false;
    if (S.senal === 'cero' && !(m.nz > 0)) return false;
    if (S.senal === 'alta' && m.nv !== 'Alta') return false;
    if (S.senal === 'altamedia' && !['Alta', 'Media'].includes(m.nv)) return false;
    if (S.senal === 'ineficiente' && !(m.ef != null && m.ef < 0.5)) return false;
    if (S.senal === 'brecha' && !(m.br != null && m.br > 30)) return false;
    return true;
  });
  const clave = S.sort || (S.cut === D.ultimo ? 'pr' : 'av'), asc = S.sort ? S.asc : clave !== 'pr';
  return filas.sort((a, b) => (a[clave] == null) - (b[clave] == null) || (asc ? a[clave] - b[clave] : b[clave] - a[clave]) || a.i.localeCompare(b.i));
}

function opciones(id, lista, actual, todas) {
  $(id).innerHTML = `<option value="">${todas}</option>` + lista.map(([v, t]) => `<option value="${esc(v)}"${v === actual ? ' selected' : ''}>${esc(t)}</option>`).join('');
}
function llenarFiltros() {
  const sectores = [...new Set(ACTS.map(a => a[1]))].sort(), ents = [...new Set(ACTS.filter(a => !S.sector || a[1] === S.sector).map(a => a[2]))].sort();
  if (!sectores.includes(S.sector)) S.sector = '';
  if (!ents.includes(S.entity)) S.entity = '';
  opciones('sector', sectores.map(s => [s, s]), S.sector, ACTS.length ? 'Todos los sectores' : 'Corte sin detalle de actividades');
  opciones('entity', ents.map(e => [e, e]), S.entity, 'Todas las entidades');
  const hayRelatos = !!D.relatos[S.cut];
  opciones('estado', hayRelatos ? [['problema', 'Narra un problema (barrera o retraso)'], ...Object.keys(COLOR_ESTADO).map(e => [e, e])] : [], S.estado, hayRelatos ? 'Cualquier relato' : 'Corte sin relatos publicados');
  opciones('barrera', hayRelatos ? [['alguna', 'Alguna barrera'], ...Object.entries(D.categorias).map(([k, c]) => [k, c.n + (c.fiable ? '' : ' (solo referencia)')])] : [], S.barrera, hayRelatos ? 'Todas' : 'Corte sin relatos publicados');
  const senales = [['rezago', 'Rezagada en este corte'], ['cero', 'Con actividades sin entrega'], ['ineficiente', 'Eficiencia menor que 0,5'], ['brecha', 'Dinero muy por delante del avance']];
  if (S.cut === D.ultimo) senales.unshift(['alta', 'Alerta alta para el próximo corte'], ['altamedia', 'Alerta alta o media']);
  opciones('senal', senales, S.senal, 'Todas las metas');
}

function pintar() {
  const b = base(), filas = bandeja(), conRelato = !!D.relatos[S.cut];
  $('notice').innerHTML = `<strong>Corte del ${fecha(S.cut)}</strong> · ${S.cut === D.ultimo ? 'Es el corte más reciente: incluye la alerta de rezago para el corte siguiente.' : 'Corte anterior: muestra la situación en ese momento, sin alerta.'} ${conRelato ? '' : `La SDP no publicó relatos por entidad para este corte; el más reciente con relatos es el del ${fecha(Object.keys(D.relatos).sort().pop())}.`} ${ACTS.length ? '' : 'Este corte no tiene archivo de gestión e inversión: no hay dinero ni actividades.'}`;
  const st = [['Metas en la bandeja', filas.length, `de ${b.length} en el alcance`],
    ['Rezagadas en este corte', filas.filter(m => m.rz === 1).length, '20 % más bajo de su tipo'],
    ['Narran un problema', conRelato ? filas.filter(m => PROBLEMA.includes(m.es)).length : '—', conRelato ? 'Barrera o retraso reconocido' : 'Corte sin relatos'],
    ['Alerta alta', S.cut === D.ultimo ? filas.filter(m => m.nv === 'Alta').length : '—', S.cut === D.ultimo ? 'Riesgo de rezago en el próximo corte' : 'Solo en el último corte'],
    ['Eficiencia mediana', dec(mediana(filas.map(m => m.ef))), 'Frente a metas comparables (0 a 1)']];
  $('stats').innerHTML = st.map(([l, v, s]) => `<div class="stat"><div class="label">${l}</div><b>${v}</b><small>${s}</small></div>`).join('');
  $('scope').textContent = 'Sector, entidad y búsqueda definen el alcance de las tres vistas. Los avances físicos son los oficiales de la meta completa; el dinero y las actividades del detalle se limitan al sector o entidad elegidos.';
  $('pie').innerHTML = `Las barreras se identifican automáticamente en los relatos de las entidades. En una revisión de 90 relatos no usados para ajustar el método, acertó en ${pct(D.acierto.problema)} de los casos al señalar que un relato narra un problema y en ${pct(D.acierto.categoria)} al señalar cuál. La categoría marcada "solo referencia" es poco fiable. La eficiencia compara cada meta con las de su mismo sector y tipo de anualización. La alerta estima el riesgo de quedar en el 20 % más bajo de avance en el corte siguiente. Ninguna de estas señales constituye evidencia de irregularidad o incumplimiento. Fuente: publicaciones oficiales de la Secretaría Distrital de Planeación.`;
  if (S.view === 'metas') pintarMetas(filas);
  if (S.view === 'grupos') pintarGrupos(b);
  if (S.view === 'barreras') pintarBarreras(b);
}

function pintarMetas(filas) {
  const paginas = Math.max(1, Math.ceil(filas.length / 25));
  S.page = Math.min(S.page, paginas - 1);
  if (!filas.some(m => m.i === S.selected)) S.selected = filas.length ? filas[0].i : null;
  $('tableSubtitle').textContent = S.sort ? 'Orden elegido en el encabezado' : S.cut === D.ultimo ? 'Ordenadas de mayor a menor alerta' : 'Ordenadas de menor a mayor avance';
  $('metas').innerHTML = filas.slice(S.page * 25, S.page * 25 + 25).map(m => `<tr data-meta="${m.i}" class="${m.i === S.selected ? 'selected' : ''}" tabindex="0">
    <td><div class="code">Meta ${m.i}${m.rz === 1 ? ' · <span class="badge red">Rezagada</span>' : ''}</div><div class="metaname">${esc(D.nombres[m.i])}</div></td>
    <td><span class="pct">${pct(m.av)}</span></td><td><span class="pct">${pct(m.pc)}</span></td><td><span class="pct">${dec(m.ef)}</span></td>
    <td><span class="badge ${COLOR_ESTADO[m.es] || 'gray'}">${esc(m.es)}</span>${m.ba.length ? `<div class="rowcount">${m.ba.map(catNombre).map(esc).join(' · ')}</div>` : ''}</td>
    <td>${m.nv ? `<span class="badge ${COLOR_ALERTA[m.nv]}">${m.nv}</span><div class="rowcount">${pct(m.pr * 100)}</div>` : '<span class="muted">—</span>'}</td></tr>`).join('')
    || '<tr><td colspan="6"><div class="empty">Ninguna meta cumple los filtros.</div></td></tr>';
  $('count').textContent = `${filas.length} metas · página ${S.page + 1} de ${paginas}`;
  $('g-hist').innerHTML = G.distribucion(filas, S.cut);
  $('g-disp').innerHTML = G.dispersion(filas, S.selected, S.cut);
  pintarDetalle(filas.find(m => m.i === S.selected));
}

function metrica(etiqueta, valor, barra) {
  return `<div class="metric"><div class="label">${etiqueta}</div><b>${valor}</b>${barra == null ? '' : `<div class="bar"><span style="width:${Math.max(0, Math.min(100, barra))}%"></span></div>`}</div>`;
}
function pintarDetalle(m) {
  if (!m) { $('detail').innerHTML = '<div class="empty">Selecciona una meta para ver su avance, sus relatos y sus actividades.</div>'; return; }
  const acts = actsFiltradas(m.i).slice().sort((a, b) => sinEntrega(b) - sinEntrega(a) || (b[8] || 0) - (a[8] || 0));
  const relatos = (D.relatos[S.cut] || {})[m.i] || [];
  const pills = [m.sp && `<span class="badge gray">${esc(m.sp)}</span>`, m.ti && `<span class="badge gray">${esc(m.ti)}</span>`,
    m.rz === 1 && '<span class="badge red">Rezagada en este corte</span>', m.nv && `<span class="badge ${COLOR_ALERTA[m.nv]}">Alerta ${m.nv.toLowerCase()}</span>`].filter(Boolean).join('');
  const narrativa = !D.relatos[S.cut] ? '<p class="smallnote">La SDP no publicó relatos por entidad para este corte.</p>'
    : !relatos.length ? '<p class="smallnote">La meta no tiene relato en este corte.</p>'
    : relatos.map((r, k) => `<div class="relato"><div class="who">${esc(r.e)} · <span class="muted">${esc(r.in)}</span></div>
      <span class="badge ${COLOR_ESTADO[r.es] || 'gray'}">${esc(r.es)}</span>
      ${r.ev.map(([c, f]) => `<div class="evid ${D.categorias[c] && !D.categorias[c].fiable ? 'ref' : ''}">${D.categorias[c] ? catBadge(c) : '<span class="badge blue">Programado para más adelante</span>'}<br>“${esc(f)}”</div>`).join('')}
      <div class="narhead"><h3>Retrasos y soluciones</h3><span class="smallnote">${esc(r.f)}, pág. ${r.pg}</span></div><div class="narrative">${esc(r.r)}</div>
      ${r.a ? `<div class="narhead"><h3>Avances y logros</h3><button data-expand="${k}">Ampliar</button></div><div class="narrative" id="avance${k}">${esc(r.a)}</div>` : ''}</div>`).join('');
  $('detail').innerHTML = `<div class="eyebrow">Ficha de seguimiento · Meta ${m.i}</div><h2 class="detail-title">${esc(D.nombres[m.i])}</h2><div class="detail-pills">${pills}</div>
    <div class="metrics">${metrica('Avance del año', pct(m.av), m.av)}${metrica('Avance transcurrido', pct(m.at), m.at)}${metrica('Avance del cuatrienio', pct(m.ap), m.ap)}${metrica('% Comprometido', pct(m.pc), m.pc)}</div>
    <div class="metrics">${metrica('Eficiencia (0 a 1)', dec(m.ef), m.ef == null ? null : m.ef * 100)}${metrica('Dinero por delante del avance', m.br == null ? '—' : dec(m.br) + ' pts')}${metrica('Actividades sin entrega', m.na == null ? '—' : `${m.nz} de ${m.na}`)}${metrica('Riesgo de rezago', m.pr == null ? '—' : pct(m.pr * 100), m.pr == null ? null : m.pr * 100)}</div>
    <p class="smallnote">${m.ef == null ? 'Sin puntaje de eficiencia: la meta no tiene suficientes metas comparables, su grupo es inestable o no comprometió recursos.' : `Eficiencia medida frente a ${esc(m.gd)}.`} ${m.pr == null ? '' : 'El riesgo es la probabilidad estimada de quedar entre las metas más atrasadas de su tipo en el próximo corte.'}</p>
    ${m.ex ? `<div class="porque"><b>Por qué este riesgo:</b> ${esc(m.ex)}<div class="smallnote">Las tres variables que más mueven la probabilidad de esta meta según el modelo (SHAP). Explican el modelo, no las causas del rezago.</div></div>` : ''}
    <div class="section">${G.evolucionMeta(CRONO, {av: CRONO.map(c => HIST.get(c).get(m.i)?.av ?? null), pc: CRONO.map(c => HIST.get(c).get(m.i)?.pc ?? null)}, medianasDelTipo(m.ti), m.ti, S.cut)}</div>
    <div class="section"><h3>Lo que narra la entidad</h3><p class="smallnote">La frase resaltada es la que llevó a identificar cada barrera. Lea el relato completo antes de concluir.</p>${narrativa}</div>
    <div class="section"><h3>Actividades${S.sector || S.entity ? ' del filtro' : ''} (${acts.length})</h3>${acts.length ? '' : '<p class="smallnote">Sin actividades para este corte.</p>'}
    ${acts.slice(0, 15).map(a => `<div class="activity" style="cursor:default"><div class="actmeta"><span>${esc(a[2])} · ${esc(a[4])}</span>${sinEntrega(a) ? '<span class="badge red">Sin entrega</span>' : ''}</div><div class="acttitle">${esc(a[3])}</div>
      <div class="actnumbers"><div>Programado<b>${dec(a[5])}</b></div><div>Entregado<b>${dec(a[6])}</b></div><div>% entregado<b>${pct(a[7])}</b></div><div>Recursos<b>${mill(a[8])}</b></div><div>Comprometido<b>${mill(a[9])}</b></div><div>Girado<b>${mill(a[10])}</b></div></div></div>`).join('')}
    ${acts.length > 15 ? `<p class="smallnote">Se muestran 15 de ${acts.length}; primero las que no registran entrega.</p>` : ''}</div>`;
}

function pintarGrupos(b) {
  const idx = S.grupo === 'sector' ? 1 : 2, ids = new Set(b.map(m => m.i)), porId = new Map(b.map(m => [m.i, m])), grupos = new Map();
  for (const a of ACTS) {
    if (!ids.has(a[0]) || (S.sector && a[1] !== S.sector) || (S.entity && a[2] !== S.entity)) continue;
    if (!grupos.has(a[idx])) grupos.set(a[idx], {metas: new Set(), R: 0, K: 0, cero: 0, prog: 0});
    const g = grupos.get(a[idx]); g.metas.add(a[0]); g.R += a[8] || 0; g.K += a[9] || 0; g.prog += a[5] > 0; g.cero += sinEntrega(a);
  }
  const lista = [...grupos].map(([n, g]) => { const metas = [...g.metas].map(i => porId.get(i).av).filter(v => v != null); return {n, metas, av: mediana(metas), pc: g.R > 0 ? 100 * g.K / g.R : null}; });
  $('g-grupos').innerHTML = G.brechas(lista, S.grupo === 'sector' ? 'sectores' : 'entidades', S.cut);
  $('g-alcance').innerHTML = G.evolucionAlcance(CRONO, evolucionAlcance('av'), evolucionAlcance('pc'), S.entity || S.sector || 'Todas las metas', S.cut);
  $('gruposTitulo').textContent = S.grupo === 'sector' ? 'Cómo va cada sector' : 'Cómo va cada entidad';
  $('gruposCol').textContent = S.grupo === 'sector' ? 'Sector' : 'Entidad';
  const conRelato = !!D.relatos[S.cut];
  $('grupos').innerHTML = [...grupos].map(([n, g]) => { const ms = [...g.metas].map(i => porId.get(i)); return {n, g, ms, av: mediana(ms.map(m => m.av))}; })
    .sort((x, y) => (x.av ?? 1e9) - (y.av ?? 1e9)).map(({n, g, ms, av}) => `<tr data-grupo-valor="${esc(n)}"><td><b>${esc(n)}</b></td><td class="num">${ms.length}</td><td class="num">${pct(av)}</td>
      <td class="num">${pct(g.R > 0 ? 100 * g.K / g.R : null)}</td><td class="num">${dec(mediana(ms.map(m => m.ef)))}</td><td class="num">${g.cero} de ${g.prog}</td>
      <td class="num">${conRelato ? ms.filter(m => PROBLEMA.includes(m.es)).length : '—'}</td><td class="num">${ms.filter(m => m.rz === 1).length}</td><td class="num">${S.cut === D.ultimo ? ms.filter(m => m.nv === 'Alta').length : '—'}</td></tr>`).join('')
    || '<tr><td colspan="9"><div class="empty">Este corte no tiene detalle de actividades por sector y entidad.</div></td></tr>';
}

function pintarBarreras(b) {
  const conRelato = b.filter(m => COLOR_ESTADO[m.es]);
  const fila = (ms, celdas) => `${celdas}<td class="num">${ms.length}</td>`;
  $('estados').innerHTML = !D.relatos[S.cut] ? '<tr><td colspan="6"><div class="empty">La SDP no publicó relatos por entidad para este corte.</div></td></tr>'
    : Object.keys(COLOR_ESTADO).reverse().map(e => { const ms = conRelato.filter(m => m.es === e); return `<tr data-estado="${esc(e)}"><td><span class="badge ${COLOR_ESTADO[e]}">${esc(e)}</span></td><td class="num">${ms.length}</td><td class="num">${pct(conRelato.length ? 100 * ms.length / conRelato.length : null)}</td><td class="num">${pct(mediana(ms.map(m => m.av)))}</td><td class="num">${dec(mediana(ms.map(m => m.ef)))}</td><td class="num">${ms.filter(m => m.rz === 1).length}</td></tr>`; }).join('');
  const ids = new Set(b.map(m => m.i)), menciones = {};
  for (const [id, rs] of Object.entries(D.relatos[S.cut] || {})) if (ids.has(id)) for (const r of rs) for (const [c] of r.ev) { (menciones[c] ??= {})[r.e] = (menciones[c][r.e] || 0) + 1; }
  const cats = !D.relatos[S.cut] ? [] : Object.keys(D.categorias).map(c => { const con = b.filter(m => m.ba.includes(c)), sin = conRelato.filter(m => !m.ba.includes(c)); return {nombre: catNombre(c), fiable: D.categorias[c].fiable, n: con.length, con: mediana(con.map(m => m.ef)), sin: mediana(sin.map(m => m.ef))}; }).sort((x, y) => y.n - x.n);
  $('g-barreras').innerHTML = G.barrerasConteo(cats, conRelato.length, S.cut);
  $('g-efbar').innerHTML = G.barrerasEficiencia(cats, S.cut);
  $('barrerasNota').textContent = 'Una meta puede narrar varias barreras. La categoría "solo referencia" es poco fiable y no debe usarse para contar.';
  $('barrerasTabla').innerHTML = !D.relatos[S.cut] ? '' : Object.keys(D.categorias).map(c => { const ms = b.filter(m => m.ba.includes(c)); return {c, ms}; }).sort((x, y) => y.ms.length - x.ms.length)
    .map(({c, ms}) => `<tr data-barrera="${c}"><td>${catBadge(c)}</td><td class="num">${ms.length}</td><td class="num">${pct(mediana(ms.map(m => m.av)))}</td><td class="num">${dec(mediana(ms.map(m => m.ef)))}</td><td class="num">${ms.filter(m => m.rz === 1).length}</td>
      <td>${Object.entries(menciones[c] || {}).sort((x, y) => y[1] - x[1]).slice(0, 4).map(([e, n]) => `${esc(e)} (${n})`).join(' · ') || '—'}</td></tr>`).join('');
}

function irA(vista) {
  S.view = vista;
  document.querySelectorAll('.navbtn').forEach(x => x.classList.toggle('active', x.dataset.view === vista));
  document.querySelectorAll('.view').forEach(x => x.classList.toggle('active', x.id === 'view-' + vista));
  const titulos = {metas: ['Dónde focalizar el seguimiento', 'Avance oficial, dinero, eficiencia, relatos de las entidades y alerta de rezago.'],
    grupos: ['Cómo va cada sector y entidad', 'Resumen de las metas del alcance elegido, agrupadas por quien ejecuta sus actividades.'],
    barreras: ['Qué barreras narran las entidades', 'Lectura automática de los relatos "Retrasos y soluciones" del corte.']};
  $('titulo').textContent = titulos[vista][0]; $('subtitulo').textContent = titulos[vista][1];
  pintar();
}
function cambiar(campo, valor) { S[campo] = valor; S.page = 0; if (campo === 'cut') { S.selected = null; S.sort = null; indexar(); } if (campo === 'cut' || campo === 'sector') llenarFiltros(); pintar(); }

$('cut').innerHTML = D.cortes.map(c => `<option value="${c}">Corte ${fecha(c)}${c === D.ultimo ? ' (último)' : ''}</option>`).join('');
for (const [id, campo] of [['cut', 'cut'], ['sector', 'sector'], ['entity', 'entity'], ['estado', 'estado'], ['barrera', 'barrera'], ['senal', 'senal']]) $(id).addEventListener('change', e => cambiar(campo, e.target.value));
$('search').addEventListener('input', e => cambiar('search', e.target.value));
document.querySelectorAll('.navbtn').forEach(b => b.addEventListener('click', () => irA(b.dataset.view)));
document.querySelectorAll('[data-grupo]').forEach(b => b.addEventListener('click', () => { S.grupo = b.dataset.grupo; document.querySelectorAll('[data-grupo]').forEach(x => x.classList.toggle('active', x === b)); pintar(); }));
document.querySelectorAll('th.sortable').forEach(th => th.addEventListener('click', () => { const k = th.dataset.sort; S.asc = S.sort === k ? !S.asc : k !== 'pr'; S.sort = k; S.page = 0; pintar(); }));
$('metas').addEventListener('click', e => { const tr = e.target.closest('[data-meta]'); if (tr) { S.selected = tr.dataset.meta; pintar(); } });
$('g-disp').addEventListener('click', e => { const p = e.target.closest('[data-meta-punto]'); if (p) { S.selected = p.dataset.metaPunto; const k = bandeja().findIndex(m => m.i === S.selected); S.page = Math.floor(k / 25); pintar(); } });
$('metas').addEventListener('keydown', e => { if (e.key === 'Enter') { const tr = e.target.closest('[data-meta]'); if (tr) { S.selected = tr.dataset.meta; pintar(); } } });
$('detail').addEventListener('click', e => { const b = e.target.closest('[data-expand]'); if (b) { const n = $('avance' + b.dataset.expand); b.textContent = n.classList.toggle('expanded') ? 'Reducir' : 'Ampliar'; } });
$('previous').onclick = () => { if (S.page > 0) { S.page--; pintar(); } };
$('next').onclick = () => { S.page++; pintar(); };
$('grupos').addEventListener('click', e => { const tr = e.target.closest('[data-grupo-valor]'); if (!tr) return; S[S.grupo === 'sector' ? 'sector' : 'entity'] = tr.dataset.grupoValor; S.page = 0; llenarFiltros(); irA('metas'); });
$('estados').addEventListener('click', e => { const tr = e.target.closest('[data-estado]'); if (tr) { S.estado = tr.dataset.estado; S.barrera = ''; S.page = 0; llenarFiltros(); irA('metas'); } });
$('barrerasTabla').addEventListener('click', e => { const tr = e.target.closest('[data-barrera]'); if (tr) { S.barrera = tr.dataset.barrera; S.estado = ''; S.page = 0; llenarFiltros(); irA('metas'); } });
$('export').onclick = () => {
  const cab = ['CORTE', 'META_CODIGO', 'META_NOMBRE', 'AVANCE_VIGENCIA', 'AVANCE_TRANSCURRIDO', 'AVANCE_PLAN', 'PCT_COMPROMETIDO', 'EFICIENCIA_DEA', 'REZAGADA', 'RELATO', 'BARRERAS', 'PROBABILIDAD_REZAGO', 'ALERTA'];
  const celda = v => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  const lineas = bandeja().map(m => [S.cut, m.i, D.nombres[m.i], m.av, m.at, m.ap, m.pc, m.ef, m.rz, m.es, m.ba.map(catNombre).join(' | '), m.pr, m.nv].map(celda).join(';'));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob(['﻿' + cab.join(';') + '\n' + lineas.join('\n')], {type: 'text/csv;charset=utf-8'}));
  a.download = `foco_pdd_${S.cut}.csv`; a.click(); URL.revokeObjectURL(a.href);
};
indexar(); llenarFiltros(); irA('metas');
