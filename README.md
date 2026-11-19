# Eficiencia técnica y riesgo de subejecución en el PDD "Bogotá Camina Segura"

Trabajo de grado de la Maestría en Ciencia de Datos, Universidad Santo Tomás.
Equipo: Jhonatan Smith Doncel, Jorge Emmanuel Marín, Adrian Felipe Grateron. Director: Carlos Isaac Zainea.

El proyecto integra tres fuentes de seguimiento del Plan Distrital de Desarrollo 2024–2027 (avance físico, gestión e inversión, y los relatos de las entidades) para:

1. medir la **eficiencia técnica** de las metas producto con Análisis Envolvente de Datos (DEA);
2. identificar en los relatos las **barreras** de ejecución y relacionarlas con la eficiencia;
3. **anticipar** qué metas quedarán rezagadas en el corte siguiente, con probabilidades calibradas, un umbral de alerta que pondera más omitir un rezago que dar una falsa alarma, y la explicación de cada alerta.

El anteproyecto está en `Ante-proyecto-final.pdf`.

## Qué leer primero

| Documento | Para qué |
|---|---|
| [docs/RESULTADOS.md](docs/RESULTADOS.md) | Qué se encontró en eficiencia, barreras y modelo predictivo |
| [docs/GUIA_GOLD_Y_NLP.md](docs/GUIA_GOLD_Y_NLP.md) | Qué contiene cada tabla y cómo se lee el texto de los reportes |
| [docs/AUDITORIA.md](docs/AUDITORIA.md) | Cómo se verificó que los datos y la clasificación son confiables |
| [docs/TABLERO.md](docs/TABLERO.md) | Cómo se usa el tablero, qué reglas aplica y cómo se reconstruye |
| [docs/DECISIONES_GRAFICAS.md](docs/DECISIONES_GRAFICAS.md) | Por qué cada gráfica del tablero es como es |
| [docs/ACUERDOS_CON_LA_ENTIDAD.md](docs/ACUERDOS_CON_LA_ENTIDAD.md) | Decisiones que hay que acordar con quienes usarán las alertas, con espacio para registrarlas |
| [docs/MEJORAS.md](docs/MEJORAS.md) | Qué se ha mejorado y qué falta (incluye la bitácora de actualizaciones) |
| [docs/Ajustes_para_el_proyecto_Foco_PDD.docx](docs/Ajustes_para_el_proyecto_Foco_PDD.docx) | Ajustes al tablero solicitados por el equipo |

Las tablas están en `data/gold/` (CSV) y reunidas en `data/gold/gold_pdd.xlsx`.

El tablero para consultar los resultados es `tablero/index.html`: se abre con doble clic y funciona sin conexión. Tiene modo oscuro: el botón con la luna, a la izquierda de «Fecha de corte», lo activa y lo desactiva, y el navegador recuerda la elección. También se puede usar desde el celular (Android e iOS): el menú pasa a una barra inferior, las tablas se muestran como tarjetas y la gráfica de cada actividad se abre al tocar la fila. En la barra lateral se pueden descargar los archivos originales de la SDP de cada corte (informe por entidad en PDF, Avance del Plan y Gestión-Inversión en Excel); esos botones enlazan a `data/raw/`, así que funcionan al abrir el tablero dentro de la carpeta del repositorio.

## Cómo reproducir los resultados

El repositorio trae todo lo necesario: los datos de entrada (`data/silver/` y `data/raw/`, 60 MB), el código y los resultados publicados (`data/gold/`). No hace falta descargar nada más ni configurar rutas.

Requisito: Python 3.14 (los resultados se generaron y se probaron con 3.14.3, en Windows). Las versiones 3.12 y 3.13 deberían servir, pero no se han probado; tampoco Linux ni macOS.

1. Creamos un entorno e instalamos las versiones exactas:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

En Linux o macOS, use `.venv/bin/python` en lugar de `.venv\Scripts\python`. Quien prefiera Poetry puede usar `poetry install --with dev`; `poetry.lock` fija las mismas versiones.

2. Ejecutamos la verificación completa:

```bash
.venv\Scripts\python scripts/reproducir.py
```

Tarda unos minutos y termina con `REPRODUCIDO: todo coincide.` si:

- los datos de entrada son exactamente los registrados en `data/FUENTES.csv`;
- las 9 pruebas automáticas pasan;
- las 20 tablas reconstruidas son iguales a las publicadas, columna por columna;
- la auditoría contra los Excel y PDF originales de la SDP no encuentra diferencias;
- el tablero regenerado es igual al publicado.

Este procedimiento se probó en una copia limpia del repositorio, con un entorno instalado desde cero.

### Otros comandos

