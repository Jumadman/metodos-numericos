"""Contrato común que deben cumplir los métodos de búsqueda de raíces.

Cada método se registra declarando qué datos exige (`requiere`) y cómo se
verifican sus condiciones de aplicación (`comprobar`). El orquestador usa esa
información para pedir solo lo necesario y para avisar antes de ejecutar una
técnica que no puede converger.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

# Datos que un método puede exigir al usuario
REQUIERE_INTERVALO = "intervalo"  # necesita un par (a, b) con cambio de signo
REQUIERE_X0 = "x0"                # necesita un valor inicial

@dataclass(frozen=True)
class Contexto:
    """Problema a resolver y datos ya elegidos por el usuario."""
    func: Callable
    args_func: Tuple
    a: Optional[float] = None
    b: Optional[float] = None
    x0: Optional[float] = None
    # Parámetros propios del método (por ejemplo {"lam": 0.2} para la iteración).
    # Existen para que `comprobar` pueda verificar exactamente las mismas
    # condiciones que `ejecutar` va a usar.
    extra: dict = field(default_factory=dict)

@dataclass(frozen=True)
class Metodo:
    """
    Descriptor de un método de búsqueda de raíces.

    clave:      identificador interno del método
    nombre:     etiqueta para el menú
    ayuda:      texto mostrado en el listado de métodos
    requiere:   datos que el método exige (REQUIERE_INTERVALO / REQUIERE_X0)
    ejecutar:   callable (func, args_func, ..., tol, max_iter=...)
    comprobar:  callable (Contexto) -> (cumple: bool, mensajes: list[str])
                Verifica las condiciones del método antes de ejecutarlo.
    """
    clave: str
    nombre: str
    ayuda: str
    requiere: Tuple[str, ...]
    ejecutar: Callable
    comprobar: Callable
    sugerir_x0: Optional[Callable] = None

    @property
    def pide_intervalo(self) -> bool:
        return REQUIERE_INTERVALO in self.requiere

    @property
    def pide_x0(self) -> bool:
        return REQUIERE_X0 in self.requiere

    def proponer_x0(self, contexto: Contexto) -> Tuple[Optional[float], str]:
        """
        Valor inicial que el método recomienda y el motivo de la recomendación.

        Si el método no propone ninguno, se devuelve None y el orquestador
        ofrece el punto medio del intervalo.
        """
        if self.sugerir_x0 is None:
            return None, "punto medio del intervalo"
        return self.sugerir_x0(contexto)

    def condiciones_previas(self, contexto: Contexto) -> Tuple[bool, list]:
        """
        Verifica las condiciones que pueden comprobarse sin pedir datos al usuario.

        Los métodos que necesitan x0 no pueden evaluarse aquí: se validan más
        tarde, cuando el usuario ya eligió el valor inicial.
        """
        if self.pide_x0:
            return True, []
        return self.comprobar(contexto)