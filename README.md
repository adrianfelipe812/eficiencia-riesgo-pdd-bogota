# Evaluación de la eficiencia técnica y predicción de riesgos en el Plan de Desarrollo Distrital de Bogotá 2024–2028

> Anteproyecto de investigación — Facultad de Estadística, Universidad Santo Tomás, seccional Bogotá.

## Resumen

Este proyecto propone evaluar la eficiencia técnica y anticipar riesgos de ineficiencia en la ejecución de las metas-producto del Plan de Desarrollo Distrital (PDD) de Bogotá 2024–2028. La propuesta integra el Análisis Envolvente de Datos (DEA), técnicas de Procesamiento de Lenguaje Natural (NLP) y modelos de clasificación de aprendizaje automático para relacionar recursos financieros, avances físicos y hallazgos de los informes institucionales.

El propósito es complementar el seguimiento basado principalmente en porcentajes de ejecución financiera con una lectura conjunta de resultados físicos y barreras operativas. El estudio se plantea como una investigación aplicada, no experimental, retrospectiva, longitudinal y analítico-predictiva. La información de seguimiento disponible hasta 2026 servirá como corte para el análisis y el desarrollo del prototipo.

**Estado del proyecto:** anteproyecto y diseño metodológico. Los documentos disponibles describen la propuesta; no reportan resultados empíricos de la aplicación del DEA ni métricas de desempeño de modelos predictivos ya entrenados.

## Problema de investigación

El seguimiento de la ejecución del PDD utiliza indicadores financieros que, por sí solos, no muestran si los recursos comprometidos o ejecutados se traducen en avances físicos oportunos. Además, los datos cuantitativos conviven con información narrativa sobre retrasos, barreras operativas, programación por hitos y otros factores de contexto. La fragmentación entre estas fuentes dificulta distinguir rezagos reales de gestión de situaciones explicadas por la programación o las características de cada meta.

La propuesta busca integrar estas fuentes para medir eficiencia relativa y explorar señales tempranas de riesgo de subejecución física.

## Pregunta de investigación

¿De qué manera la integración de modelos de eficiencia técnica y procesamiento de lenguaje natural permite evaluar, clasificar y anticipar ineficiencias en la ejecución de las metas-producto del Plan de Desarrollo Distrital de Bogotá?

## Objetivos

### Objetivo general

Evaluar la eficiencia técnica y predecir los riesgos de ineficiencia en la ejecución de las metas-producto del Plan de Desarrollo Distrital de Bogotá 2024–2028 mediante la integración de DEA, NLP e indicadores de gestión.

### Objetivos específicos

1. Estimar la eficiencia técnica relativa de metas-producto comparables, relacionando recursos financieros con avances físicos.
2. Extraer y categorizar barreras operativas y de gestión descritas en informes institucionales, y estudiar su asociación con las brechas de eficiencia.
3. Desarrollar un modelo de clasificación que identifique riesgos de subejecución física con la información institucional disponible hasta el corte analítico de 2026, con miras a generar alertas tempranas.

## Alcance y datos

- **Ámbito:** Plan de Desarrollo Distrital de Bogotá 2024–2028.
- **Población de referencia:** 425 metas-producto del PDD, según el documento metodológico.
- **Unidad de análisis:** metas-producto; para DEA se analizarán grupos comparables dentro de sectores homólogos, sujetos a disponibilidad y calidad de datos.
- **Fuentes previstas:** bases oficiales de seguimiento del PDD y SEGPLAN, datos de avance físico y financiero e informes institucionales narrativos en PDF o Excel.
- **Ventana analítica propuesta:** registros disponibles hasta 2026.
- **Resultado esperado:** un prototipo analítico para apoyar la identificación de brechas de eficiencia y riesgos de subejecución. La propuesta no afirma que el sistema ya esté desplegado en producción.

## Metodología propuesta

1. **Preparación de datos:** recopilar, depurar y homologar información financiera, física y narrativa; documentar la calidad y comparabilidad de las metas.
2. **Medición de eficiencia:** aplicar DEA a grupos comparables, usando recursos financieros como insumos y avances físicos o beneficiarios reportados como productos, según la disponibilidad de las variables.
3. **Análisis de informes:** extraer y normalizar texto de reportes institucionales; identificar y categorizar barreras operativas mediante técnicas de NLP.
4. **Modelado predictivo:** entrenar clasificadores para estimar riesgo de subejecución física. La metodología contempla validación temporal para reducir filtración de información futura (*data leakage*) y revisión de la importancia de las variables.
5. **Integración y evaluación:** relacionar los puntajes DEA, las variables extraídas del texto y los indicadores de gestión; evaluar el desempeño del modelo antes de proponer alertas.

