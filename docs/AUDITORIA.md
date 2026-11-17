# Informe de auditoría de la capa Gold y del análisis de texto

Fecha: 12 de noviembre de 2026. Corresponde a la ejecución con los 9 cortes trimestrales (sep-2024 a sep-2026).

Este informe responde tres preguntas: ¿las tablas conservan fielmente los datos de origen?, ¿el texto se leyó bien de los PDF? y ¿qué tan confiable es la clasificación de barreras?

## 1. Resumen

| Qué se auditó | Resultado |
|---|---|
| Fidelidad de las cifras frente a Silver | 8 de 8 comprobaciones cumplen |
| Lectura de los relatos en los PDF | 4 de 4 comprobaciones cumplen |
| Uso correcto del tiempo (sin información del futuro) | 2 de 2 comprobaciones cumplen |
| Coherencia de los puntajes de eficiencia | 2 de 2 comprobaciones cumplen |
| Tablas frente a los Excel y PDF originales de la SDP | 40 de 40 comprobaciones cumplen |
| Detectar si un relato narra una barrera o retraso | Precisión 94,5 %, sensibilidad 91,7 % |
| Acertar la categoría de la barrera | Precisión 74,6 %, sensibilidad 66,0 % |

Lectura: la señal "esta meta narra un problema" es confiable. La categoría exacta del problema lo es para cinco de las seis categorías (sección 4.4).

## 2. Fidelidad de las cifras

Cada comprobación compara Gold contra una fuente independiente. Se ejecutan en cada corrida y quedan en `gold_control_calidad`.

| Comprobación | Esperado | Obtenido |
|---|---|---|
| Actividades: mismas filas que Silver | 13.089 | 13.089 |
| Actividades sin duplicados por actividad y corte | 0 | 0 |
| Metas: mismas filas que Silver | 3.825 | 3.825 |
| Metas sin duplicados por meta y corte | 0 | 0 |
| Cada corte tiene las 425 metas producto | 425 | 425 |
| Recursos programados no cambian al agregar (millones) | 287.263.316,17 | 287.263.316,17 |
| Giros no cambian al agregar (millones) | 101.498.147,73 | 101.498.147,73 |
| Avance oficial idéntico al de Silver (suma) | 211.644,54 | 211.644,54 |

Además, `python scripts/auditar_gold.py` compara las tablas con los archivos **originales** de la SDP (no con la versión intermedia): número de actividades y sumas de dinero del último corte frente al Excel original, avance de las 425 metas, y 60 relatos al azar buscados en la página del PDF que indica la tabla. Las 40 comprobaciones cumplen.

## 3. Lectura de los relatos

| Corte | Rótulos en el PDF | Relatos con texto | Celdas vacías |
|---|---|---|---|
| 30/09/2024 | 1.028 | 911 | 117 |
| 31/12/2024 | 1.028 | 1.021 | 7 |
| 31/03/2026 | 1.030 | 1.027 | 3 |
| 30/06/2026 | 1.034 | 1.032 | 2 |

- **Ningún relato se perdió.** Cada rótulo "Retrasos y soluciones" o "Avances y Logros" del PDF terminó en un relato o en una celda vacía (4.120 = 3.991 + 129).
- **Las celdas vacías lo están en el PDF.** Se revisaron las 117 de septiembre de 2024: en todas el rótulo aparece solo, sin texto al lado.
- **Cada relato quedó en su meta e indicador correctos.** El 100 % de los pares meta–indicador leídos del PDF existe en la base de Avance del Plan, que es una fuente distinta. También el 100 % de los pares entidad–meta existe en Gestión-Inversión.

## 4. Confiabilidad de la clasificación de barreras

### 4.1 Cómo se midió

1. Se sacaron al azar 180 relatos de "Retrasos y soluciones", en dos tandas de 90.
2. Cada relato se leyó **sin ver** lo que había dicho el clasificador y se anotó qué barreras narra realmente.
3. Se comparó la lectura con el clasificador.

Las dos tandas cumplen funciones distintas:

| Tanda | Uso | ¿Se puede citar? |
|---|---|---|
| Desarrollo (90) | Encontrar errores y corregir el diccionario | No: el resultado es optimista porque el método se ajustó a ella |
| Prueba (90) | Medir después de las correcciones, sin tocar nada más | Sí |

Como se tomaron más relatos de los grupos escasos (los que tienen barrera), cada relato lleva un peso para que el resultado valga para el total de relatos de retrasos (cerca de 2.000).

**Quién leyó:** la lectura la hizo Claude (el asistente de IA), no un analista de la Veeduría. Es una lectura independiente del clasificador, pero el equipo debería repetirla sobre una parte de la muestra. Las 180 lecturas están en `auditoria/etiquetas_barreras.csv` y se pueden corregir; el acierto se recalcula solo.

### 4.2 Qué se encontró y qué se corrigió

Primera medición (tanda de desarrollo, método anterior):

| Medida | Precisión | Sensibilidad |
|---|---|---|
| ¿El relato narra alguna barrera? | 82,2 % | 75,0 % |
| ¿Acertó la categoría? | 57,5 % | 63,7 % |

La precisión por categoría era bastante menor que la estimación informal anterior ("unas 24 de 30"). Los errores seguían tres patrones, y cada uno originó una corrección:

| Error | Ejemplo | Corrección |
|---|---|---|
| La palabra clave estaba en la solución, no en el problema | "Se fortalecerá la articulación interinstitucional" | Las frases de solución y todo lo que sigue al rótulo "Soluciones:" ya no cuentan |
| La palabra clave aparecía sin que hubiera problema | "Culminación satisfactoria de la obra" | Una frase solo cuenta si contiene una señal de problema (retraso, pendiente, debido a, suspendido...) |
| Retrasos sin causa explícita pasaban inadvertidos | "Se presenta retraso en las acciones de monitoreo" | Nuevo estado "Retraso sin causa clasificada" |

También se afinaron expresiones puntuales ("contrato de obra" ya no cuenta como problema de obra; "demandan" ya no cuenta como demanda).

### 4.3 Resultado final (tanda de prueba)

| Medida | Precisión | Sensibilidad |
|---|---|---|
| ¿El relato narra alguna barrera o retraso? | **94,5 %** | **91,7 %** |
| ¿Acertó la categoría de cada barrera?, con nueve categorías | 70,1 % | 63,6 % |
| ¿Acertó la categoría de cada barrera?, tras fusionar cuatro | **74,6 %** | **66,0 %** |

Cómo leerlo:

- De cada 100 relatos que el clasificador marca con problema, unos 94 lo tienen de verdad.
- De cada 100 relatos que tienen un problema, el clasificador encuentra unos 92.
- De cada 100 categorías que asigna, unas 75 son correctas; y encuentra unas 66 de cada 100 categorías reales.

De los 90 relatos de prueba: 59 aciertos completos, 26 aciertos parciales (detectó el problema, pero sobró o faltó alguna categoría), 3 falsas alarmas y 2 barreras no detectadas.

### 4.4 Qué categorías son confiables

Conteo sobre la tanda de prueba. Con tan pocos casos por categoría, las cifras son orientativas.

| Categoría | Casos reales | Precisión | Sensibilidad | Lectura |
|---|---|---|---|---|
| Contratación | 19 | 88 % | 79 % | Confiable |
| Talento humano y capacidad | 8 | 100 % | 88 % | Confiable |
| Demanda y población | 10 | 100 % | 60 % | Precisa, pero se le escapan casos |
| Trámites y permisos | 13 | 67 % | 77 % | Aceptable |
| Factores externos | 4 | 100 % | 50 % | Pocos casos |
| **Las cinco anteriores juntas** | 54 | **85 %** | **74 %** | Confiable en conjunto |
| Coordinación, recursos y aspectos técnicos (fusionada) | 19 | 44 % | 37 % | Débil |

La categoría fusionada reúne cuatro que, medidas por separado, eran débiles:

| Categoría original | Casos reales | Precisión | Sensibilidad |
|---|---|---|---|
| Dependencia de terceros | 10 | 43 % | 30 % |
| Técnico y de obra | 5 | 33 % | 40 % |
| Presupuesto | 4 | 33 % | 25 % |
| Información y sistemas | 3 | 25 % | 33 % |

**La fusión ayudó menos de lo esperado.** Se pensaba que estas cuatro se confundían entre sí y que juntas acertarían más. La precisión general subió de 70,1 % a 74,6 %, pero la categoría fusionada sigue en 44 %: el problema no era solo que se confundieran entre ellas, sino que sus expresiones ("obra", "plataforma", "articulación con") aparecen a menudo en frases que hablan de otra cosa.

Una salvedad sobre esta última cifra: la decisión de fusionar se tomó mirando los resultados de la tanda de prueba, así que el 74,6 % es algo optimista. El 94,5 % de la detección de problema no tiene ese sesgo.

### 4.5 Qué se recomienda

- **Usar con confianza** `estado_narrativa` y `menciona_dificultad` como señales de que la meta narra un problema.
- **Usar como variables** las banderas de contratación, talento humano, demanda, factores externos y trámites.
- **No usar como variable** la bandera `barrera_coordinacion_recursos_y_tecnica`. Sirve para ubicar la frase y leerla, no para contar.
- Para clasificar bien esos casos haría falta un método que entienda el sentido de la frase y no solo sus palabras. Es una decisión del equipo, porque se gana acierto pero se pierde la transparencia del diccionario.

## 5. Uso correcto del tiempo

El modelo predictivo no debe conocer el futuro. Se comprobó que:

- El "corte siguiente" de cada fila es siempre posterior y de la misma meta.
- El último corte no tiene dato de corte siguiente (queda vacío, no en cero).
- Solo cinco columnas contienen información posterior al corte: `fecha_corte_siguiente`, `avance_vigencia_siguiente`, `riesgo_relativo_siguiente`, `riesgo_lineal_siguiente` y `riesgo_cierre_anio`. Son lo que se quiere predecir y ninguna entra como variable explicativa; la auditoría lo comprueba contra la lista de variables del modelo.

## 6. Límites que la auditoría no resuelve

- **Relatos en 4 de 9 cortes.** La SDP no publicó el PDF por entidad en 2025 ni en septiembre de 2026, así que la narrativa no cubre esos cinco cortes.
- **Septiembre de 2024 no tiene archivo de Gestión-Inversión.** Ese corte tiene avance físico y relatos, pero no dinero.
- **La variable de riesgo es relativa.** Marca el 20 % más bajo de cada tipo de anualización, así que siempre señala una quinta parte de las metas. En diciembre, 85 % de las marcadas cerraron el año por debajo de 90 % (ver RESULTADOS.md).
- **Un solo lector.** Las etiquetas no se han contrastado con una segunda persona.
- **El texto dice lo que la entidad quiso decir.** 969 de 1.275 metas-corte declaran no tener retrasos; eso no prueba que no los haya.
