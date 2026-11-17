# Resultados: eficiencia, barreras y modelo predictivo

Fecha: 13 de noviembre de 2026. Datos: 425 metas producto en 9 cortes trimestrales (sep-2024 a sep-2026). Escrito para quien conoce de indicadores pero no programa.

## Resumen frente al anteproyecto

| Pregunta del anteproyecto | Respuesta con los datos actuales |
|---|---|
| ¿Hay diferencias de eficiencia que la ejecución presupuestal no explica? (hipótesis auxiliar 1) | **Sí.** La eficiencia y el porcentaje de compromisos se parecen poco (relación de 0,34 en una escala de 0 a 1) |
| ¿Las barreras narradas se asocian con menor eficiencia? (hipótesis auxiliar 2) | **Sí**, en los tres cortes donde se pudo probar |
| ¿El modelo integrado anticipa mejor el rezago que uno solo financiero? (hipótesis central H1) | **Sí**, con mejora verificable |
| ¿Esa mejora se debe a la eficiencia DEA y al texto? | **No se puede afirmar.** La mejora viene del avance físico; DEA y texto no añaden nada verificable todavía |

El último punto es el más importante para no sobreinterpretar: H1 se cumple tal como está escrita, pero la parte novedosa del proyecto (DEA y texto como predictores) aún no demuestra aporte.

## 1. Eficiencia técnica (DEA)

### Qué se hizo

- **Qué se compara:** cada meta producto en cada corte, contra las metas de su mismo tipo de anualización y su mismo sector.
- **Insumo y producto:** recursos comprometidos del año frente a avance físico oficial del año (contado hasta 100 %).
- **Modelo:** BCC orientado al producto. Responde: con el mismo dinero, ¿cuánto más avance lograron las mejores metas comparables?
- **Grupos pequeños:** los de menos de 8 metas no se evalúan, porque con tan pocas casi todas quedarían "eficientes".

### Cómo leer el puntaje

Una eficiencia de 1 significa que ninguna meta comparable logró más avance con igual o menos dinero. Una eficiencia de 0,6 significa que la meta alcanzó el 60 % del avance que lograron las mejores de su grupo con esos recursos. Es una medida **relativa al grupo**: no dice si la meta es buena o mala en términos absolutos.

### Qué se encontró

| Dato | Valor |
|---|---|
| Grupos evaluados (grupo y corte) | 129 |
| Grupos estables al cambiar el insumo de compromisos a giros | 123 |
| Metas-corte con puntaje utilizable | 2.289 de 3.400 |
| Corte de septiembre de 2026: metas con puntaje | 295 de 425 |
| Corte de septiembre de 2026: eficiencia mediana | 0,81 |
| Corte de septiembre de 2026: metas en la frontera | 72 |

Unas 130 metas por corte quedan sin puntaje: pertenecen a grupos pequeños, a grupos inestables o no comprometieron recursos. El anteproyecto ya preveía esta exclusión.

### Límites

- **En diciembre el DEA distingue poco.** Al cierre del año la mayoría de las metas llega a 100 % y unas 200 de 295 quedan en la frontera. La medida es más informativa en marzo, junio y septiembre.
- **El producto es un porcentaje de cumplimiento, no una cantidad física.** Dos metas al 80 % pueden representar esfuerzos muy distintos. Por eso la comparación se limita a metas del mismo sector y tipo.
- **No se aplicó Frontera Estocástica (SFA).** Los grupos son pequeños (se aceptan desde 8 metas), con muy pocas unidades para estimar una frontera paramétrica; el anteproyecto la dejaba condicionada a esto.

## 2. Barreras y eficiencia

Se comparó la eficiencia de las metas que narran un problema con la de las que no, **dentro de cada corte** (para no confundir el efecto con la época del año).

| Corte | Metas que narran problema | Eficiencia mediana si narran problema | Eficiencia mediana si no | ¿Diferencia significativa? |
|---|---|---|---|---|
| 31/12/2024 | 49 | 0,83 | 1,00 | Sí |
| 31/03/2026 | 48 | 0,16 | 0,38 | Sí |
| 30/06/2026 | 60 | 0,42 | 0,67 | Sí |

El mismo patrón aparece para las barreras de contratación y de trámites y permisos en los tres cortes. Para talento humano y demanda hay muy pocos casos y no se observa diferencia.

Es una **asociación, no una causa**: no se puede saber si la barrera redujo la eficiencia o si las metas con bajo avance son las que más explican sus dificultades.

El corte de septiembre de 2026 no entra en esta prueba porque la SDP no publicó sus relatos.

## 3. Variable de riesgo

### La definición elegida: rezago relativo

