# Guía de la capa Gold y del análisis de texto (NLP)

Esta guía está escrita para quien conoce el seguimiento del Plan Distrital de Desarrollo y sus indicadores, pero no programa. Explica qué tablas se generan, cómo se lee el texto de los reportes y qué se puede (y no se puede) concluir con ellas. La verificación de todo lo que aquí se afirma está en [AUDITORIA.md](AUDITORIA.md).

## 1. Qué problema resuelve

El seguimiento del PDD "Bogotá Camina Segura" está repartido en tres lugares:

| Fuente de la SDP | Qué trae | Formato |
|---|---|---|
| Avance del Plan | Porcentaje oficial de avance físico de cada meta producto | Excel |
| Gestión-Inversión | Lo programado, entregado, comprometido y girado de cada actividad | Excel |
| Gestión-Inversión por entidad | Lo mismo, más dos relatos que escribe cada entidad: "Retrasos y soluciones" y "Avances y Logros" | PDF |

La capa Gold junta las tres en tablas listas para analizar. Así, en una misma fila se ve cuánto avanzó una meta, cuánto dinero se comprometió y qué explicó la entidad.

## 2. Qué archivos se usan

Se usan **todos los cortes trimestrales** publicados. Seguir cada meta trimestre a trimestre es lo que permite anticipar qué pasará en el corte siguiente, que es el objetivo del modelo predictivo.

| Corte | Avance físico | Dinero y actividades | Relatos (PDF) |
|---|---|---|---|
| 30/09/2024 | Sí | No | Sí |
| 31/12/2024 | Sí | Sí | Sí |
| 31/03/2025 | Sí | Sí | No |
| 30/06/2025 | Sí | Sí | No |
| 30/09/2025 | Sí | Sí | No |
| 31/12/2025 | Sí | Sí | No |
| 31/03/2026 | Sí | Sí | Sí |
| 30/06/2026 | Sí | Sí | Sí |
| 30/09/2026 | Sí | Sí | No |

Los cortes de 2025 y el de septiembre de 2026 no tienen relatos porque la SDP no publicó el PDF por entidad (esas publicaciones solo traen Excel). Si se consiguen, basta dejarlos en `data/raw/` y volver a ejecutar.

El *scraper* descarga los archivos del portal de la SDP (capa Bronce) y los consolida sin calcular nada nuevo (capa Silver). Este repositorio toma Silver y los PDF, y produce Gold. No modifica Silver ni Bronce.

## 3. Cómo se lee el texto de los PDF

El PDF por entidad es una tabla muy ancha: cifras de cuatro años y, debajo de cada indicador, los dos relatos. Si se copiara como texto corrido, las cifras se mezclarían con las frases. Por eso el programa usa la **posición** de cada renglón en la página:

- Un título en negrita al margen izquierdo que empieza con un código de cuatro dígitos abre una **meta producto**.
- Un renglón con sangría que empieza con un código abre un **indicador**.
- Los rótulos "Retrasos y soluciones:" y "Avances y Logros:" abren cada **relato**.
- El relato continúa (incluso en la página siguiente) hasta el próximo título.

Cada relato queda guardado con su entidad, meta, indicador, corte y **número de página**, para poder ir al PDF y comprobarlo.

## 4. Cómo se identifican las barreras

### 4.1 De dónde salen las categorías

No se partió de una lista teórica. Se tomaron los relatos de "Retrasos y soluciones", se apartaron las frases que solo dicen "no hubo retrasos" y se contaron las expresiones más repetidas en el resto. Esas expresiones se agruparon en seis barreras y una categoría que **no** es barrera:

| Categoría | Qué recoge |
|---|---|
| Contratación | Procesos de selección, adjudicación, prórrogas, contratos suspendidos o incumplidos |
| Trámites, permisos y asuntos jurídicos | Licencias, aprobaciones, actos administrativos, predios |
| Talento humano y capacidad operativa | Falta o cambio de personal, capacidad limitada |
| Demanda y participación de la población | Baja asistencia, deserción, requisitos no cumplidos |
| Factores externos | Clima, orden público, ley de garantías |
| Coordinación, recursos y aspectos técnicos | Dependencia de otras entidades, recursos insuficientes, estudios y obras, información y sistemas |
| *Avance programado para más adelante* | *No es barrera: el resultado está previsto para un corte posterior* |

