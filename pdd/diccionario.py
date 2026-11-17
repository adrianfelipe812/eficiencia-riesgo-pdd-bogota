"""Diccionario de datos de la capa Gold, escrito para quien conoce de indicadores
pero no de programación: qué significa cada columna, en qué unidad está y de dónde sale."""
import yaml

from pdd.comun import RAIZ

AP = "Avance del Plan (SDP)"
GI = "Gestión-Inversión (SDP)"
PDF = "PDF Gestión-Inversión por entidad"
CALC = "Calculado"
NLP = "Análisis de texto"
MILL = "millones de pesos corrientes"

M, A = "gold_meta_corte", "gold_actividad_corte"
F, B = "gold_narrativa_fragmento", "gold_barrera_fragmento"

DICCIONARIO = [
    # ---------------- gold_meta_corte ----------------
    (M, "fecha_corte", "Fecha del corte trimestral de seguimiento al que corresponde la fila.", "fecha", AP),
    (M, "vigencia", "Año al que pertenece el corte.", "año", CALC),
    (M, "objetivo_codigo", "Código del objetivo estratégico del Plan.", "código", AP),
    (M, "objetivo_nombre", "Nombre del objetivo estratégico.", "texto", AP),
    (M, "programa_codigo", "Código del programa.", "código", AP),
    (M, "programa_nombre", "Nombre del programa.", "texto", AP),
    (M, "meta_producto_codigo", "Código de la meta producto. Junto con fecha_corte identifica la fila.", "código", AP),
    (M, "meta_producto_nombre", "Enunciado de la meta producto.", "texto", AP),
    (M, "avance_vigencia", "Avance físico oficial de la meta frente a lo programado para el año del corte.", "% (puede superar 100)", AP),
    (M, "avance_transcurrido", "Avance físico oficial desde el inicio del Plan hasta el año del corte.", "%", AP),
    (M, "avance_plan", "Avance físico oficial frente a todo el cuatrienio.", "%", AP),
    (M, "n_actividades", "Número de actividades de proyectos de inversión asociadas a la meta en ese corte.", "conteo", GI),
    (M, "n_entidades", "Número de entidades que aportan actividades a la meta.", "conteo", GI),
    (M, "n_actividades_programadas", "Actividades con magnitud física programada mayor que cero para el año.", "conteo", CALC),
    (M, "n_actividades_entrega_cero", "Actividades con programación positiva y entrega física igual a cero al corte.", "conteo", CALC),
    (M, "recursos_programados", "Suma de los recursos programados para el año en las actividades de la meta.", MILL, GI),
    (M, "recursos_comprometidos", "Suma de los recursos comprometidos o contratados del año.", MILL, GI),
    (M, "recursos_girados", "Suma de los giros (pagos) del año.", MILL, GI),
    (M, "tipo_anualizacion_predominante", "Tipo de anualización más frecuente entre las actividades de la meta: Suma, Constante, Creciente o Decreciente.", "categoría", GI),
    (M, "sector_principal", "Sector que concentra más recursos programados de la meta.", "texto", CALC),
    (M, "entidad_principal", "Sigla de la entidad que concentra más recursos programados de la meta.", "texto", CALC),
    (M, "pct_compromisos", "Ejecución financiera: recursos comprometidos / recursos programados del año.", "%", CALC),
    (M, "pct_giros", "Recursos girados / recursos programados del año.", "%", CALC),
    (M, "pct_actividades_entrega_cero", "Actividades con entrega cero / actividades con programación positiva.", "%", CALC),
    (M, "tiene_datos_financieros", "Verdadero si el corte tiene archivo de Gestión-Inversión (septiembre de 2024 no lo tiene).", "sí/no", CALC),
    (M, "avance_esperado_lineal", "Referencia exploratoria: parte del año transcurrida (marzo 25, junio 50, septiembre 75, diciembre 100). No es una obligación oficial de la meta.", "%", CALC),
    (M, "brecha_fisico_financiera", "pct_compromisos menos avance_vigencia. Positivo: el dinero va más adelantado que la entrega física.", "puntos porcentuales", CALC),
    (M, "n_relatos_retraso", "Número de relatos 'Retrasos y soluciones' leídos para la meta en ese corte (uno por entidad e indicador).", "conteo", PDF),
    (M, "menciona_dificultad", "Verdadero si algún relato reconoce un retraso, demora, rezago o dificultad.", "sí/no", NLP),
    (M, "estado_narrativa", "Lectura resumida del relato de retrasos. Si varias entidades reportan, queda el estado más delicado.", "categoría", NLP),
    (M, "n_barreras_distintas", "Cuántas categorías de barrera distintas aparecen en los relatos de la meta.", "conteo", NLP),
    (M, "corte_con_narrativa", "Verdadero si para ese corte existe el PDF por entidad (hoy: sep-2024, dic-2024, mar-2026, jun-2026).", "sí/no", CALC),
    (M, "fecha_corte_siguiente", "Fecha del corte inmediatamente posterior de la misma meta.", "fecha", CALC),
    (M, "avance_vigencia_siguiente", "avance_vigencia observado en el corte siguiente. Sirve para comprobar si la alerta se cumplió. NO debe usarse como variable explicativa.", "%", CALC),
    (M, "grupo_dea", "Grupo de metas comparables usado para medir eficiencia: mismo tipo de anualización y mismo sector. Vacío si el grupo tiene menos de 8 metas o la meta no comprometió recursos.", "texto", CALC),
    (M, "eficiencia_dea", "Eficiencia técnica relativa (DEA). 1 = ninguna meta comparable logró más avance físico con igual o menos dinero. 0,6 = con ese dinero, las mejores del grupo lograron un avance equivalente a 1/0,6 veces el de esta meta. Vacío si el grupo es inestable.", "0 a 1", "DEA"),
    (M, "brecha_eficiencia", "1 menos eficiencia_dea: qué tan lejos está la meta de las mejores de su grupo.", "0 a 1", "DEA"),
    (M, "en_frontera", "Verdadero si la meta es una de las de mejor desempeño de su grupo (eficiencia 1).", "sí/no", "DEA"),
    (M, "holgura_insumo_pct", "Parte de los recursos comprometidos que, comparada con la frontera, no habría sido necesaria para el avance logrado.", "%", "DEA"),
    (M, "grupo_estable", "Verdadero si el orden de las metas del grupo se mantiene al medir con giros en vez de compromisos. Los grupos inestables no se usan para concluir.", "sí/no", "DEA"),
    (M, "en_rezago_actual", "1 si en este corte la meta está en el 20 % más bajo de avance físico entre las metas de su mismo tipo de anualización.", "1/0", CALC),
    (M, "riesgo_relativo_siguiente", "Variable objetivo PRINCIPAL: 1 si en el corte siguiente la meta queda en el 20 % más bajo de avance entre las metas de su tipo de anualización. NO usar como variable explicativa.", "1/0", CALC),
    (M, "riesgo_lineal_siguiente", "Variable objetivo alterna: 1 si en el corte siguiente el avance del año queda por debajo del 70 % de lo esperado con avance parejo (marzo 25, junio 50...). NO usar como variable explicativa.", "1/0", CALC),
    (M, "riesgo_cierre_anio", "Variable objetivo alterna: 1 si la meta cierra el año (corte de diciembre) con avance inferior a 90 %. Solo para cortes de marzo, junio y septiembre de años ya cerrados. NO usar como variable explicativa.", "1/0", CALC),
    # ---------------- gold_actividad_corte ----------------
    (A, "fecha_corte", "Fecha del corte de seguimiento.", "fecha", GI),
    (A, "vigencia", "Año que la fila está reportando.", "año", GI),
    (A, "sector_codigo", "Código del sector administrativo.", "código", GI),
    (A, "sector_nombre", "Nombre del sector.", "texto", GI),
    (A, "entidad_codigo", "Código de la entidad responsable.", "código", GI),
    (A, "entidad_sigla", "Sigla de la entidad.", "texto", GI),
    (A, "entidad_nombre", "Nombre de la entidad.", "texto", GI),
    (A, "objetivo_codigo", "Código del objetivo estratégico.", "código", GI),
    (A, "programa_codigo", "Código del programa.", "código", GI),
    (A, "meta_producto_codigo", "Meta producto a la que aporta la actividad.", "código", GI),
    (A, "proyecto_codigo", "Código del proyecto de inversión.", "código", GI),
    (A, "proyecto_nombre", "Nombre del proyecto de inversión.", "texto", GI),
    (A, "proyecto_actividad_codigo", "Código de la actividad dentro del proyecto. Entidad + proyecto + actividad identifican la actividad.", "código", GI),
    (A, "proyecto_actividad_nombre", "Enunciado de la actividad.", "texto", GI),
    (A, "tipo_anualizacion", "Cómo se acumula la actividad: Suma (se suman los años), Constante (se repite cada año), Creciente o Decreciente (niveles).", "categoría", GI),
    (A, "fila_rezagada", "Verdadero si el archivo del corte trae el seguimiento de un año anterior. Estas filas no se suman en gold_meta_corte.", "sí/no", CALC),
    (A, "fisico_programado", "Magnitud física programada para el año.", "unidad propia de la actividad", GI),
    (A, "fisico_entregado", "Magnitud física entregada al corte.", "unidad propia de la actividad", GI),
    (A, "pct_fisico_entregado", "Porcentaje de entrega física del año, tal como lo publica la fuente.", "%", GI),
    (A, "recursos_programados", "Recursos programados para el año.", MILL, GI),
    (A, "recursos_comprometidos", "Recursos comprometidos o contratados del año.", MILL, GI),
    (A, "recursos_girados", "Giros (pagos) del año.", MILL, GI),
    (A, "pct_compromisos", "Recursos comprometidos / programados del año.", "%", CALC),
    (A, "pct_giros", "Recursos girados / programados del año.", "%", CALC),
    (A, "fisico_total_programado", "Magnitud física programada para todo el cuatrienio.", "unidad propia de la actividad", GI),
    (A, "fisico_total_entregado", "Magnitud física entregada acumulada, según la fuente.", "unidad propia de la actividad", GI),
    (A, "pct_fisico_total_entregado", "Porcentaje de entrega frente al cuatrienio, según la fuente.", "%", GI),
    (A, "recursos_total_programados_constantes", "Recursos programados del cuatrienio a precios constantes (comparables entre años).", "millones de pesos constantes", GI),
    (A, "recursos_total_girados_constantes", "Giros acumulados a precios constantes.", "millones de pesos constantes", GI),
    (A, "entrega_cero_con_programacion", "Verdadero si la actividad tenía programación positiva para el año y su entrega al corte es cero.", "sí/no", CALC),
    # ---------------- gold_narrativa_fragmento ----------------
    (F, "fragmento_id", "Identificador estable del relato: corte-entidad-meta-indicador-campo (R = retrasos, A = avances).", "código", CALC),
    (F, "fecha_corte", "Corte del reporte, leído de la portada del PDF.", "fecha", PDF),
    (F, "entidad_codigo", "Entidad que escribió el relato.", "código", PDF),
    (F, "entidad_nombre", "Nombre de la entidad, como aparece en el PDF.", "texto", PDF),
    (F, "meta_producto_codigo", "Meta producto a la que se refiere el relato.", "código", PDF),
    (F, "indicador_codigo", "Indicador bajo el cual aparece el relato.", "código", PDF),
    (F, "indicador_nombre", "Nombre del indicador.", "texto", PDF),
    (F, "campo", "Cuál de los dos relatos es: retrasos_y_soluciones o avances_y_logros.", "categoría", PDF),
    (F, "archivo_fuente", "Nombre del PDF del que se leyó.", "texto", CALC),
    (F, "texto", "Relato completo, tal como lo escribió la entidad.", "texto", PDF),
    (F, "pagina_inicio", "Página del PDF donde empieza el relato.", "número de página", CALC),
    (F, "pagina_fin", "Página del PDF donde termina.", "número de página", CALC),
    (F, "estado_retraso", "Solo para retrasos_y_soluciones: Sin retraso declarado, Avance programado para más adelante, Texto sin clasificar, Retraso sin causa clasificada o Barrera identificada.", "categoría", NLP),
    (F, "declara_sin_retraso", "Verdadero si alguna frase afirma que no hubo retrasos.", "sí/no", NLP),
    (F, "menciona_dificultad", "Verdadero si alguna frase (que no sea de solución) reconoce retraso, demora, rezago o dificultad.", "sí/no", NLP),
    (F, "n_barreras", "Número de categorías de barrera encontradas en el relato.", "conteo", NLP),
    # ---------------- gold_barrera_fragmento ----------------
    (B, "fragmento_id", "Relato en el que se encontró la barrera (enlaza con gold_narrativa_fragmento).", "código", CALC),
    (B, "fecha_corte", "Corte del reporte.", "fecha", PDF),
    (B, "entidad_codigo", "Entidad que escribió el relato.", "código", PDF),
    (B, "meta_producto_codigo", "Meta producto del relato.", "código", PDF),
    (B, "indicador_codigo", "Indicador del relato.", "código", PDF),
    (B, "categoria", "Clave de la categoría (ver gold_catalogo_barreras).", "categoría", NLP),
    (B, "categoria_nombre", "Nombre legible de la categoría.", "texto", NLP),
    (B, "es_barrera", "Falso solo para 'Avance programado para más adelante', que explica el avance pero no es un obstáculo.", "sí/no", NLP),
    (B, "frase_evidencia", "Primera frase del relato que activó la categoría. Permite comprobar la clasificación leyendo.", "texto", PDF),
]

with open(RAIZ / "configs" / "barreras.yaml", encoding="utf-8") as _f:
    for _clave, _cat in yaml.safe_load(_f)["categorias"].items():
        if _cat.get("es_barrera", True):
            DICCIONARIO.append((M, f"barrera_{_clave}",
                                f"1 si algún relato de la meta menciona la barrera '{_cat['nombre']}': {_cat['descripcion']}",
                                "1/0", NLP))