> Una meta está **rezagada** en un corte si su avance físico del año está en el 20 % más bajo entre las metas de su mismo tipo de anualización. El modelo anticipa si la meta estará rezagada en el corte siguiente.

Se compara con metas del mismo tipo de anualización (Suma, Constante o Creciente) porque avanzan de forma distinta a lo largo del año. Así una meta que entrega por hitos no queda marcada solo por estar a mitad de año.

### Por qué esta variante y no otra

El equipo eligió el rezago relativo. Para decidir su forma exacta se compararon nueve variantes: tres fracciones (20 %, 25 % y 33 % más bajo) y tres grupos de comparación. Cada una se juzgó con dos preguntas:

- **Validez:** ¿la etiqueta señala subejecución real? Se mira diciembre, el único momento en que el avance del año es exigible completo. *Precisión*: de las metas marcadas en diciembre, cuántas cerraron por debajo de 90 %. *Cobertura*: de las que cerraron por debajo de 90 %, cuántas quedaron marcadas.
- **Anticipación:** ¿el modelo logra anticiparla? Se mide con ROC-AUC en los cortes de prueba (0,5 es adivinar al azar; 1 es acertar siempre).

| Comparada con | Fracción | Validez: precisión | Validez: cobertura | Anticipación (ROC-AUC) | Veces mejor que el azar |
|---|---|---|---|---|---|
| Todas las metas | 20 % | 88,8 % | 92,1 % | 0,855 | 3,4 |
| Todas las metas | 25 % | 76,6 % | 100 % | 0,859 | 2,8 |
| Todas las metas | 33 % | 66,1 % | 100 % | 0,855 | 2,2 |
| **Mismo tipo de anualización** | **20 %** | **84,9 %** | **89,0 %** | **0,900** | **3,7** |
| Mismo tipo de anualización | 25 % | 76,7 % | 98,2 % | 0,878 | 2,9 |
| Mismo tipo de anualización | 33 % | 66,9 % | 100 % | 0,854 | 2,2 |
| Mismo tipo y sector | 20 % | 80,9 % | 77,4 % | 0,884 | 3,1 |
| Mismo tipo y sector | 25 % | 75,4 % | 80,5 % | 0,843 | 2,4 |
| Mismo tipo y sector | 33 % | 72,8 % | 86,6 % | 0,831 | 2,0 |

Lectura:

- **El 20 % es mejor que el 25 % o el 33 %** en cualquier grupo: con fracciones mayores se marcan metas que en realidad cierran bien el año (la precisión cae de 85–89 % a 66–77 %).
- **Comparar por tipo de anualización es lo que mejor anticipa el modelo** (0,900) y conserva una validez alta.
- **Comparar con todas las metas** tiene una validez algo mayor (88,8 % frente a 84,9 %), pero el modelo la anticipa peor y pierde la razón metodológica: mezcla metas que avanzan a ritmos distintos.
- **Comparar por tipo y sector** deja grupos muy pequeños y la fracción marcada oscila entre 17 % y 29 % según el corte.

Salvedad: la columna de anticipación se midió en los mismos cortes de prueba que luego se usan para evaluar el modelo, así que favorece ligeramente a la variante elegida. Las diferencias entre las tres mejores son pequeñas. La columna de validez no tiene ese problema, y es la que sustenta con más firmeza preferir el 20 %.

La comparación completa está en `gold_comparacion_riesgo`.

### Las otras dos definiciones

Se conservan en la tabla como referencia:

| Definición | Qué marca | Proporción marcada |
|---|---|---|
| Regla lineal | El avance queda bajo el 70 % de lo esperado con avance parejo en el año | 11 % a 48 % según el corte |
| Cierre de año | La meta cierra diciembre con avance inferior a 90 % | 16 % a 23 % |

## 4. Modelo predictivo

### Cómo se evaluó

| Parte | Cortes | Filas |
|---|---|---|
| Entrenamiento | dic-2024, mar-2025, jun-2025, sep-2025 | 1.700 |
| Elección del modelo | dic-2025 | 425 |
| Prueba | mar-2026, jun-2026 | 850 |

Se entrena con el pasado y se mide con el futuro, nunca al revés. Se compararon cuatro conjuntos de variables con el mismo algoritmo (árboles potenciados), cada uno añadiendo algo al anterior. El corte de septiembre de 2026 aporta el resultado conocido de junio de 2026, lo que permitió ampliar la prueba.

### Resultado (cortes de prueba)

Se reportan dos tipos de medida:

- **Capacidad de ordenar las metas** (PR-AUC): ¿pone arriba a las que de verdad se rezagan? Va de 0 a 1; un modelo que adivinara al azar obtendría 0,205. Se mide con las probabilidades sin calibrar, para que la calibración no interfiera en la comparación entre conjuntos.
- **Resultado de las alertas**: con el umbral de decisión (sección siguiente), cuántos rezagos se detectan y cuántas falsas alarmas se generan.