Al principio había nueve barreras. La auditoría mostró que cuatro de ellas (terceros, obra, presupuesto e información) no se distinguían bien entre sí y se fusionaron en "Coordinación, recursos y aspectos técnicos".

La última categoría de la tabla atiende una advertencia del anteproyecto: un avance bajo puede deberse a la programación y no a un problema de gestión.

### 4.2 Cómo se clasifica un relato

El relato se divide en frases. Una frase cuenta para una barrera solo si cumple tres condiciones:

1. **No es una frase de "no hubo retrasos"** ("No se presentaron retrasos", "No aplica", "conforme a lo programado").
2. **No es una frase de solución**, es decir, lo que la entidad hará para corregir. Tampoco cuenta lo que sigue a un rótulo "Soluciones:".
3. **Contiene una señal de problema**: retraso, pendiente, suspendido, debido a, a la espera, entre otras.

Ejemplo: "Se fortalecerá la articulación interinstitucional" no cuenta. "El atraso se debe a la articulación interinstitucional con el IDU" sí cuenta como dependencia de terceros.

De cada barrera se guarda la **frase exacta** que la activó. Cada relato termina en uno de cinco estados:

| Estado | Significado |
|---|---|
| Sin retraso declarado | La entidad dice que no hubo retrasos y no aparece ninguna barrera |
| Avance programado para más adelante | Solo explica que el resultado llega en un corte posterior |
| Texto sin clasificar | Hay texto, pero no se reconoce ni retraso ni barrera; requiere lectura humana |
| Retraso sin causa clasificada | La entidad reconoce un retraso, pero no se identifica la causa |
| Barrera identificada | Aparece al menos una de las seis barreras |

Si varias entidades reportan la misma meta, la meta toma el estado más delicado (el de más abajo en la tabla).

### 4.3 Por qué este método y no uno más sofisticado

Se eligió un diccionario de expresiones porque cualquier persona puede leerlo, discutirlo y corregirlo (está en `configs/barreras.yaml`), y porque cada resultado se puede comprobar con su frase de evidencia. Un modelo estadístico de temas daría grupos de palabras difíciles de explicar ante una entidad.

### 4.4 Qué tan confiable es

Se midió leyendo 180 relatos sin ver la clasificación y comparando después. El resultado sobre los 90 que no se usaron para corregir el método:

| Pregunta | Precisión | Sensibilidad |
|---|---|---|
| ¿El relato narra alguna barrera o retraso? | 94,5 % | 91,7 % |
| ¿Acertó la categoría de cada barrera? | 74,6 % | 66,0 % |

- **Precisión:** de lo que el clasificador marcó, qué parte era correcta.
- **Sensibilidad:** de lo que había de verdad, qué parte encontró.

En la práctica: saber **si** una meta narra un problema es confiable. Saber **cuál** es el problema es confiable para contratación, talento humano, demanda y factores externos, y aceptable para trámites: esas cinco categorías juntas aciertan el 85 % de las veces. La categoría fusionada "Coordinación, recursos y aspectos técnicos" es débil (44 %) y solo sirve para ubicar la frase y leerla. El detalle está en [AUDITORIA.md](AUDITORIA.md).

Dos límites adicionales:

- Muchas entidades escriben "no hubo retrasos" aunque el avance sea bajo. La ausencia de barrera en el texto no prueba que no exista.
- Una barrera identificada es una **señal para revisar**, no una prueba de incumplimiento.

## 5. Las tablas Gold

Todas están en `data/gold/`, en CSV y reunidas en el libro `gold_pdd.xlsx` (una hoja por tabla; la hoja LEAME las resume).

