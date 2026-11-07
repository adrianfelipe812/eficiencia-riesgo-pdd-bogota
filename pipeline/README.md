# Seguimiento del Plan Distrital de Desarrollo

Los notebooks contienen la metodología, los parámetros y los controles de cada etapa:

1. `01_descarga_ultimo_corte.ipynb`: descarga las fuentes oficiales a `Capa Bronce` (requiere Internet).
2. `02_limpieza_avance_plan.ipynb`: prepara las tablas de Avance del Plan.
3. `03_limpieza_gestion_inversion.ipynb`: prepara la base y los diccionarios de Gestión-Inversión.
4. `04_extraccion_narrativas_gestion_inversion.ipynb`: extrae los relatos del PDF.

`Capa Bronce` conserva los originales y `Capa Silver` los resultados por fecha de corte. El único script, `rutas.py`, localiza la carpeta del proyecto. El diagnóstico previo de Gestión-Inversión se conserva como anexo Markdown del notebook 03.

## Uso en otro equipo

Comprime y envía la carpeta completa. Descomprímela e instala **Python 3.11 o posterior**. Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
python -m jupyterlab
```

Abre los notebooks y ejecuta sus celdas en orden. Selecciona el entorno de Python donde instalaste las dependencias. Puedes crear un entorno virtual local; no necesitas enviarlo a otro equipo.

Puedes cambiar el nombre o la ubicación de la carpeta. Conserva juntos los notebooks, `rutas.py` y las carpetas de datos. Inicia Jupyter desde esta carpeta y ejecuta las celdas de cada notebook en orden. Los notebooks 02 a 04 pueden ejecutarse sin repetir la descarga si conservas los originales de Bronce.

La instalación requiere Internet; los notebooks 02 a 04 usan las fuentes locales. Cambios en la estructura de los archivos publicados pueden exigir ajustes en los notebooks.