| Variables | PR-AUC | Sensibilidad | Precisión | F2 | Mejora en PR-AUC sobre la línea base |
|---|---|---|---|---|---|
| 1. Solo financieras (línea base) | 0,367 | 0,37 | 0,33 | 0,36 | — |
| 2. Financieras + físicas | 0,767 | 0,81 | 0,77 | 0,80 | +0,394 (verificable) |
| 3. Financieras + físicas + DEA | 0,780 | 0,82 | 0,69 | 0,79 | +0,407 (verificable) |
| 4. Integrado (+ texto) | 0,756 | 0,80 | 0,74 | 0,79 | +0,383 (verificable) |

"Verificable" significa que, al repetir la medición 2.000 veces con distintas muestras de metas, la mejora nunca desaparece (para el modelo integrado va de +0,31 a +0,46). F2 es una medida que pesa la sensibilidad el doble que la precisión, coherente con que omitir un rezago es lo más costoso.

### Qué significa

- **La línea base financiera predice poco.** Saber cuánto dinero se comprometió casi no anticipa el rezago físico.
- **El avance físico es lo que predice.** Añadirlo duplica el desempeño. Las variables que más pesan son el avance del año y si la meta ya está rezagada.
- **DEA y texto no añaden nada verificable.** Frente al modelo financiero + físico, el aporte conjunto es de −0,011 (entre −0,031 y +0,009): indistinguible de cero.

### Por qué el texto no aporta (todavía)

Solo 4 de los 9 cortes tienen relatos, y de los cuatro cortes de entrenamiento solo uno. El modelo casi no tuvo de dónde aprender a usar el texto. No es evidencia de que el texto no sirva; es que hoy no se puede medir bien.

La SDP **no publicó** el PDF por entidad en ningún corte de 2025 ni en septiembre de 2026 (se verificó en el portal: esas publicaciones solo traen Excel). Para tenerlos habría que pedirlos directamente a la SDP.

### Umbral de alerta por costos

No todos los errores cuestan lo mismo. **Omitir** una meta que sí se rezaga pierde la ventana para corregirla; **revisar** una que al final no se rezagó cuesta unas horas de análisis. Por eso el umbral de alerta no se elige con F1 (que trata ambos errores igual), sino minimizando el costo:

> Costo = 5 × rezagos omitidos + 1 × falsas alarmas

La razón 5 a 1 es un **supuesto del equipo**, no una cifra oficial; se cambia en `configs/pdd.yaml`.

Con probabilidades calibradas, el umbral que minimiza ese costo tiene una fórmula: conviene alertar si la probabilidad de rezago es al menos 1 / (1 + 5) = **16,7 %**. Se prefirió esta fórmula a buscar el umbral en el corte de validación, porque no depende de un solo corte.

Resultado en los cortes de prueba (850 metas-corte, 174 rezagos reales), modelo integrado:

| Umbral | Metas señaladas | Rezagos detectados | Rezagos omitidos | Falsas alarmas | Costo |
|---|---|---|---|---|---|
| Por costos (16,7 %) | 189 | 139 | 35 | 50 | 225 |
| Por F1 (como antes) | — | — | — | — | 231 |

La mejora frente a F1 es pequeña, porque en estos datos el umbral de F1 ya quedaba cerca. La ventaja principal es otra: el umbral ahora se justifica con una regla explícita y discutible, no con una métrica abstracta.

**¿Y si la razón no fuera 5 a 1?** La tabla `gold_modelo_costos` muestra el efecto:

| Omitir cuesta… | Umbral | Metas señaladas | Rezagos detectados | Rezagos omitidos | Falsas alarmas |
|---|---|---|---|---|---|
| Igual que una falsa alarma | 50,0 % | 137 | 108 | 66 | 29 |
| 2 veces más | 33,3 % | 166 | 130 | 44 | 36 |
| 3 veces más | 25,0 % | 172 | 133 | 41 | 39 |
| **5 veces más (configurado)** | **16,7 %** | **189** | **139** | **35** | **50** |
| 10 veces más | 9,1 % | 258 | 146 | 28 | 112 |

Pasar de 1 a 5 detecta 31 rezagos más a cambio de 21 falsas alarmas más. Pasar de 5 a 10 detecta solo 7 más a cambio de 62 falsas alarmas: a partir de 5 el beneficio se aplana.

### Calibración de las probabilidades

