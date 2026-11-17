# Acuerdos con la entidad usuaria de las alertas

Este documento reúne las decisiones que el sistema de alertas no puede tomar por sí solo: dependen de cómo trabaja la entidad que las va a usar (por ejemplo, el equipo de seguimiento preventivo de la Veeduría Distrital). Hoy cada una tiene un **valor provisional** elegido por el equipo del proyecto; el objetivo es reemplazarlo por un valor acordado y dejar constancia de por qué.

Está escrito para leerse en una reunión con la entidad. Cada acuerdo dice qué se decide, cuál es el valor actual, qué preguntar, qué consecuencias tiene cada opción y dónde se cambia. Al final hay un espacio para registrar lo acordado.

## Antes de empezar: qué es y qué no es una alerta

Conviene acordar esto primero, porque condiciona todo lo demás.

- Una alerta dice: *"esta meta tiene una probabilidad alta de quedar entre las más atrasadas de su tipo en el próximo corte trimestral"*.
- Una alerta **no** dice que la meta vaya a incumplir, que haya una irregularidad ni que la entidad responsable haya fallado. Es una señal para priorizar la revisión.
- Las explicaciones que acompañan cada alerta describen en qué se fijó el modelo, no las causas del rezago.

**Acuerdo 0.** La entidad acepta usar las alertas como apoyo para priorizar y no como conclusión sobre el desempeño de una entidad.

---

## Acuerdo 1. Cuánto más grave es omitir un rezago que revisar de más

**Qué se decide.** El sistema puede equivocarse de dos maneras:

- **Omitir** una meta que sí se rezaga: se pierde la oportunidad de advertir a tiempo.
- **Dar una falsa alarma:** el equipo revisa una meta que al final no se rezagó; se pierden unas horas de análisis.

El umbral de alerta depende de cuánto más grave es lo primero que lo segundo.

**Valor provisional: 5 a 1.** Omitir un rezago se considera 5 veces más grave que una falsa alarma. Con eso se alerta toda meta con 16,7 % o más de probabilidad de rezago. Es un supuesto del equipo del proyecto, no una cifra de la entidad.

**Pregunta para la entidad.** La forma más sencilla de obtener la razón es esta:

> Para no dejar pasar **una** meta que sí se va a rezagar, ¿cuántas metas que al final **no** se rezagan estaría dispuesto su equipo a revisar?

La respuesta es la razón. Si dicen "unas cinco", la razón es 5 a 1.

**Consecuencias de cada opción.** Medido en los cortes de marzo y junio de 2026 (174 rezagos reales en 850 metas-corte). La última columna es el promedio por corte trimestral.

| Razón | Se alerta desde | Rezagos detectados | Rezagos omitidos | Falsas alarmas | Metas a revisar por corte |
|---|---|---|---|---|---|
| 1 a 1 | 50,0 % | 108 | 66 | 29 | 69 |
| 2 a 1 | 33,3 % | 130 | 44 | 36 | 83 |
| 3 a 1 | 25,0 % | 133 | 41 | 39 | 86 |
| **5 a 1 (actual)** | **16,7 %** | **139** | **35** | **50** | **95** |
| 10 a 1 | 9,1 % | 146 | 28 | 112 | 129 |

Lectura para la reunión: pasar de 1 a 5 detecta 31 rezagos más a cambio de 21 falsas alarmas. Pasar de 5 a 10 detecta solo 7 más a cambio de 62 falsas alarmas.

**Dónde se cambia.** `configs/pdd.yaml`, campos `costo_rezago_no_detectado` y `costo_falsa_alarma`. La tabla completa se regenera en `data/gold/gold_modelo_costos.csv`.

---

## Acuerdo 2. Cuántas metas puede revisar el equipo en cada corte

**Qué se decide.** La razón del acuerdo 1 es un criterio de valor; este es un límite práctico. Si el equipo solo puede revisar a fondo 60 metas por trimestre, no sirve un umbral que señale 95.

**Valor provisional:** ninguno; hoy no hay límite.

**Pregunta para la entidad.** ¿Cuántas metas puede revisar el equipo con profundidad en cada corte trimestral, y en cuánto tiempo después de publicado el corte?

