// Gráficas del tablero, dibujadas en SVG sin librerías (funcionan sin conexión).
//
// Criterios de diseño (curso de Visualización de Datos, sesiones 1 a 6):
//   · Título activo: dice el hallazgo, no el nombre de la variable, y se recalcula con cada filtro.
//   · Gris para el contexto y UN color para la historia (atributo preatentivo).
//   · Etiquetado directo sobre las marcas en lugar de leyenda; una anotación con la conclusión.
//   · Posición y longitud antes que área o ángulo; barras desde cero; un solo eje por gráfica.
//   · Varias medidas: paneles pequeños con la misma escala, nunca doble eje.
//   · No esconder la distribución detrás de un promedio: se ven las metas, no solo la mediana.
//   · Color y forma a la vez (círculo / cuadrado), para que se lea sin distinguir colores.
//   · Detalle bajo demanda: el valor exacto aparece al pasar el cursor. Fuente visible.
const G = (() => {
  const FOCO = '#b75b16', GRIS = '#b9c5ca', GRIS_OSC = '#6f828a', TENUE = '#dde5e8', TINTA = '#183743';
  const e = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const n1 = v => v == null ? '—' : v.toLocaleString('es-CO', {maximumFractionDigits: 1});
  const n2 = v => v == null ? '—' : v.toLocaleString('es-CO', {minimumFractionDigits: 2, maximumFractionDigits: 2});
  const med = xs => { const v = xs.filter(x => x != null).sort((a, b) => a - b); if (!v.length) return null; const m = v.length >> 1; return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
  const fechaLarga = c => { const [a, m] = c.split('-'); return `${['marzo', 'junio', 'septiembre', 'diciembre'][m / 3 - 1]} de ${a}`; };
  const fuente = c => `Fuente: Secretaría Distrital de Planeación, corte del ${c.split('-').reverse().join('/')}. Cálculos del proyecto.`;
  const marco = (titulo, subtitulo, svg, corte) => `<div class="grafica"><div class="gtitulo">${e(titulo)}</div><div class="gsub">${subtitulo}</div>${svg}<div class="gnota">${e(fuente(corte))}</div></div>`;
  const vacia = (titulo, motivo) => `<div class="grafica"><div class="gtitulo">${e(titulo)}</div><div class="gvacia">${e(motivo)}</div></div>`;
  const lienzo = (W, H, titulo, cuerpo) => `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${e(titulo)}">${cuerpo}</svg>`;
  const circulo = (x, y, c, tip = '', r = 5) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}" stroke="#fff" stroke-width="1.5"${tip ? ` data-tip="${e(tip)}"` : ''}/>`;
  const cuadro = (x, y, c, tip = '', l = 9) => `<rect x="${x - l / 2}" y="${y - l / 2}" width="${l}" height="${l}" rx="1.5" fill="${c}" stroke="#fff" stroke-width="1.5"${tip ? ` data-tip="${e(tip)}"` : ''}/>`;

  // 1. ¿Dónde están las metas rezagadas dentro de la distribución del avance?
  function distribucion(filas, corte) {
    const v = filas.filter(m => m.av != null);
    if (!v.length) return vacia('Avance físico de las metas', 'No hay metas en la bandeja.');
    const tramos = Array.from({length: 11}, () => ({n: 0, r: 0}));
    v.forEach(m => { const t = tramos[Math.min(10, Math.floor(m.av / 10))]; t.n++; t.r += m.rz === 1; });
    const rez = v.filter(m => m.rz === 1), mr = med(rez.map(m => m.av));
    const titulo = rez.length ? `${rez.length} de ${v.length} metas están rezagadas: la mitad de ellas lleva ${n1(mr)} % de avance o menos`
      : `Ninguna de las ${v.length} metas de la bandeja está rezagada`;
    const W = 520, H = 200, x0 = 30, y0 = 158, alto = 128, w = (W - x0 - 8) / 11, max = Math.max(...tramos.map(t => t.n));
    const paso = Math.max(1, Math.ceil(max / 4 / 5) * 5);
    let s = '';
    for (let k = 0; k <= max; k += paso) s += `<line x1="${x0}" x2="${W - 8}" y1="${y0 - alto * k / max}" y2="${y0 - alto * k / max}" class="grejilla"/><text x="${x0 - 5}" y="${y0 - alto * k / max + 3}" class="geje" text-anchor="end">${k}</text>`;
    tramos.forEach((t, i) => {
      const x = x0 + i * w + 2, hT = alto * t.n / max, hR = alto * t.r / max, rango = i < 10 ? `entre ${i * 10} y ${i * 10 + 10} %` : 'de 100 % o más';
      s += `<g data-tip="Avance ${rango}: ${t.n} metas, ${t.r} de ellas rezagadas"><rect x="${x0 + i * w}" y="${y0 - alto}" width="${w}" height="${alto}" fill="transparent"/>`
        + (t.n > t.r ? `<rect x="${x}" y="${y0 - hT}" width="${w - 4}" height="${Math.max(0, hT - hR - (t.r ? 2 : 0))}" rx="2" fill="${GRIS}"/>` : '')
        + (t.r ? `<rect x="${x}" y="${y0 - hR}" width="${w - 4}" height="${hR}" rx="2" fill="${FOCO}"/>` : '') + '</g>'
        + `<text x="${x0 + i * w + w / 2}" y="${y0 + 13}" class="geje" text-anchor="middle">${i < 10 ? i * 10 : '100+'}</text>`;
    });
    const iR = tramos.reduce((b, t, i) => t.r > tramos[b].r ? i : b, 0), iN = tramos.reduce((b, t, i) => t.n - t.r > tramos[b].n - tramos[b].r ? i : b, 0);
    if (tramos[iR].r) s += `<text x="${x0 + iR * w + w / 2}" y="${y0 - alto * tramos[iR].n / max - 6}" class="gdirecta foco" text-anchor="${iR < 2 ? 'start' : 'middle'}">Rezagadas</text>`;
    if (iN !== iR) s += `<text x="${x0 + iN * w + w / 2}" y="${y0 - alto * tramos[iN].n / max - 6}" class="gdirecta" text-anchor="middle">Demás metas</text>`;
    s += `<text x="${x0}" y="${H - 6}" class="geje">Avance físico del año (%)</text>`;
    return marco(titulo, 'Número de metas en cada tramo de avance físico oficial del año.', lienzo(W, H, titulo, s), corte);
  }

  // 2. ¿El dinero va por delante de la entrega? Contexto en gris, rezagadas en color.
  function dispersion(filas, seleccionada, corte) {
    const p = filas.filter(m => m.av != null && m.pc != null);
    if (!p.length) return vacia('Avance físico frente a dinero comprometido', 'Este corte no tiene información de dinero comprometido.');
    const rez = p.filter(m => m.rz === 1), conMitad = rez.filter(m => m.pc >= 50).length, adelantadas = p.filter(m => m.pc - m.av > 30).length;
    const titulo = rez.length ? `${conMitad} de las ${rez.length} metas rezagadas ya comprometieron más de la mitad de su dinero`
      : `En ${adelantadas} de ${p.length} metas el dinero va más de 30 puntos por delante del avance`;
    const W = 520, H = 268, x0 = 34, y0 = 226, w = W - x0 - 14, h = 200, X = v => x0 + w * Math.min(100, v) / 100, Y = v => y0 - h * Math.min(100, v) / 100;
    let s = [0, 25, 50, 75, 100].map(k => `<line x1="${x0}" x2="${W - 14}" y1="${Y(k)}" y2="${Y(k)}" class="grejilla"/><text x="${x0 - 5}" y="${Y(k) + 3}" class="geje" text-anchor="end">${k}</text><text x="${X(k)}" y="${y0 + 13}" class="geje" text-anchor="middle">${k}</text>`).join('');
    s += `<line x1="${X(0)}" y1="${Y(0)}" x2="${X(100)}" y2="${Y(100)}" stroke="${GRIS_OSC}" stroke-dasharray="4 4" stroke-width="1"/>`
      + `<text x="${X(64)}" y="${Y(70) - 5}" class="gdirecta" transform="rotate(${-Math.atan2(h, w) * 180 / Math.PI} ${X(64)} ${Y(70) - 5})" text-anchor="middle">avance = dinero comprometido</text>`
      + `<text x="${X(99)}" y="${Y(4)}" class="gdirecta" text-anchor="end">▼ el dinero va por delante de la entrega</text>`;
    const punto = m => { const foco = m.rz === 1, sel = m.i === seleccionada;
      return `<circle cx="${X(m.pc)}" cy="${Y(m.av)}" r="${sel ? 6.5 : foco ? 4.5 : 3.5}" fill="${foco ? FOCO : GRIS}" fill-opacity="${foco ? 0.9 : 0.75}" stroke="${sel ? TINTA : '#fff'}" stroke-width="${sel ? 2 : 1}" data-meta-punto="${m.i}" data-tip="Meta ${m.i}${foco ? ' · rezagada' : ''}: ${n1(m.av)} % de avance físico y ${n1(m.pc)} % del dinero comprometido" style="cursor:pointer"/>`; };
    s += p.filter(m => m.rz !== 1).map(punto).join('') + rez.map(punto).join('');
    s += circulo(x0 + 10, 16, FOCO, '', 4.5) + `<text x="${x0 + 19}" y="19" class="gdirecta foco">Rezagadas</text>` + circulo(x0 + 86, 16, GRIS, '', 3.5) + `<text x="${x0 + 94}" y="19" class="gdirecta">Demás metas</text>`;
    s += `<text x="${x0}" y="${H - 6}" class="geje">Dinero comprometido (% de lo programado para el año)</text>`;
    return marco(titulo, 'Cada punto es una meta. Vertical: avance físico del año (%, tope en 100). Haz clic en un punto para abrir su ficha.', lienzo(W, H, titulo, s), corte);
  }

  // Eje de tiempo compartido por las gráficas de evolución.
  function ejeTiempo(cortes, X, y0, yTope) {
    let s = '';
    cortes.forEach((c, i) => {
      if (i && c.slice(0, 4) !== cortes[i - 1].slice(0, 4)) s += `<line x1="${(X(i) + X(i - 1)) / 2}" x2="${(X(i) + X(i - 1)) / 2}" y1="${yTope}" y2="${y0}" stroke="${TENUE}"/>`;
      s += `<text x="${X(i)}" y="${y0 + 12}" class="geje" text-anchor="middle">${['mar', 'jun', 'sep', 'dic'][c.slice(5, 7) / 3 - 1]}</text>`;
      if (!i || c.slice(0, 4) !== cortes[i - 1].slice(0, 4)) s += `<text x="${X(i)}" y="${y0 + 24}" class="geje" text-anchor="middle">${c.slice(0, 4)}</text>`;
    });
    return s;
  }
  function trazo(valores, X, Y, color, grosor, nombre, cortes, forma) {
    let d = '', pluma = false, s = '';
    valores.forEach((v, i) => { if (v == null) { pluma = false; return; } d += `${pluma ? 'L' : 'M'}${X(i)} ${Y(v)}`; pluma = true; });
    s += `<path d="${d}" fill="none" stroke="${color}" stroke-width="${grosor}" stroke-linejoin="round" stroke-linecap="round"/>`;
    valores.forEach((v, i) => { if (v != null) s += forma(X(i), Y(v), color, `${nombre}: ${n1(v)} % en ${fechaLarga(cortes[i])}`, forma === circulo ? 4 : 7); });
    return s;
  }
  const ultimo = v => { for (let i = v.length - 1; i >= 0; i--) if (v[i] != null) return [v[i], i]; return null; };

  // 3. La meta frente a las de su tipo: dos paneles pequeños con la misma escala.
  function evolucionMeta(cortes, meta, grupo, tipo, corteActual) {
    const k = cortes.indexOf(corteActual), a = meta.av[k], g = grupo.av[k];
    const titulo = a == null || g == null ? 'Evolución de la meta frente a las de su tipo'
      : Math.abs(a - g) < 1 ? `En ${fechaLarga(corteActual)} la meta avanza al ritmo de las metas de su tipo (${n1(a)} %)`
      : `En ${fechaLarga(corteActual)} la meta lleva ${n1(a)} % de avance: ${n1(Math.abs(a - g))} puntos ${a < g ? 'por debajo' : 'por encima'} de las metas de su tipo`;
    const W = 520, H = 196, y0 = 150, h = 112, Y = v => y0 - h * Math.min(100, v) / 100;
    const panel = (x0, x1, nombre, m, gr, conEje) => {
      const X = i => x0 + (x1 - x0) * i / Math.max(1, cortes.length - 1);
      let s = `<text x="${x0}" y="14" class="gpanel">${nombre}</text>` + [0, 50, 100].map(v => `<line x1="${x0}" x2="${x1}" y1="${Y(v)}" y2="${Y(v)}" class="grejilla"/>${conEje ? `<text x="${x0 - 5}" y="${Y(v) + 3}" class="geje" text-anchor="end">${v}</text>` : ''}`).join('');
      s += ejeTiempo(cortes, X, y0, Y(100)) + trazo(gr, X, Y, GRIS_OSC, 1.5, 'Mediana de su tipo', cortes, cuadro) + trazo(m, X, Y, FOCO, 2.5, 'Esta meta', cortes, circulo);
      const um = ultimo(m), ug = ultimo(gr);
      if (um) s += `<text x="${X(um[1]) + 8}" y="${Y(um[0]) + (ug && Math.abs(Y(um[0]) - Y(ug[0])) < 11 ? (um[0] >= ug[0] ? -4 : 11) : 3)}" class="gdirecta foco">${n1(um[0])} %</text>`;
      if (ug) s += `<text x="${X(ug[1]) + 8}" y="${Y(ug[0]) + (um && Math.abs(Y(um[0]) - Y(ug[0])) < 11 ? (ug[0] > um[0] ? -4 : 11) : 3)}" class="gdirecta">${n1(ug[0])} %</text>`;
      return s;
    };
    const s = panel(28, 214, 'Avance físico del año (%)', meta.av, grupo.av, true) + panel(292, 478, 'Dinero comprometido (%)', meta.pc, grupo.pc, true)
      + circulo(34, 184, FOCO, '', 4) + `<text x="43" y="187" class="gdirecta foco">Esta meta</text>` + cuadro(106, 184, GRIS_OSC, '', 7) + `<text x="115" y="187" class="gdirecta">Mediana de las metas tipo ${e(tipo || '—')}</text>`;
    return marco(titulo, 'Los dos paneles usan la misma escala. Ambas medidas vuelven a empezar cada enero; por eso bajan al cambiar de año.', lienzo(W, H, titulo, s), corteActual);
  }

  // 4. Brecha entre el avance y el dinero, por sector o entidad (mancuernas + cada meta como punto).
  function brechas(lista, plural, corte) {
    const filas = lista.filter(f => f.av != null && f.pc != null).map(f => ({...f, brecha: f.pc - f.av})).sort((a, b) => b.brecha - a.brecha);
    if (!filas.length) return vacia(`Avance y dinero comprometido por ${plural}`, 'Este corte no tiene detalle de actividades.');
    const top = filas[0], vis = filas.slice(0, 14);
    const titulo = top.brecha > 0 ? `${top.n}: el dinero va ${n1(top.brecha)} puntos por delante del avance, la mayor brecha entre ${filas.length} ${plural}`
      : `En ningún caso el dinero comprometido supera al avance físico`;
    const W = 520, alto = 22, x0 = 176, x1 = W - 58, H = vis.length * alto + 44, X = v => x0 + (x1 - x0) * Math.min(100, Math.max(0, v)) / 100;
    let s = [0, 50, 100].map(k => `<line x1="${X(k)}" x2="${X(k)}" y1="22" y2="${H - 18}" class="grejilla"/><text x="${X(k)}" y="${H - 5}" class="geje" text-anchor="middle">${k} %</text>`).join('');
    vis.forEach((f, i) => {
      const y = 34 + i * alto, foco = i === 0 && f.brecha > 0;
      s += `<text x="${x0 - 8}" y="${y + 3}" class="gfila${foco ? ' fuerte' : ''}" text-anchor="end">${e(f.n.replace(/^Sector /, '').length > 29 ? f.n.replace(/^Sector /, '').slice(0, 28) + '…' : f.n.replace(/^Sector /, ''))}</text>`
        + f.metas.map(v => `<circle cx="${X(v)}" cy="${y}" r="1.6" fill="${TENUE}"/>`).join('')
        + `<line x1="${X(f.av)}" x2="${X(f.pc)}" y1="${y}" y2="${y}" stroke="${foco ? FOCO : GRIS}" stroke-width="${foco ? 3 : 2}"/>`
        + cuadro(X(f.pc), y, GRIS_OSC, `${f.n}: ${n1(f.pc)} % del dinero comprometido`, 8)
        + circulo(X(f.av), y, foco ? FOCO : GRIS_OSC, `${f.n}: ${n1(f.av)} % de avance físico (mediana de ${f.metas.length} metas)`, 4.5)
        + `<text x="${x1 + 8}" y="${y + 3}" class="gdirecta${foco ? ' foco' : ''}">${f.brecha > 0 ? '+' : ''}${n1(f.brecha)} pts</text>`;
      if (i === 0) s += `<text x="${X(f.av)}" y="${y - 9}" class="gdirecta${foco ? ' foco' : ''}" text-anchor="${f.av < f.pc ? 'end' : 'start'}">● Avance</text><text x="${X(f.pc)}" y="${y - 9}" class="gdirecta" text-anchor="${f.av < f.pc ? 'start' : 'end'}">■ Comprometido</text>`;
    });
    return marco(titulo, `Ordenado de mayor a menor brecha${filas.length > vis.length ? ` (se muestran ${vis.length} de ${filas.length})` : ''}. Los puntos pequeños son las metas de cada fila; el círculo, su mediana.`, lienzo(W, H, titulo, s), corte);
  }

  // 5. Evolución del alcance elegido: avance en color, dinero en gris, etiquetas al final de cada línea.
  function evolucionAlcance(cortes, av, pc, nombre, corteActual) {
    const k = cortes.indexOf(corteActual), a = av[k], c = pc[k];
    const titulo = a == null ? `Evolución de ${nombre}` : c == null ? `${nombre}: en ${fechaLarga(corteActual)} el avance mediano es ${n1(a)} %`
      : `${nombre}: en ${fechaLarga(corteActual)} el avance mediano es ${n1(a)} % y el dinero comprometido ${n1(c)} %`;
    if (!av.some(x => x != null)) return vacia(titulo, 'No hay datos para dibujar la evolución.');
    const W = 520, H = 214, x0 = 30, x1 = W - 128, y0 = 168, h = 136, X = i => x0 + (x1 - x0) * i / Math.max(1, cortes.length - 1), Y = v => y0 - h * Math.min(100, v) / 100;
    let s = [0, 50, 100].map(v => `<line x1="${x0}" x2="${x1}" y1="${Y(v)}" y2="${Y(v)}" class="grejilla"/><text x="${x0 - 5}" y="${Y(v) + 3}" class="geje" text-anchor="end">${v}</text>`).join('');
    s += ejeTiempo(cortes, X, y0, Y(100)) + trazo(pc, X, Y, GRIS_OSC, 1.5, 'Dinero comprometido (mediana)', cortes, cuadro) + trazo(av, X, Y, FOCO, 2.5, 'Avance físico (mediana)', cortes, circulo);
    const ua = ultimo(av), uc = ultimo(pc), junto = ua && uc && Math.abs(Y(ua[0]) - Y(uc[0])) < 12;
    if (ua) s += `<text x="${X(ua[1]) + 9}" y="${Y(ua[0]) + (junto ? (ua[0] >= uc[0] ? -3 : 12) : 3)}" class="gdirecta foco">Avance ${n1(ua[0])} %</text>`;
    if (uc) s += `<text x="${X(uc[1]) + 9}" y="${Y(uc[0]) + (junto ? (uc[0] > ua[0] ? -3 : 12) : 3)}" class="gdirecta">Comprometido ${n1(uc[0])} %</text>`;
    return marco(titulo, 'Mediana de las metas del alcance en cada corte (%). Ambas medidas vuelven a empezar cada enero.', lienzo(W, H, titulo, s), corteActual);
  }

  // 6. ¿Qué barrera narran más? Barras desde cero, ordenadas; la primera en color.
  function barrerasConteo(cats, totalConRelato, corte) {
    if (!cats.length) return vacia('Barreras narradas por las entidades', 'La SDP no publicó relatos por entidad para este corte.');
    const fiables = cats.filter(c => c.fiable), top = fiables[0];
    const titulo = top && top.n ? `${top.nombre} es la barrera más narrada: ${top.n} de ${totalConRelato} metas con relato` : 'Ninguna meta del alcance narra una barrera';
    const W = 520, alto = 26, x0 = 226, x1 = W - 40, H = cats.length * alto + 30, max = Math.max(...cats.map(c => c.n), 1), paso = Math.max(1, Math.ceil(max / 3 / 5) * 5);
    let s = '';
    for (let k = 0; k <= max; k += paso) s += `<line x1="${x0 + (x1 - x0) * k / max}" x2="${x0 + (x1 - x0) * k / max}" y1="4" y2="${H - 20}" class="grejilla"/><text x="${x0 + (x1 - x0) * k / max}" y="${H - 6}" class="geje" text-anchor="middle">${k}</text>`;
    cats.forEach((c, i) => {
      const y = 8 + i * alto, w = Math.max(2, (x1 - x0) * c.n / max), foco = c === top && c.n;
      s += `<text x="${x0 - 8}" y="${y + 12}" class="gfila${foco ? ' fuerte' : c.fiable ? '' : ' tenue'}" text-anchor="end">${e(c.nombre.length > 36 ? c.nombre.slice(0, 35) + '…' : c.nombre)}</text>`
        + `<g data-tip="${e(c.nombre)}: ${c.n} metas la narran${c.fiable ? '' : ' (categoría de baja fiabilidad: solo referencia)'}"><rect x="${x0}" y="${y}" width="${x1 - x0}" height="16" fill="transparent"/><rect x="${x0}" y="${y}" width="${w}" height="16" rx="3" fill="${foco ? FOCO : c.fiable ? GRIS : TENUE}"/></g>`
        + `<text x="${x0 + w + 5}" y="${y + 12}" class="gdirecta${foco ? ' foco' : ''}">${c.n}</text>`;
    });
    return marco(titulo, 'Número de metas que narran cada barrera; una meta puede narrar varias. En gris claro, la categoría de baja fiabilidad.', lienzo(W, H, titulo, s), corte);
  }

  // 7. Eficiencia de las metas con y sin cada barrera (mancuernas).
  function barrerasEficiencia(cats, corte) {
    const filas = cats.filter(c => c.fiable && c.con != null && c.sin != null && c.n >= 5).map(c => ({...c, dif: c.con - c.sin})).sort((a, b) => a.dif - b.dif);
    if (!filas.length) return vacia('Eficiencia de las metas con y sin cada barrera', cats.length ? 'Hay muy pocas metas con barrera para comparar.' : 'La SDP no publicó relatos por entidad para este corte.');
    const top = filas[0];
    const titulo = top.dif < 0 ? `Las metas que narran ${top.nombre.toLowerCase()} tienen una eficiencia de ${n2(top.con)}, frente a ${n2(top.sin)} de las demás`
      : 'Las metas que narran barreras no muestran menor eficiencia en este corte';
    const W = 520, alto = 30, x0 = 226, x1 = W - 60, H = filas.length * alto + 46, X = v => x0 + (x1 - x0) * v;
    let s = [0, 0.5, 1].map(k => `<line x1="${X(k)}" x2="${X(k)}" y1="24" y2="${H - 18}" class="grejilla"/><text x="${X(k)}" y="${H - 5}" class="geje" text-anchor="middle">${n2(k)}</text>`).join('');
    filas.forEach((f, i) => {
      const y = 38 + i * alto, foco = i === 0 && f.dif < 0;
      s += `<text x="${x0 - 8}" y="${y + 3}" class="gfila${foco ? ' fuerte' : ''}" text-anchor="end">${e(f.nombre.length > 36 ? f.nombre.slice(0, 35) + '…' : f.nombre)}</text>`
        + `<line x1="${X(f.con)}" x2="${X(f.sin)}" y1="${y}" y2="${y}" stroke="${foco ? FOCO : GRIS}" stroke-width="${foco ? 3 : 2}"/>`
        + cuadro(X(f.sin), y, GRIS_OSC, `Sin ${f.nombre.toLowerCase()}: eficiencia mediana de ${n2(f.sin)}`, 8)
        + circulo(X(f.con), y, foco ? FOCO : GRIS_OSC, `Con ${f.nombre.toLowerCase()}: eficiencia mediana de ${n2(f.con)} (${f.n} metas)`, 4.5)
        + `<text x="${x1 + 8}" y="${y + 3}" class="gdirecta${foco ? ' foco' : ''}">${f.dif > 0 ? '+' : ''}${n2(f.dif)}</text>`;
      if (i === 0) s += `<text x="${X(f.con)}" y="${y - 10}" class="gdirecta${foco ? ' foco' : ''}" text-anchor="${f.con < f.sin ? 'end' : 'start'}">● Con la barrera</text><text x="${X(f.sin)}" y="${y - 10}" class="gdirecta" text-anchor="${f.con < f.sin ? 'start' : 'end'}">■ Sin ella</text>`;
    });
    return marco(titulo, 'Eficiencia mediana (0 a 1) de las metas que narran cada barrera y de las que no. Es una asociación, no una causa.', lienzo(W, H, titulo, s), corte);
  }

  return {distribucion, dispersion, evolucionMeta, brechas, evolucionAlcance, barrerasConteo, barrerasEficiencia};
})();

// Detalle bajo demanda: recuadro con el valor exacto al pasar el cursor sobre una marca.
(() => {
  const tip = document.createElement('div'); tip.id = 'gtip'; document.body.appendChild(tip);
  document.addEventListener('mousemove', ev => {
    const t = ev.target.closest && ev.target.closest('[data-tip]');
    if (!t) { tip.style.display = 'none'; return; }
    tip.textContent = t.dataset.tip; tip.style.display = 'block';
    tip.style.left = Math.min(window.innerWidth - tip.offsetWidth - 8, ev.clientX + 12) + 'px'; tip.style.top = (ev.clientY + 14) + 'px';
  });
})();
