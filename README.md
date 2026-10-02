# Framework de Métodos Numéricos

Este repositorio contiene un motor reutilizable para cálculo numérico. 
Todo ejercicio debe iniciarse ejecutando el motor de tanteo y luego seleccionando el método de aproximación.

## Estructura
* `tanteo.py`: Lógica de expansión bidireccional y graficación.
* `interpolacion_lineal.py`: Algoritmo de aproximación por Regla Falsa.
* `orquestador.py`: Menú interactivo que une las fases.
* `ejercicio_tanque.py`: Ejemplo de implementación de un ejercicio de la guía.

## Uso
Para resolver un nuevo ejercicio, duplica `ejercicio_tanque.py`, cambia la función matemática `f(x)` y ejecútalo con:
`python nombre_del_ejercicio.py`