"""Pruebas automáticas de las reglas centrales. Ejecutar con:  python -m pytest -q"""
import numpy as np
import pandas as pd

from pdd.barreras import ESTADOS, cargar_diccionario, clasificar_texto
from pdd.dea import eficiencia_bcc
from pdd.modelo import agregar_objetivos

DIC = cargar_diccionario()


def estado(texto):
    return clasificar_texto(texto, DIC)


def test_sin_retraso():
    assert estado("No se presentaron retrasos.")["estado"] == ESTADOS["sin_retraso"]
    assert estado("N/A")["estado"] == ESTADOS["sin_retraso"]


def test_barrera_exige_frase_de_problema():
    r = estado("Se presentaron retrasos en la adjudicación del proceso licitatorio.")
    assert r["estado"] == ESTADOS["barrera"] and "contratacion" in r["evidencia"]
    # La misma palabra clave, sin señal de problema, no cuenta.
    assert "contratacion" not in estado("Se avanzó en la contratación de acuerdo con el plan.")["evidencia"]


def test_la_solucion_no_es_barrera():
    r = estado("No se presentaron retrasos. Soluciones: se suspendió el contrato pendiente con el contratista.")
    assert r["estado"] == ESTADOS["sin_retraso"]
    assert estado("Para mitigar el retraso se fortalecerá la articulación interinstitucional.")["evidencia"] == {}


def test_salvedad_despues_de_no_hubo_retrasos():
    r = estado("No se presentaron retrasos; sin embargo, la licencia de construcción sigue pendiente.")
    assert "tramites_y_permisos" in r["evidencia"]


def test_retraso_sin_causa_y_programado():
    assert estado("Se presenta retraso en las acciones de monitoreo.")["estado"] == ESTADOS["retraso"]
    assert estado("El indicador está programado para el último trimestre.")["estado"] == ESTADOS["programado"]


def test_dea_caso_conocido():
    # Tres metas con el mismo dinero: la de mayor avance es eficiente y las otras se miden contra ella.
    ef, _ = eficiencia_bcc(np.array([10.0, 10.0, 10.0]), np.array([100.0, 50.0, 25.0]))
    assert np.allclose(ef, [1.0, 0.5, 0.25])
    # Una meta sin avance tiene eficiencia cero; una que domina a todas, uno.
    ef, _ = eficiencia_bcc(np.array([5.0, 10.0]), np.array([80.0, 0.0]))
    assert np.allclose(ef, [1.0, 0.0])


def test_riesgo_no_usa_el_futuro_y_respeta_empates():
    cortes = pd.to_datetime(["2025-09-30", "2025-12-31"])
    meta = pd.DataFrame({
        "meta_producto_codigo": np.repeat(list("ABCDEFGH"), 2), "fecha_corte": np.tile(cortes, 8),
        "tipo_anualizacion_predominante": "Suma",
        "avance_vigencia": [10, 60, 70, 100, 70, 100, 70, 100, 70, 100, 70, 100, 70, 100, 70, 100]})
    meta["vigencia"] = meta["fecha_corte"].dt.year
    cfg = {"riesgo": {"grupo_relativo": ["tipo_anualizacion_predominante"], "cuantil_relativo": 0.25, "fraccion_minima_del_esperado": 0.7, "umbral_cierre": 90}}
    t = agregar_objetivos(meta, cfg).set_index(["meta_producto_codigo", "fecha_corte"])
    # En diciembre casi todas llegan a 100: solo la que quedó por debajo está rezagada.
    assert t.loc[("A", cortes[0]), "riesgo_relativo_siguiente"] == 1
    assert t.loc[("B", cortes[0]), "riesgo_relativo_siguiente"] == 0
    # El último corte no conoce el futuro.
    assert t.xs(cortes[1], level="fecha_corte")["riesgo_relativo_siguiente"].isna().all()
    assert t.loc[("A", cortes[0]), "riesgo_cierre_anio"] == 1 and t.loc[("B", cortes[0]), "riesgo_cierre_anio"] == 0


def test_umbral_por_costos():
    from pdd.modelo import costo_total, umbral_bayes, umbral_minimo_costo
    # Con un rezago omitido 5 veces más costoso que una falsa alarma, se alerta desde p = 1/6.
    assert abs(umbral_bayes(5, 1) - 1 / 6) < 1e-12 and umbral_bayes(1, 1) == 0.5
    y, p = np.array([0, 0, 1, 1]), np.array([0.1, 0.4, 0.35, 0.9])
    assert costo_total(y, p >= 0.5, 5, 1) == 5        # omite la meta de 0,35
    assert costo_total(y, p >= 0.3, 5, 1) == 1        # una falsa alarma (0,4)
    # El umbral de mínimo costo detecta los dos rezagos con una sola falsa alarma.
    assert costo_total(y, p >= umbral_minimo_costo(y, p, 5, 1), 5, 1) == 1


def test_explicacion_legible():
    import pandas as pd
    from pdd.modelo import _explicar
    valores = pd.Series({"avance_vigencia": 0.0, "en_rezago_actual": 1.0, "trimestre": 3.0})
    texto = _explicar(valores, np.array([1.2, 0.8, -0.1]))
    assert texto.startswith("Avance del año: 0,0 % (sube el riesgo)")
    assert "Ya rezagada en este corte: sí" in texto and "septiembre (baja el riesgo)" in texto