| Tabla | Una fila es... | Filas | Para qué sirve |
|---|---|---|---|
| `gold_meta_corte` | Una meta producto en un corte | 3.825 | Tabla principal: insumos y productos para DEA, y panel para el modelo predictivo |
| `gold_actividad_corte` | Una actividad en un corte | 13.089 | Detalle de qué actividades explican el resultado de la meta, con su avance año por año del Plan |
| `gold_narrativa_fragmento` | Un relato leído del PDF | 3.991 | Consultar el texto original y su clasificación |
| `gold_barrera_fragmento` | Una barrera encontrada en un relato | 373 | Ver la frase que sustenta cada barrera |
| `gold_catalogo_barreras` | Una categoría | 7 | Definición y expresiones buscadas |
| `gold_diccionario` | Una columna | 120 | Significado, unidad y origen de cada dato |
| `gold_control_calidad` | Una comprobación | 19 | Verificar que la construcción no alteró los datos |
| `gold_auditoria_extraccion` | Un PDF | 4 | Rótulos encontrados, relatos obtenidos y celdas vacías |
| `gold_auditoria_nlp_resumen` | Una medida de acierto | 20 | Precisión y sensibilidad del clasificador |
| `gold_auditoria_nlp` | Un relato leído por una persona | 180 | Comparación uno a uno con el clasificador |
| `gold_dea_grupo` | Un grupo comparable en un corte | 129 | Eficiencia del grupo y si es estable |
| `gold_asociacion_barreras` | Una barrera en un corte | 14 | Eficiencia de las metas con y sin esa barrera |
| `gold_modelo_particion` | Una parte de los datos | 6 | Qué cortes se usaron para entrenar y para probar |
| `gold_modelo_metricas` | Un conjunto de variables | 8 | Desempeño del modelo frente a la línea base |
| `gold_modelo_importancia` | Una variable | 50 | Qué variables pesan más |
| `gold_prediccion_riesgo` | Una meta en el último corte | 850 | Probabilidad de rezago y nivel de alerta (una fila por cada definición de riesgo) |
| `gold_comparacion_riesgo` | Una variante de la definición de rezago | 9 | Sustento de la definición elegida |
| `gold_modelo_calibracion` | Un décimo de metas, ordenadas por riesgo | 40 | Si la probabilidad anunciada coincide con lo que pasó |
| `gold_modelo_costos` | Una razón de costo entre omitir un rezago y una falsa alarma | 10 | Cómo cambian las alertas según esa razón |
| `gold_modelo_explicacion` | Una variable de una meta del último corte | 4.250 | Las cinco variables que más suben o bajan el riesgo de cada meta (SHAP) |

### Columnas clave de `gold_meta_corte`

| Columna | Cómo leerla |
|---|---|
| `avance_vigencia` | Avance físico oficial frente a lo programado para el año |
| `pct_compromisos` | Ejecución financiera: comprometido / programado del año |
| `brecha_fisico_financiera` | `pct_compromisos` − `avance_vigencia`. Positivo: el dinero va más adelantado que la entrega |
| `pct_actividades_entrega_cero` | Proporción de actividades programadas que aún no entregan nada |
| `estado_narrativa` | Resumen del relato de retrasos de la meta |
| `barrera_...` | 1 si la meta menciona esa barrera, 0 si no |
| `eficiencia_dea` | Eficiencia relativa frente a metas comparables (0 a 1) |
| `avance_vigencia_siguiente` | El avance que la meta mostró en el corte siguiente |
| `riesgo_relativo_siguiente` | Variable que el modelo anticipa (ver sección 6) |

### Entidades normalizadas

Los nombres de las entidades se normalizan con `data/raw/Normalizacion_Entidades.xlsx` (nombre oficial con sigla, NIT, códigos SIGEP y de Hacienda, sector). `scripts/normalizar_entidades.py` lo lleva a Silver (`data/silver/entidades/entidad.csv`), cruzando por el código de Hacienda, que es el mismo `entidad_codigo` de Gestión-Inversión con cuatro dígitos. Gold agrega `entidad_nombre_sigla` en `gold_actividad_corte` y `gold_narrativa_fragmento`, y es el nombre que muestra el tablero. Si una entidad nueva no está en el Excel, el script lo avisa: hay que agregarla con su código de Hacienda.

### Avance año por año en `gold_actividad_corte`

Cada actividad trae, además del año reportado, su avance en cada año del Plan tal como lo informa el corte (bloques VIG1 a VIG4 de Gestión-Inversión): `fisico_programado_<año>`, `fisico_entregado_<año>` y `pct_fisico_entregado_<año>`, para 2024 a 2027. Es la tabla «Año / Programación / Ejecución vigencia / Avance de la vigencia» de los reportes de la SDP y alimenta la gráfica que aparece al pasar el cursor en la sección de actividades del tablero. La columna del año reportado repite `fisico_programado` y `fisico_entregado` (un control de calidad lo verifica). `recursos_comprometidos_vigencias_futuras` suma lo ya comprometido para años posteriores al reportado.