| Comando | Qué hace |
|---|---|
| `python scripts/normalizar_entidades.py` | Normaliza las entidades en Silver a partir de `data/raw/Normalizacion_Entidades.xlsx` (antes de construir Gold) |
| `python scripts/construir_gold.py` | Regenera las tablas de `data/gold/` (sobrescribe las publicadas) |
| `python scripts/auditar_gold.py` | Compara las tablas con los archivos originales de la SDP |
| `python -m pytest -q` | Ejecuta las pruebas automáticas |
| `python scripts/construir_plantilla.py` | Reconstruye el diseño del tablero (`tablero/plantilla_foco.html`) aplicando los ajustes `scripts/ajustar_*.py` al diseño original |
| `python scripts/generar_tablero.py` | Regenera `tablero/index.html` a partir de las tablas de `data/gold/` |
| `python scripts/actualizar_todo.py <carpeta data del scraper>` | Cuando hay un corte nuevo: trae los datos, reconstruye las tablas, regenera el tablero y audita |

### Qué garantiza y qué no

- **Mismos datos, mismo código, mismas versiones → mismos resultados.** Los pasos con azar (modelo y remuestreo) usan una semilla fija.
- **Entre equipos distintos** pueden aparecer diferencias de redondeo en la sexta cifra decimal; la verificación las tolera.
- **Con otras versiones de las librerías** el modelo podría dar cifras ligeramente distintas. Por eso las versiones están fijadas.
- **Las lecturas de la auditoría del texto** (`auditoria/etiquetas_barreras.csv`) son un insumo: se hicieron una vez y se conservan tal cual.

### De dónde vienen los datos

Los publica la Secretaría Distrital de Planeación en su portal de seguimiento a la inversión. `data/FUENTES.csv` registra, por archivo, la dirección de descarga, la fecha y su huella digital. Los tres archivos de `data/silver/` son la consolidación de esos originales hecha por el *scraper* del equipo (proyecto aparte).

Para trabajar con una descarga más reciente, copie `configs/pdd.local.ejemplo.yaml` como `configs/pdd.local.yaml` y escriba ahí las rutas de la nueva descarga. Los resultados cambiarán y `reproducir.py` lo señalará; es lo esperado.

## Limitaciones conocidas

- Solo 4 de los 9 cortes tienen relatos de las entidades: la SDP no publicó los demás.
- La eficiencia DEA distingue poco en los cortes de diciembre, cuando casi todas las metas llegan a 100 %.
- El clasificador de barreras acierta 94,5 % al señalar que un relato narra un problema y 74,6 % al señalar cuál. Una de las seis categorías es poco fiable y aparece marcada como "solo referencia".
- Las lecturas con que se midió ese acierto las hizo un solo lector (un asistente de IA) y no se han contrastado con una segunda persona.
- El modelo supera a la línea base financiera, pero la eficiencia DEA y el texto aún no muestran aporte propio como predictores.
- El umbral de alerta supone que omitir un rezago cuesta 5 veces más que una falsa alarma. Es un supuesto del equipo; `gold_modelo_costos` muestra el efecto de otras razones.
- Las explicaciones de cada alerta (SHAP) describen el modelo, no las causas del rezago.
- La relación entre barreras y menor eficiencia es una asociación, no una causa.
- Probado en Windows con Python 3.14.3.

## Pendiente por validar

**Alerta en metas sin recursos comprometidos.** El tablero no muestra alerta ni puntaje de riesgo para una meta que, en el último corte, tiene 0 % comprometido (o sin dato) y no tiene compromisos en vigencias futuras: si no se comprometió nada, no hay compromiso que vigilar. La regla se aplica al generar el tablero (`scripts/generar_tablero.py`); Gold y el modelo no cambian. En el corte del 30/09/2026 afecta a 15 metas (las alertas altas pasan de 52 a 42) y ninguna meta registra compromisos en vigencias futuras.

Falta decidir qué hacer con las 5 de esas metas que **sí tienen recursos programados para el año pero no comprometieron nada**: 2023, 2065, 2150, 2216 y 2218 (esta última con cerca de 48.000 millones programados). Hoy quedan sin alerta como las demás, pero que no se haya comprometido dinero programado podría ser justamente una señal de alerta. Las otras 10 no tenían recursos programados en el año.

## Estructura

```text
configs/      pdd.yaml (parámetros), barreras.yaml (expresiones de cada barrera)
pdd/          código: lectura de PDF, barreras, DEA, modelo, tablas Gold, auditoría
scripts/      reproducir.py, construir_gold.py, auditar_gold.py, normalizar_entidades.py, generar_tablero.py,
              construir_plantilla.py y los ajustes de diseño del tablero (ajustar_*.py)
auditoria/    relatos leídos por una persona para medir el acierto del clasificador
data/silver/  datos de entrada consolidados por el scraper, más las entidades normalizadas (entidades/)
data/raw/     archivos originales de la SDP (PDF por entidad y Excel de los últimos cortes) y Normalizacion_Entidades.xlsx
data/gold/    tablas resultantes
tablero/      index.html (tablero final), plantilla_foco.html (diseño con ajustes) y plantilla_foco_base.html (diseño original)
docs/         documentación para lectores no técnicos (incluye TABLERO.md)
tests/        pruebas automáticas
```

## Advertencia de uso

Los puntajes de eficiencia, las barreras y las alertas son señales para priorizar la revisión. No constituyen evidencia de irregularidad, incumplimiento ni responsabilidad institucional.