**Cómo se usa la respuesta.** Se elige la razón más alta de la tabla anterior cuyas "metas a revisar por corte" quepan en esa capacidad. Si la capacidad es menor que lo que pide la razón acordada en el acuerdo 1, hay que decirlo explícitamente: se aceptan más rezagos omitidos por falta de capacidad, no porque no importen.

---

## Acuerdo 3. Qué hace el equipo con cada nivel de alerta

**Qué se decide.** El tablero clasifica las metas en tres niveles. Falta acordar qué acción corresponde a cada uno.

**Valores provisionales** (corte de septiembre de 2026):

| Nivel | Probabilidad de rezago | Metas | Acción propuesta, por acordar |
|---|---|---|---|
| Alta | 50 % o más | 52 | Revisión a fondo y, si se confirma, comunicación a la entidad responsable |
| Media | Entre 16,7 % y 50 % | 40 | Revisión de escritorio: avance, dinero y relato de la entidad |
| Baja | Menos de 16,7 % | 333 | Seguimiento ordinario |

Un dato para la reunión: las probabilidades intermedias son conservadoras. Entre las metas con riesgo anunciado de alrededor de 50 %, en las pruebas se rezagó el 72 %. Una alerta media alta merece más atención de la que sugiere su número.

**Preguntas para la entidad.** ¿Qué acción concreta corresponde a cada nivel? ¿El corte de la alerta alta (50 %) les sirve, o prefieren otro?

**Dónde se cambia.** `configs/pdd.yaml`, campo `alerta_alta`. La alerta media empieza siempre en el umbral del acuerdo 1.

---

## Acuerdo 4. Qué cuenta como "meta rezagada"

**Qué se decide.** El modelo aprende a anticipar una definición de rezago. Si la entidad entiende "rezago" de otra forma, las alertas responderán a una pregunta distinta de la suya.

**Valor provisional.** Una meta está rezagada si su avance físico del año está en el 20 % más bajo entre las metas de su mismo tipo de anualización (Suma, Constante o Creciente). Se eligió tras comparar nueve variantes: en diciembre, el 85 % de las metas así marcadas cerraron el año por debajo de 90 %.

**Lo que conviene que la entidad sepa.** Es una definición **relativa**: siempre marca cerca de una quinta parte de las metas, aunque todas vayan bien. Responde a "¿cuáles son las más atrasadas?", no a "¿cuáles van a incumplir?".

**Preguntas para la entidad.** ¿Les sirve una definición relativa? ¿O necesitan una absoluta, como "cerrar el año por debajo de 90 %"? Esta segunda es más fácil de defender, pero hoy solo hay un año cerrado con datos completos; será evaluable cuando se publique diciembre de 2026.

**Dónde se cambia.** `configs/pdd.yaml`, sección `riesgo`. El sustento está en `docs/RESULTADOS.md` y `data/gold/gold_comparacion_riesgo.csv`.

---

## Acuerdo 5. Qué hacer con las metas sin programación en el año

**Qué se decide.** Algunas metas ya cumplieron su meta del cuatrienio y reportan 0 % de avance en el año, probablemente porque no tienen programación para ese año. Hoy pueden quedar marcadas como rezagadas, lo que genera alertas que no corresponden.

**Situación actual:** 3 de las 87 metas rezagadas en septiembre de 2026 están en ese caso (16 en toda la historia).

**Pregunta para la entidad.** ¿Esas metas deben excluirse de la etiqueta de rezago y de las alertas? ¿Conocen otros casos en que un 0 % no signifique atraso (por ejemplo, metas que entregan solo al final del año)?

**Dónde se cambia.** Requiere un ajuste en `pdd/modelo.py` (función `agregar_objetivos`). El equipo del proyecto lo implementa una vez acordado.

---

## Acuerdo 6. Cómo registrar si cada alerta se confirmó

**Qué se decide.** Hoy el acierto del sistema se mide con datos pasados. Para saber si sirve en la práctica, hay que registrar qué pasó con cada alerta.

**Valor provisional:** no hay registro.