El documento metodológico también menciona la Frontera Estocástica (SFA) como técnica considerada. Su inclusión definitiva deberá quedar alineada con el alcance metodológico y los datos que finalmente se validen.

## Avances del anteproyecto

- Formulación del problema con ejemplos de seguimiento de metas y avances reportados al 31 de marzo de 2026.
- Revisión de literatura organizada mediante preguntas guía sobre qué se estudia, cómo se estudia, qué se encontró y qué permanece pendiente.
- Identificación de brechas en la integración de eficiencia técnica, análisis de texto institucional y alertas tempranas para proyectos del PDD.
- Definición de pregunta, hipótesis, objetivo general y objetivos específicos.
- Delimitación inicial de población, variables, fuentes, diseño y fases metodológicas.
- Elaboración de cronograma de actividades y estimación presupuestal para alojamiento de datos en una capa de consulta analítica durante seis meses, con inicio proyectado para febrero de 2027. Los costos son estimaciones sujetas a cambios.
- Proyección de trabajo futuro: conexión con fuentes institucionales y SECOP II, análisis de documentos contractuales, seguimiento durante el cuatrienio y evaluación de replicabilidad en otros entes territoriales.

## Pipeline de datos (`pipeline/`)

Primera fase técnica del proyecto, con arquitectura por capas (Bronce → Silver):

| Notebook | Etapa |
|---|---|
| `01_descarga_ultimo_corte.ipynb` | Descarga las fuentes oficiales de la Secretaría Distrital de Planeación a `Capa Bronce` |
| `02_limpieza_avance_plan.ipynb` | Prepara las tablas de Avance del Plan |
| `03_limpieza_gestion_inversion.ipynb` | Prepara la base y los diccionarios de Gestión-Inversión |
| `04_extraccion_narrativas_gestion_inversion.ipynb` | Extrae del PDF oficial los relatos de retrasos, soluciones y logros |

`pipeline/Capa Silver/2026-06-30/` contiene los resultados limpios del corte del 30 de junio de 2026. La `Capa Bronce` no se versiona: se regenera ejecutando el notebook 01. Instrucciones de ejecución en `pipeline/README.md`.

## Prototipo

`prototipo/index.html` es un prototipo funcional (sin conexión, sin IA ni API) para focalizar el seguimiento de metas y actividades del PDD con datos reales de tres cortes de la auditoría publicados por la Secretaría Distrital de Planeación. Se abre directamente en el navegador. `prototipo/guia_completa.html` documenta la capa Gold propuesta.

> Los cálculos y observaciones del prototipo son de demostración y no constituyen un dictamen institucional.

## Estructura del repositorio

```text
├── pipeline/                    # Notebooks Bronce → Silver, rutas.py y Capa Silver
├── docs/anteproyecto.pdf        # Anteproyecto final (oct. 2026)
├── latex/                       # Fuente LaTeX de la versión resumida (plantilla USTA)
└── prototipo/
    ├── index.html               # Prototipo de focalización
    └── guia_completa.html       # Guía de la capa Gold
```

## Equipo

- Adrian Grateron
- Jhonatan Smith Doncel
- Jorge Emmanuel Marín

Coautor del anteproyecto: Carlos Isaac Zainea Maya

Facultad de Estadística — Universidad Santo Tomás, seccional Bogotá.

## Consideraciones

- Los puntajes DEA dependen de la comparabilidad entre metas y de la calidad de los insumos y productos disponibles.
- La clasificación de riesgos requiere definir operativamente la variable objetivo y validar que haya suficientes observaciones históricas.
- Los informes narrativos pueden variar en formato y detalle; su normalización y clasificación deben documentarse para hacer el análisis reproducible.
- Las cifras y estados citados en la propuesta corresponden al corte señalado en los documentos y no deben interpretarse como datos actuales en tiempo real.

## Licencia y uso de datos

No se especifica una licencia de software ni de datos en los documentos disponibles. Antes de publicar el repositorio, se recomienda definir la licencia y verificar las condiciones de uso, atribución y redistribución de cada fuente de datos institucional.
