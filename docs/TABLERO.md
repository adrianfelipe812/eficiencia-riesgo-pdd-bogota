# Tablero Foco PDD

Guía del tablero `tablero/index.html`: qué muestra cada vista, qué reglas usa y cómo se reconstruye. El tablero es un solo archivo que se abre con doble clic, lleva los datos adentro y funciona sin conexión.

## 1. Cómo se usa

### Encabezado (todas las vistas)

Arriba queda fijo un recuadro con el título de la vista y, a la derecha:

- **Modo oscuro**: el botón con la luna lo activa y el del sol lo desactiva. El navegador recuerda la elección.
- **Fecha de corte**: cambia el corte de todo el tablero.
- **Filtros**: abre un panel con Sector, Entidad y Meta. El número sobre el botón indica cuántos filtros hay activos. Al hacer clic en una gráfica se pueden sumar otros filtros (señal, relato, barrera); «Limpiar filtros» los quita todos.

### Inicio (Panorama)

- **Seis tarjetas**: Metas en el alcance, Porcentaje programado, Porcentaje de recursos girados, Porcentaje comprometido, Rezagadas en el corte y Alerta alta. Los tres porcentajes son promedios simples por meta (suma de los porcentajes ÷ número de metas con dato):
  - Porcentaje programado: `avance_vigencia`, el avance físico frente a lo programado del año.
  - Porcentaje de recursos girados: `pct_giros`, girado ÷ programado del año.
  - Porcentaje comprometido: `pct_compromisos`, comprometido ÷ programado del año.
- **Gráficas**: metas por tramo de avance, avance frente a dinero comprometido y evolución del alcance por corte. Las leyendas van abajo y centradas; cada gráfica ocupa toda su celda; en la evolución, la franja gris marca el año del corte elegido.

### Metas (bandeja de focalización)

- **Tabla**: Meta producto, Avance de vigencia, Comprometido, Girado, Relato y Alerta. Al bajar quedan fijos el encabezado de la tarjeta y los títulos de columna.
- **Detalle de la meta** (al hacer clic en una fila): la cabecera de la meta queda fija; debajo van seis tarjetas con semáforo, los relatos de las entidades y, al final, la evolución de la meta frente a las de su tipo (avance de vigencia y dinero comprometido, en dos gráficas).

**Semáforo de las tarjetas.** Cada valor se compara con lo esperado al corte si el avance fuera parejo en el tiempo (el Plan se cuenta desde enero de 2024, cuatro años):

| Tarjeta | Esperado al corte |
|---|---|
| Avance de vigencia, % Comprometido, % Girado | Parte del año transcurrida: marzo 25 %, junio 50 %, septiembre 75 %, diciembre 100 % |
| Transcurrido | Meses desde enero de 2024 ÷ meses hasta el cierre del año del corte |
| Cuatrienio | Meses desde enero de 2024 ÷ 48 |

Verde: 90 % o más de lo esperado. Ámbar: entre 60 % y 90 %. Rojo: menos de 60 %. Gris: sin dato. «Sin entrega» es verde si ninguna actividad programada quedó sin entrega, ámbar si menos de la mitad y rojo si la mitad o más. «0 de 1» significa que, de una actividad programada, ninguna quedó sin entrega.

### Actividades

Tabla de actividades del alcance, con encabezado fijo. **Al pasar el cursor** sobre una actividad (o al tocarla en el celular) aparece su avance de vigencia año por año del Plan, como la tabla «Año / Programación / Ejecución vigencia / Avance de la vigencia» de los reportes de la SDP: barras de programado (gris) y ejecutado (semáforo), el % de cada año y el total «Al plan de desarrollo». Los años cerrados se comparan con 100 %, el año del corte con lo esperado al corte, y los años siguientes aparecen «por ejecutar».

### Descargas (barra lateral)

«Descargar archivos fuente» tiene su propio selector de corte (sincronizado con el del encabezado) y un botón por cada archivo original disponible en ese corte: informe por entidad (PDF), Avance del Plan (Excel) y Gestión e inversión (Excel). Si el corte no tiene un archivo, su botón no aparece. Los botones descargan la copia de `data/raw/`, así que funcionan al abrir el tablero dentro de la carpeta del repositorio; cuando se conoce, también hay un enlace oficial de la SDP.

### Celular (Android e iOS)

El menú pasa a una barra fija abajo; las tablas se ven como tarjetas con etiquetas; la gráfica de cada actividad se abre al tocar la fila (panel inferior con botón de cerrar) y las descargas quedan al final de la página. En el celular no hay encabezados fijos ni orden por columna.

## 2. Reglas propias del tablero

- **Metas sin compromiso, sin alerta.** En el último corte, una meta con 0 % comprometido (o sin dato) y sin compromisos en vigencias futuras no lleva alerta ni puntaje de riesgo; aparece como «Sin alerta · sin compromiso». Está pendiente decidir qué hacer con las metas que sí tenían recursos programados (ver README, «Pendiente por validar»).
- **Entidades normalizadas.** Las entidades se muestran con su nombre oficial y sigla (`entidad_nombre_sigla`, de `data/raw/Normalizacion_Entidades.xlsx`).

## 3. Cómo se construye

```text
tablero/plantilla_foco_base.html   diseño original (aplicación compilada, sin datos)
        │  scripts/construir_plantilla.py  aplica scripts/ajustar_*.py en orden
        ▼
tablero/plantilla_foco.html        diseño con los ajustes del equipo
        │  scripts/generar_tablero.py      inyecta los datos Gold (gzip + base64)
        ▼
tablero/index.html                 tablero final
```

| Ajuste | Qué hace |
|---|---|
| `ajustar_encabezado.py` | Título y filtros en un recuadro fijo; fecha de corte junto a «Filtros»; filtros de sector, entidad y meta |
| `ajustar_tarjetas.py` | Tarjetas del Panorama centradas, con ícono junto al número |
| `ajustar_graficas.py` | Leyendas abajo, gráficas que llenan su celda, franja del año del corte |
| `ajustar_bandeja.py` | Tabla de metas: títulos completos y fijos, columna «Girado», anchos compactos |
| `ajustar_detalle.py` | Detalle de la meta: seis tarjetas con semáforo, cabecera fija, relatos antes que gráficas |
| `ajustar_actividades.py` | Gráfica de avance por año al pasar el cursor; encabezado fijo |
| `ajustar_descargas.py` | Descargas de archivos fuente por corte |
| `ajustar_tema.py` | Modo oscuro |
| `ajustar_movil.py` | Uso cómodo en celular |

Cada ajuste reemplaza fragmentos exactos del código compilado y se detiene con un mensaje si no encuentra lo que busca. Para cambiar el diseño se edita (o se agrega) un ajuste y se ejecutan:

```bash
python scripts/construir_plantilla.py
```

```bash
python scripts/generar_tablero.py
```

Los datos del tablero salen solo de Gold: `gold_meta_corte`, `gold_actividad_corte` (incluye el avance año por año y los compromisos en vigencias futuras), `gold_narrativa_fragmento`, `gold_barrera_fragmento`, `gold_prediccion_riesgo`, `gold_catalogo_barreras` y `gold_auditoria_nlp_resumen`. La lista de archivos descargables sale de `data/FUENTES.csv`.