**Propuesta.** Por cada meta revisada, una fila con: corte, código de la meta, nivel de alerta, si la revisión encontró un problema real (sí / no / no concluyente) y una nota breve. Con dos o tres cortes de registro se puede medir el acierto real y ajustar la razón del acuerdo 1.

**Preguntas para la entidad.** ¿Quién lleva el registro? ¿En qué formato les resulta práctico (hoja de cálculo compartida, formulario)?

---

## Acuerdo 7. Qué relatos de las entidades se pueden usar

**Qué se decide.** Las barreras narradas salen de los relatos "Retrasos y soluciones" de los reportes por entidad que publica la Secretaría Distrital de Planeación. La SDP no publicó esos reportes en los cortes de 2025 ni en septiembre de 2026, así que hoy solo hay relatos para 4 de 9 cortes.

**Preguntas para la entidad.**

- ¿Puede la entidad solicitar a la SDP los reportes por entidad que faltan? Es lo que más mejoraría la medición del aporte del texto.
- ¿Tiene la entidad otras fuentes narrativas (actas, informes de seguimiento) que se pudieran incorporar?

---

## Acuerdo 8. Una segunda lectura de los relatos

**Qué se decide.** El acierto del clasificador de barreras (94,5 % al detectar que un relato narra un problema; 74,6 % al identificar cuál) se midió con 180 relatos leídos por un solo lector, que fue un asistente de IA.

**Pregunta para la entidad.** ¿Puede un analista con experiencia en seguimiento leer una parte de esos relatos (por ejemplo, 50) para contrastar la lectura? El archivo es `auditoria/etiquetas_barreras.csv`; si se corrige alguna lectura, el acierto se recalcula solo.

---

## Acuerdo 9. Con qué frecuencia se actualiza y quién lo hace

**Valor provisional.** Cada vez que la SDP publique un corte trimestral, alguien del equipo descarga los datos con el *scraper* y ejecuta `python scripts/actualizar_todo.py`. Las cifras de `docs/RESULTADOS.md` se actualizan a mano.

**Preguntas para la entidad.** ¿En cuántos días después de publicado el corte necesitan las alertas? ¿Quién se hace cargo de la actualización cuando termine el proyecto académico?

---

## Acuerdo 10. Uso y circulación de las alertas

**Preguntas para la entidad.**

- ¿Quién puede ver el tablero? ¿Solo el equipo de seguimiento, o también las entidades responsables de las metas?
- ¿Se puede citar una alerta en una comunicación oficial? Si es así, ¿con qué advertencia sobre su alcance?
- ¿Qué pasa si una entidad responsable cuestiona una alerta? (Se sugiere que pueda pedir la explicación de la alerta y el relato que la sustenta, que ya están en el tablero).

---

## Registro de acuerdos

Completar en la reunión. Cuando un valor cambie, actualizar `configs/pdd.yaml`, ejecutar `python scripts/actualizar_todo.py` y dejar aquí la fecha.

| # | Acuerdo | Valor provisional | Valor acordado | Justificación de la entidad | Quién decidió | Fecha |
|---|---|---|---|---|---|---|
| 0 | Alcance de las alertas | Apoyo para priorizar, no conclusión | | | | |
| 1 | Razón de costos | 5 a 1 (umbral 16,7 %) | | | | |
| 2 | Capacidad de revisión | Sin límite | | | | |
| 3 | Acción por nivel | Alta ≥ 50 %; media ≥ umbral del acuerdo 1 | | | | |
| 4 | Definición de rezago | 20 % más bajo de su tipo de anualización | | | | |
| 5 | Metas sin programación en el año | Se incluyen | | | | |
| 6 | Registro de alertas confirmadas | No hay | | | | |
| 7 | Solicitud de relatos a la SDP | Pendiente | | | | |
| 8 | Segunda lectura de relatos | Pendiente | | | | |
| 9 | Frecuencia y responsable | Cada corte trimestral; equipo del proyecto | | | | |
| 10 | Circulación de las alertas | Sin definir | | | | |

**Asistentes a la reunión:**

**Fecha:**
