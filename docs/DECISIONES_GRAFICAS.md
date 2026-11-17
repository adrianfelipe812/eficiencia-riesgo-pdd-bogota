# Decisiones de diseño de las gráficas del tablero

Este documento justifica cada gráfica de `tablero/index.html` con los criterios del curso de Visualización de Datos (sesiones 1 a 6). Sigue la plantilla de "documento de decisiones" de la sesión 2.

**Propósito:** el tablero es exploratorio (el analista filtra y busca), pero cada gráfica se diseñó como explicativa: abre con su hallazgo. **Audiencia:** analistas que conocen los indicadores del PDD y no programan. **Decisión que apoya:** en qué metas, sectores o entidades focalizar el seguimiento.

## Criterios aplicados a todas

| Criterio del curso | Cómo se aplica |
|---|---|
| Título activo ("Bing") | El título dice el hallazgo con su cifra, no el nombre de la variable |
| Interactividad coherente | El título, las etiquetas y la fuente se recalculan con cada filtro y cada corte; no quedan títulos ni anotaciones "fantasma" |
| Gris para el contexto, un color para la historia | Todo va en gris salvo lo que sustenta el título, en naranja |
| Etiquetado directo | Las series se nombran sobre las marcas; no hay cajas de leyenda |
| Detalle bajo demanda | El valor exacto aparece al pasar el cursor, redactado como frase |
| Integridad de escala | Barras desde cero; porcentajes en escala fija de 0 a 100; ningún eje truncado |
| Un solo eje | Ninguna gráfica tiene doble eje; dos medidas van en paneles con la misma escala |
| Datos-tinta | Sin bordes ni fondos; rejilla suave detrás de los datos |
| Accesibilidad | Naranja y gris se distinguen por luminosidad, y las dos series usan formas distintas (círculo y cuadrado), así que se leen sin distinguir colores y en blanco y negro. Se evita el par rojo–verde |
| Auditabilidad | Cada gráfica cita fuente y corte |

Sobre el color: el naranja se eligió como único acento por ser neutro (no sugiere "bueno" ni "malo", como harían el verde y el rojo) y por su contraste con el gris.

## Gráfica por gráfica

| # | Gráfica | Relación que muestra | Marca y canal | Qué se resalta | Qué se quitó |
|---|---|---|---|---|---|
| 1 | Metas por tramo de avance | Distribución | Barras; longitud desde cero | El tramo de cada barra que corresponde a metas rezagadas | El color uniforme de la versión anterior, que no decía nada |
| 2 | Avance frente a dinero comprometido | Correlación | Puntos; posición en dos ejes de 0 a 100 | Las metas rezagadas; la diagonal marca "avance = dinero" | La escala de cuatro tonos por eficiencia: eran demasiadas codificaciones para un solo mensaje |
| 3 | Evolución de la meta | Tendencia, meta frente a su contexto | Líneas en dos paneles pequeños con la misma escala | La meta; la mediana de las metas de su tipo queda en gris | Las dos medidas superpuestas en un mismo panel |
| 4 | Brecha por sector o entidad | Comparación de dos medidas (ranking por brecha) | Mancuernas; posición | La fila con la mayor brecha | Las barras agrupadas: obligaban a restar mentalmente |
| 5 | Evolución del alcance | Tendencia | Dos líneas en la misma escala | El avance físico; el dinero queda en gris | La leyenda: cada línea lleva su nombre y su valor al final |
| 6 | Metas que narran cada barrera | Ranking | Barras horizontales ordenadas, desde cero | La barrera más narrada entre las confiables | El color en todas las barras |
| 7 | Eficiencia con y sin cada barrera | Comparación antes–después | Mancuernas; posición en escala de 0 a 1 | La barrera con mayor diferencia | Las barras agrupadas |

## Decisiones que conviene poder defender

- **Por qué mancuernas y no barras agrupadas (4 y 7).** El mensaje es la magnitud de la diferencia. La mancuerna la dibuja como una línea; con barras, el lector tiene que restar.
- **Por qué la gráfica 4 muestra cada meta como un punto pequeño.** La mediana sola esconde la dispersión: dos sectores con la misma mediana pueden tener metas muy distintas. Es el criterio de "no esconder la distribución" de la sesión 3.
- **Por qué dos paneles en la gráfica 3.** Avance y dinero son medidas distintas. Superponerlas invita a leer cruces que no significan nada; dos paneles con la misma escala permiten comparar sin doble eje.
- **Por qué el avance se dibuja con tope en 100 en la gráfica 2.** Unas pocas metas superan el 100 % y aplastarían al resto. El tope se declara en el subtítulo y el valor real aparece al pasar el cursor.
- **Por qué la categoría de barreras poco fiable va en gris claro (6) y fuera de la gráfica 7.** Su precisión es de 44 %; mostrarla con el mismo peso que las demás sería presentar como dato algo que no lo es.

## Chequeo ético

- Ningún eje truncado ni gráfico en 3D; ninguna torta.
- Se muestran todos los cortes disponibles en las evoluciones, incluidos los que desfavorecen a la meta: no hay recorte conveniente.
- Las gráficas de evolución advierten que el avance y el dinero vuelven a empezar cada enero, para que la caída no se lea como retroceso.
- La gráfica 7 declara que muestra una asociación y no una causa.
- La anotación de cada gráfica se limita a hechos calculables con los datos.
