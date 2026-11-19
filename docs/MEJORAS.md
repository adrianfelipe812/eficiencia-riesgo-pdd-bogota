# Mejoras realizadas y auditoría del estado actual

Bitácora del proyecto, escrita para quien conoce de indicadores pero no programa. Cada sección registra lo hecho en su fecha; las cifras vigentes están en [RESULTADOS.md](RESULTADOS.md) y [AUDITORIA.md](AUDITORIA.md).

## 1. De dónde partimos y dónde estamos

| Aspecto | Al inicio | Ahora |
|---|---|---|
| Tema del repositorio | Abandono de clientes de un banco (ejercicio de curso) | Seguimiento del PDD "Bogotá Camina Segura" |
| Datos | Un archivo de clientes bancarios | 425 metas producto en 9 cortes trimestrales (sep-2024 a sep-2026) |
| Capa Gold | No existía | 20 tablas en CSV y un libro de Excel |
| Texto de los reportes | No se usaba | 3.991 relatos leídos de 4 PDF, cada uno con su página |
| Barreras | No existían | 6 categorías, con la frase que sustenta cada una |
| Verificación | Ninguna | 19 controles automáticos, auditoría contra los archivos originales y una medición del acierto con 180 relatos leídos |
| Documentación para no programadores | Ninguna | Guía, informe de auditoría y diccionario de 96 columnas |

## 2. Mejoras, una por una

### 2.1 Lectura de los relatos en los PDF

Los relatos "Retrasos y soluciones" y "Avances y Logros" solo existen en los PDF por entidad, mezclados con cifras de cuatro años. El programa los separa usando la posición de cada renglón en la página y guarda cada relato con su entidad, meta, indicador y número de página.

### 2.2 Clasificación de barreras

| Versión | Qué hacía | Precisión al detectar problema | Precisión por categoría |
|---|---|---|---|
| 1 | Buscaba palabras clave en todo el relato | 82 % | 57 % |
| 2 | Ignora frases de solución y exige una señal de problema en la frase | 94,5 % | 70 % |
| 3 | Además, fusiona cuatro categorías que no se distinguían bien | 94,5 % | 74,6 % |

Cómo leerlo: de cada 100 relatos que el programa marca con problema, 94 lo tienen de verdad. La categoría exacta acierta 3 de cada 4 veces; las cinco categorías confiables juntas llegan al 85 %, y la fusionada se queda en 44 % (se conserva solo como referencia).

### 2.3 Medición honesta del acierto

Se leyeron 180 relatos sin ver lo que decía el programa. Los primeros 90 sirvieron para corregir el método; los otros 90 no se tocaron y dan la cifra que se cita. Así se evitó presentar un resultado inflado: la primera estimación informal ("unas 24 de 30") resultó optimista.

### 2.4 Histórico trimestral

Las tablas siguen cada meta en todos los cortes. Eso permite guardar, junto a cada fila, lo que pasó en el corte siguiente, que es lo que el modelo predictivo deberá anticipar.

### 2.5 Controles en cada ejecución

Cada vez que se generan las tablas se comprueba que las filas, el dinero y el avance oficial coincidan con la fuente; que ningún relato se haya perdido; que cada relato esté en su meta e indicador; y que ninguna columna explicativa contenga información del futuro.

## 3. Auditoría del 11 de noviembre de 2026 (con 8 cortes)

Se hizo una revisión adicional, distinta de los controles habituales: comparar las tablas con los **archivos originales de la SDP**, no con la versión intermedia. Se puede repetir con `python scripts/auditar_gold.py`.

### 3.1 Lo que está bien (30 comprobaciones)

| Comprobación | Resultado |
|---|---|
| Actividades de junio de 2026 frente al Excel original | 1.655 en ambos |
| Recursos programados frente al Excel original | 42.297.666,72 millones en ambos |
| Recursos comprometidos, girados y entrega física | Coinciden al centavo |
| Avance físico de las 425 metas frente al Excel original | Diferencia máxima de 0,005 puntos (redondeo) |
| 60 relatos al azar buscados en su página del PDF | 60 de 60 aparecen |
| Cada frase de evidencia está dentro de su relato | Sí |
| El conteo de barreras por meta coincide con el detalle | Sí |
| El dato del "corte siguiente" es realmente el del corte posterior | Sí |
| La variable de riesgo reproduce la regla del 70 % | Sí |
| Solo 3 columnas contienen información posterior al corte | Sí |
| Las cifras de la guía y del informe coinciden con las tablas | 16 de 16 |

### 3.2 Hallazgos

