"""Comprueba que el proyecto se puede reproducir de principio a fin en este equipo.

Uso, desde la raíz del repositorio:
    python scripts/reproducir.py

Hace cinco cosas y al final dice si todo coincide:
  1. Verifica que los datos de entrada son exactamente los registrados en data/FUENTES.csv.
  2. Ejecuta las pruebas automáticas.
  3. Vuelve a construir todas las tablas en una carpeta temporal y las compara, columna
     por columna, con las publicadas en data/gold/.
  4. Repite la auditoría contra los archivos originales de la SDP.
  5. Vuelve a generar el tablero y comprueba que es igual al publicado en tablero/index.html.

No modifica data/gold/. Para regenerar las tablas publicadas use scripts/construir_gold.py.
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from pdd.comun import cargar_config  # noqa: E402
from pdd.gold import construir_gold  # noqa: E402

TEMPORAL = RAIZ / "data" / "_verificacion"
TOLERANCIA = 1e-6      # diferencia numérica admitida entre equipos (redondeos del procesador)


def verificar_entradas() -> bool:
    fuentes = pd.read_csv(RAIZ / "data" / "FUENTES.csv", sep=";", encoding="utf-8-sig")
    bien = True
    for fila in fuentes.itertuples():
        ruta = RAIZ / fila.archivo
        igual = ruta.exists() and hashlib.sha256(ruta.read_bytes()).hexdigest() == fila.sha256
        bien &= igual
        if not igual:
            print(f"   DIFERENTE o ausente: {fila.archivo}")
    print(f"   {len(fuentes)} archivos de entrada: {'todos coinciden' if bien else 'HAY DIFERENCIAS'}")
    return bien


def leer(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, sep="|", decimal=",", encoding="utf-8-sig", low_memory=False)


def comparar_tablas() -> bool:
    bien = True
    publicadas = sorted((RAIZ / "data" / "gold").glob("gold_*.csv"))
    for ruta in publicadas:
        nueva = TEMPORAL / ruta.name
        if not nueva.exists():
            print(f"   FALTA    {ruta.name}")
            bien = False
            continue
        a, b = leer(ruta), leer(nueva)
        if a.shape != b.shape or list(a.columns) != list(b.columns):
            estado = f"DIFERENTE (forma {a.shape} frente a {b.shape})"
        else:
            distintas = []
            for col in a.columns:
                if pd.api.types.is_numeric_dtype(a[col]) and pd.api.types.is_numeric_dtype(b[col]):
                    iguales = np.allclose(a[col].astype(float), b[col].astype(float), rtol=TOLERANCIA,
                                          atol=TOLERANCIA, equal_nan=True)
                else:
                    iguales = a[col].astype(str).equals(b[col].astype(str))
                if not iguales:
                    distintas.append(col)
            estado = "igual" if not distintas else f"DIFERENTE en {distintas[:4]}"
        bien &= estado == "igual"
        print(f"   {estado:<10} {ruta.name}  ({len(a)} filas)")
    sobrantes = {p.name for p in TEMPORAL.glob("gold_*.csv")} - {p.name for p in publicadas}
    if sobrantes:
        print(f"   Tablas nuevas que no están publicadas: {sorted(sobrantes)}")
        bien = False
    return bien


def ejecutar(comando: list[str]) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, *comando], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    return r.returncode == 0, r.stdout + r.stderr


if __name__ == "__main__":
    resultados = {}
    print("1/5 Datos de entrada")
    resultados["Datos de entrada sin cambios"] = verificar_entradas()

    print("2/5 Pruebas automáticas")
    ok, salida = ejecutar(["-m", "pytest", "-q"])
    print("   " + salida.strip().splitlines()[-1])
    resultados["Pruebas automáticas"] = ok

    print("3/5 Reconstrucción de las tablas (tarda unos minutos)")
    config = cargar_config()
    config["rutas"]["gold"] = str(TEMPORAL)
    tablas = construir_gold(config, silencioso=True)
    control = tablas["gold_control_calidad"]
    resultados["Controles de calidad"] = bool((control["cumple"] == "Sí").all())
    print(f"   Controles de calidad: {(control['cumple'] == 'Sí').sum()} de {len(control)}")
    resultados["Tablas iguales a las publicadas"] = comparar_tablas()
    shutil.rmtree(TEMPORAL, ignore_errors=True)

    print("4/5 Auditoría contra los archivos originales")
    ok, salida = ejecutar(["scripts/auditar_gold.py"])
    fallas = [l for l in salida.splitlines() if l.startswith("FALLA")]
    aciertos = sum(l.startswith("OK") for l in salida.splitlines())
    print(f"   {aciertos} comprobaciones correctas, {len(fallas)} con falla")
    for l in fallas:
        print("   " + l)
    resultados["Auditoría contra originales"] = ok and not fallas

    print("5/5 Tablero")
    temporal = RAIZ / "tablero" / "_verificacion.html"
    ok, salida = ejecutar(["scripts/generar_tablero.py", str(temporal)])
    limpio = lambda ruta: ruta.read_bytes().replace(b"\r\n", b"\n")
    igual = ok and limpio(temporal) == limpio(RAIZ / "tablero" / "index.html")
    temporal.unlink(missing_ok=True)
    print(f"   El tablero publicado {'corresponde' if igual else 'NO corresponde'} a las tablas")
    resultados["Tablero igual al publicado"] = igual

    print("\nRESUMEN")
    for nombre, bien in resultados.items():
        print(f"   {'SÍ' if bien else 'NO'}  {nombre}")
    todo = all(resultados.values())
    print("\nREPRODUCIDO: todo coincide." if todo else "\nNO REPRODUCIDO: revise los puntos marcados con NO.")
    sys.exit(0 if todo else 1)