Si el tablero dice "30 % de riesgo", de cada 100 metas con ese valor deberían rezagarse cerca de 30. Se probaron tres opciones y se eligió, en el corte de validación, la de menor error de Brier (el promedio de la diferencia al cuadrado entre la probabilidad y lo que pasó):

- dejar el modelo como está;
- **escalamiento de Platt** (una curva en forma de S);
- **regresión isotónica** (una escalera creciente).

Para evitar optimismo, la calibración se ajusta con 5 grupos de metas: una misma meta nunca queda a la vez en la parte que entrena y en la que calibra.

**Resultado:** para el modelo integrado se eligió Platt, pero la mejora es mínima (error de Brier de 0,0834 frente a 0,0840 sin calibrar). Los árboles potenciados de este proyecto se entrenan minimizando el error de probabilidad, así que ya salían razonablemente calibrados. Se midió en lugar de suponerlo.

La tabla `gold_modelo_calibracion` muestra la confiabilidad por décimos de metas. En los ocho décimos de menor riesgo la probabilidad anunciada (entre 1 % y 14 %) se parece a lo observado (entre 0 % y 16 %). En el noveno décimo el modelo **se queda corto**: anuncia en promedio 52 % y se rezagó el 72 %. Es decir, las probabilidades intermedias son conservadoras; una meta con 50 % está en más riesgo del que dice el número.

### Por qué el modelo da cada alerta (SHAP)

Cada alerta trae su explicación: las tres variables que más suben o bajan el riesgo de esa meta, calculadas con SHAP (valores de Shapley). Aparece en la ficha de cada meta en el tablero y en `gold_modelo_explicacion` (cinco variables por meta).

Ejemplo, meta con 92,9 % de riesgo:

> Avance del año: 0 % (sube el riesgo); Ya rezagada en este corte: sí (sube el riesgo); Avance del cuatrienio: 100 % (sube el riesgo)

Visto en conjunto (`gold_modelo_importancia`), las variables que más mueven las predicciones son:

| Variable | Contribución media (SHAP) | Importancia por permutación |
|---|---|---|
| Época del año del corte | 0,67 | 0,009 |
| Avance del año | 0,51 | 0,199 |
| Ya rezagada en este corte | 0,37 | 0,085 |
| Eficiencia DEA | 0,22 | 0,010 |
| Número de actividades | 0,20 | 0,007 |
| Avance del cuatrienio | 0,19 | 0,014 |

Las dos columnas responden preguntas distintas. SHAP dice **cuánto usa** el modelo cada variable; la permutación dice **cuánto empeora** si se le quita. La eficiencia DEA es un buen ejemplo: el modelo la usa (cuarta en SHAP), pero casi no pierde nada sin ella, porque su información ya está en el avance físico. Eso es coherente con que su aporte no sea verificable.

Dos advertencias:

- **SHAP explica el modelo, no las causas del rezago.** "Época del año" pesa porque el rezago se reparte distinto según el trimestre, no porque el calendario lo provoque.
- **Las explicaciones ayudan a encontrar problemas en los datos.** En el ejemplo, una meta con el cuatrienio cumplido (100 %) aparece rezagada porque reporta 0 % en el año: probablemente no tiene programación para 2026. Hay 3 casos así entre las 87 metas rezagadas de septiembre de 2026 (16 en toda la historia). El equipo debería decidir si esas metas se excluyen de la etiqueta de rezago.

### Alertas del último corte

Con el modelo entrenado sobre todos los cortes con resultado conocido, para el corte de septiembre de 2026 (`gold_prediccion_riesgo`):

| Nivel de alerta | Probabilidad estimada de rezago en diciembre de 2026 | Metas |
|---|---|---|
| Alta | 50 % o más | 52 |
| Media | Entre 16,7 % (umbral por costos) y 50 % | 40 |
| Baja | Menos de 16,7 % | 333 |

Toda meta en alerta alta o media supera el umbral por costos: revisarla cuesta, en promedio, menos que omitirla. Una alerta señala una meta para revisar; no prueba que vaya a incumplir.

## 5. Qué habría que hacer para fortalecer los resultados

1. **Pedir a la SDP los PDF por entidad de 2025 y de septiembre de 2026.** Es lo único que permitiría medir de verdad el aporte del texto.
2. **Volver a evaluar cuando se publique diciembre de 2026.** Será el segundo cierre de año completo y permitirá probar la definición de "cierre de año".
3. **Probar DEA con un producto distinto del porcentaje de cumplimiento** en los sectores donde exista una magnitud física comparable.
4. **Acordar la razón de costos** entre omitir un rezago y dar una falsa alarma con quienes usarían las alertas; hoy es un supuesto (5 a 1).
5. **Decidir qué hacer con las metas sin programación en el año**, que hoy pueden quedar marcadas como rezagadas.