| # | Hallazgo | Gravedad | Estado |
|---|---|---|---|
| 1 | 68 relatos tienen como texto "NA" o "N/A". Las tablas los tratan bien (quedan como "Sin retraso declarado"), pero quien abra el CSV con un programa estadístico puede verlos como celda vacía | Baja | Documentado aquí; el libro de Excel no tiene el problema |
| 2 | La variable de riesgo marca entre 44 % y 48 % de las metas en los cortes de diciembre y solo 11 % en septiembre. Es un efecto de la regla (supone avance parejo en el año), no de la gestión | Media | Resuelto el 12 de noviembre: se adoptó el rezago relativo |
| 3 | La categoría fusionada de barreras acierta 44 % | Media | Se deja como referencia; no usar como variable |
| 4 | Las lecturas que miden el acierto las hizo un solo lector (el asistente de IA) | Media | Pendiente: que el equipo revise una parte |
| 5 | Faltan los PDF por entidad de los cuatro cortes de 2025 | Media | Pendiente: descargarlos |
| 6 | El archivo de configuración apunta a carpetas del computador de Adrian | Media | Resuelto: los datos van dentro del repositorio y las rutas son relativas |
| 7 | El README todavía describe el ejercicio bancario | Baja | Resuelto |
| 8 | El código y los datos del ejercicio bancario siguen en el repositorio | Baja | Resuelto: retirado del repositorio junto con `services/` (se conservan en una carpeta aparte, fuera de él) |
| 9 | No hay pruebas automáticas en la carpeta `tests/`, y el archivo `poetry.lock` no incluye las dos librerías nuevas | Baja | Resuelto: 7 pruebas y `poetry.lock` regenerado |

Ningún hallazgo afecta la exactitud de las cifras de las tablas.

### 3.3 Dato útil para el modelo

De las 2.975 filas que tienen dato del corte siguiente, el 30 % queda marcado en riesgo con la regla actual. Es un desbalance moderado, manejable con las métricas que el anteproyecto ya prevé (PR-AUC, F1 y sensibilidad).

## 4. Actualización: los cinco puntos previos al tablero

| Punto | Qué se hizo | Resultado |
|---|---|---|
| 1. Eficiencia DEA | Modelo BCC por grupos de tipo de anualización y sector, con prueba de estabilidad | 107 de 113 grupos estables; puntaje para 275 de 425 metas en el último corte |
| 2. Variable de riesgo | Tres definiciones calculadas; la principal es el rezago relativo | Marca una fracción estable en todos los cortes, sin el efecto de calendario de la regla anterior |
| 3. Modelo predictivo | Partición temporal, cuatro conjuntos de variables, prueba de la mejora | El modelo integrado supera a la línea base financiera; DEA y texto aún no muestran aporte propio |
| 4. PDF de 2025 | Se revisó el portal de la SDP | No existen: esos cortes solo se publicaron en Excel |
| 5. Repositorio | Datos de entrada incluidos, versiones fijadas, README nuevo, ejercicio bancario movido a `legado_churn/`, 7 pruebas automáticas | Reproducible: `python scripts/reproducir.py` se probó en una copia limpia |

Durante este trabajo se detectaron y corrigieron tres errores propios antes de reportar: la regla de rezago marcaba 60 % de las metas en diciembre por un empate; la comparación de modelos mezclaba algoritmos distintos, lo que inflaba el aporte del texto; y la asociación barreras–eficiencia mezclaba cortes de distinta época del año. El detalle de los resultados está en [RESULTADOS.md](RESULTADOS.md).

## 4b. Actualización del 12 de noviembre de 2026

| Qué | Resultado |
|---|---|
| Corte de septiembre de 2026 | Incorporado: ahora hay 9 cortes. Solo trae Excel, sin relatos |
| Definición de riesgo | Rezago relativo, 20 % más bajo dentro del mismo tipo de anualización; elegida tras comparar nueve variantes |
| Probabilidades del modelo | Se dejó de sobreponderar los casos de riesgo: la probabilidad ahora se puede leer como tal |
| Niveles de alerta | Bandas fijas: alta desde 50 %, media desde 20 % |
| Tablero | Siete gráficas, con el valor de cada marca al pasar el cursor |
| Verificación | `reproducir.py` comprueba también que el tablero corresponde a las tablas |

## 4c. Actualización del 13 de noviembre de 2026: rigor del modelo predictivo