El detalle de las demás columnas está en `gold_diccionario`.

### Reglas que se respetaron

- **El dinero no se duplica.** Se suma al nivel de actividad; los totales por meta coinciden con los de Silver.
- **Un vacío no es un cero.** Si un corte no tiene archivo financiero o relato, las columnas quedan vacías.
- **Los porcentajes oficiales no se recalculan.** Los tres avances son los publicados por la SDP.
- **Las filas rezagadas no se suman.** En marzo de 2025 hay 5 actividades que reportan 2024; quedan marcadas y fuera de los totales de la meta.
- **Nada del futuro entra como variable explicativa.** Solo cinco columnas contienen información posterior al corte: las terminadas en `_siguiente` y `riesgo_cierre_anio`.

## 6. Eficiencia, riesgo y modelo

Estas tres piezas se explican, con sus resultados y sus límites, en [RESULTADOS.md](RESULTADOS.md). En breve:

- **Eficiencia (DEA):** compara cada meta con las de su mismo tipo de anualización y sector. Un puntaje de 1 significa que ninguna meta comparable logró más avance con igual o menos dinero.
- **Riesgo:** la definición elegida es el *rezago relativo*: la meta queda, en el corte siguiente, en el 20 % más bajo de avance entre las de su mismo tipo de anualización. Se escogió tras comparar nueve variantes. Hay dos definiciones alternas en la tabla, como referencia.
- **Modelo:** estima la probabilidad de rezago en el corte siguiente y la compara con una línea base que solo usa variables financieras. Las probabilidades se calibran, el umbral de alerta se fija por costos (omitir un rezago pesa 5 veces una falsa alarma) y cada alerta trae las tres variables que más la explican.

## 7. Primera lectura de los resultados

Sobre los tres cortes que tienen a la vez dinero y relatos (dic-2024, mar-2026, jun-2026):

| Estado del relato | Metas-corte | Avance físico del año (mediana) | Brecha físico-financiera (mediana) | Actividades con entrega cero (promedio) |
|---|---|---|---|---|
| Sin retraso declarado | 969 | 63,5 % | 0,0 puntos | 9,5 % |
| Barrera identificada | 177 | 35,2 % | 18,1 puntos | 20,1 % |
| Texto sin clasificar | 89 | 39,2 % | 19,0 puntos | 17,9 % |
| Retraso sin causa clasificada | 29 | 44,4 % | 23,9 puntos | 7,6 % |
| Avance programado para más adelante | 9 | 0,0 % | 66,4 puntos | 41,4 % |

Las metas donde la entidad narra una barrera muestran cerca de la mitad del avance físico, más dinero comprometido que entrega y el doble de actividades sin entrega. Es una **asociación descriptiva**: mezcla cortes de distinto momento del año y no prueba causa. La prueba formal, con los puntajes DEA y corte por corte, está en [RESULTADOS.md](RESULTADOS.md).

Las barreras más mencionadas son contratación (82 metas-corte) y trámites y permisos (60). La categoría fusionada aparece en 88, pero su conteo no es fiable.

## 8. Qué falta

- **Relatos de 2025 y de septiembre de 2026:** la SDP no publicó esos PDF; habría que pedirlos.
- **Mejorar la categoría fusionada** de barreras y contrastar las lecturas con una segunda persona.
- **Segunda lectura** de los relatos usados para medir el clasificador.

## 9. Cómo volver a generar las tablas

El tablero `tablero/index.html` muestra estas tablas con filtros y gráficas; se regenera con `python scripts/generar_tablero.py`.

Con Python instalado, desde la carpeta del repositorio:

```bash
python scripts/construir_gold.py
```

Las rutas de entrada de cada integrante van en `configs/pdd.local.yaml`; los parámetros del DEA, del riesgo y del modelo, en `configs/pdd.yaml`; las expresiones de cada barrera, en `configs/barreras.yaml`; las lecturas de la auditoría, en `auditoria/etiquetas_barreras.csv`. Cada ejecución repite todas las comprobaciones y vuelve a medir el acierto del clasificador.
