"""Catálogo de métodos de búsqueda de raíces.

Para agregar un método al framework basta con crear un módulo en este paquete
que declare un descriptor METODO (ver `base.Metodo`) e importarlo en la lista
METODOS de este archivo. El orquestador arma el menú y valida las condiciones
a partir de ese registro, sin modificar una sola línea.
"""

import consola  # Configura stdout a UTF-8 al importarse (afecta a todo el paquete)

from .base import Contexto, Metodo, REQUIERE_INTERVALO, REQUIERE_X0
from . import biseccion, interpolacion_lineal, iteracion, newton_raphson
from .tanteo import ejecutar_tanteo, derivada_numerica

# Orden del menú. Para incorporar una técnica nueva (Secante, Broyden, ...) basta
# con añadir su módulo aquí.
METODOS = (
    biseccion.METODO,
    interpolacion_lineal.METODO,
    newton_raphson.METODO,
    iteracion.METODO,
    iteracion.METODO_AITKEN,
)

def obtener(clave):
    """Devuelve el descriptor del método indicado por clave, o None si no existe."""
    for metodo in METODOS:
        if metodo.clave == clave:
            return metodo
    return None

def listar():
    """Devuelve el catálogo de métodos como (indice, Metodo) para mostrar en el menú."""
    return list(enumerate(METODOS, start=1))

def ejecutar(metodo, contexto, tol, max_iter=100):
    """
    Invoca el método pasando solo los datos que declara en `requiere`.

    Así cada técnica recibe exactamente los argumentos que sabe interpretar, sin
    que el orquestador necesite conocer su firma concreta. Un método que exige
    x0 recibe ese valor; los métodos de bracketsación reciben el par (a, b).
    """
    if metodo.pide_x0:
        return metodo.ejecutar(
            contexto.func, contexto.args_func, contexto.x0, tol, max_iter=max_iter
        )
    return metodo.ejecutar(
        contexto.func, contexto.args_func, contexto.a, contexto.b, tol, max_iter=max_iter
    )