| Mejora | Qué se hizo | Resultado |
|---|---|---|
| Costos de error asimétricos | El umbral de alerta minimiza 5 × rezagos omitidos + 1 × falsas alarmas; se fija con la fórmula 1/(1+5) = 16,7 %. Se reporta también F2 | Costo 225 frente a 231 con el umbral de F1; tabla de sensibilidad para razones de 1 a 10 |
| Calibración de probabilidades | Se elige en validación entre sin calibrar, Platt e isotónica, por error de Brier, con pliegues agrupados por meta | Platt, con mejora mínima (Brier 0,0834 frente a 0,0840): el modelo ya salía calibrado |
| Explicaciones con SHAP | Contribución de cada variable a cada predicción; global y por meta | Cada alerta del tablero muestra las tres variables que más la explican |

Al implementarlo se encontró y corrigió un efecto indeseado: la regresión isotónica crea empates que bajaban el PR-AUC de algunos conjuntos y hacían parecer verificable el aporte de DEA y texto. La capacidad de ordenar ahora se mide con las probabilidades sin calibrar, y la conclusión de H1 no cambia.

## 4d. Actualización del 19 de noviembre de 2026: nuevo tablero y ajustes del equipo

El tablero adopta el diseño «Foco PDD» (Veeduría Distrital) y se ajusta con las observaciones del equipo (documento [Ajustes_para_el_proyecto_Foco_PDD.docx](Ajustes_para_el_proyecto_Foco_PDD.docx) y revisiones posteriores). Detalle de uso y construcción en [TABLERO.md](TABLERO.md).

| Tema | Cambio |
|---|---|
| Diseño | `tablero/index.html` usa el diseño Foco PDD con los datos Gold. El diseño original quedó en `tablero/plantilla_foco_base.html` y los ajustes en `scripts/ajustar_*.py`, que `scripts/construir_plantilla.py` aplica en orden |
| Encabezado | Título y filtros en un recuadro fijo; fecha de corte visible; filtros reducidos a sector, entidad y meta |
| Panorama | Tarjetas: metas, % programado, % girado, % comprometido, rezagadas y alerta alta (promedios simples por meta; giros validados contra Gold) |
| Gráficas | Leyendas abajo y centradas; cada gráfica llena su celda; la franja gris sigue al año del corte |
| Bandeja de metas | Títulos de columna completos y fijos al bajar; «Eficiencia» se reemplaza por «Girado» |
| Detalle de la meta | Seis tarjetas con semáforo frente a lo esperado al corte; cabecera fija; relatos antes que gráficas; se quitan eficiencia, dinero vs. avance, riesgo y «Por qué este riesgo» |
| Actividades | Gráfica del avance de vigencia año por año del Plan al pasar el cursor; encabezado fijo |
| Regla de alerta | Las metas sin recursos comprometidos (ni en vigencias futuras) no llevan alerta; queda pendiente decidir el caso de las que sí tenían recursos programados |
| Entidades | Normalización con `data/raw/Normalizacion_Entidades.xlsx` (se completaron la Universidad Distrital y la EAAB); nueva tabla Silver `data/silver/entidades/entidad.csv` y columna `entidad_nombre_sigla` en Gold |
| Gold | `gold_actividad_corte` suma el avance físico de cada año del Plan (`fisico_*_<año>`) y los compromisos en vigencias futuras; dos controles nuevos de entidades y uno de la serie por año (19 en total) |
| Descargas | Archivos originales de la SDP por corte desde la barra lateral |
| Accesibilidad | Modo oscuro activable y uso cómodo en celular (Android e iOS) |
| Limpieza | Se retiraron el tablero anterior (`app.js`, `estilos*.css`, `graficas.js`, `plantilla.html`) y los borradores de diseño |

## 5. Qué falta frente al anteproyecto

| Objetivo | Estado |
|---|---|
| 1. Eficiencia con DEA | Hecho. Pendiente: probar otro producto donde haya magnitudes comparables |
| 2. Barreras y su relación con la eficiencia | Hecho: asociación significativa en los tres cortes con datos |
| 3. Modelo predictivo | Hecho con definición de riesgo provisional. Pendiente: acordar la definición y conseguir relatos de 2025 |
| Tablero | Hecho, con gráficas |

## 6. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Tablas | `data/gold/` y `data/gold/gold_pdd.xlsx` |
| Uso y construcción del tablero | `docs/TABLERO.md` |
| Resultados de eficiencia, barreras y modelo | `docs/RESULTADOS.md` |
| Explicación de tablas y método | `docs/GUIA_GOLD_Y_NLP.md` |
| Medición del acierto, en detalle | `docs/AUDITORIA.md` |
| Lista de expresiones de cada barrera | `configs/barreras.yaml` |
| Relatos leídos para la medición | `auditoria/etiquetas_barreras.csv` |
