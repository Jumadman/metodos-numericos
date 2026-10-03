# Framework de Métodos Numéricos

Este repositorio contiene un motor reutilizable para cálculo numérico. 
Todo ejercicio debe iniciarse ejecutando el motor de tanteo y luego seleccionando el método de aproximación.

## Estructura
* `tanteo.py`: Lógica de expansión bidireccional y graficación.
* `interpolacion_lineal.py`: Algoritmo de aproximación por Regla Falsa.
* `orquestador.py`: Menú interactivo que une las fases.
* `ejercicio_tanque.py`: Ejemplo de implementación de un ejercicio de la guía.

## Requisitos
* Python 3.9 o superior.
* Las dependencias declaradas en `requirements.txt` (principalmente `matplotlib` para la graficación del tanteo).

## Instalación

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> Si PowerShell bloquea la activación con un error de *execution policy*, ejecuta:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`
> y vuelve a correr `.\.venv\Scripts\Activate.ps1`.

### Ejecutar sin activar el entorno
Si prefieres no activar el venv, llama al intérprete directamente:

* Linux / macOS: `./.venv/bin/python ejercicio1.py`
* Windows: `.\.venv\Scripts\python.exe ejercicio1.py`

## Uso
Para resolver un nuevo ejercicio, duplica `ejercicio_tanque.py`, cambia la función matemática `f(x)` y ejecútalo con:
`python nombre_del_ejercicio.py`

El flujo interactivo pide:
1. Las constantes del problema (radio del tanque y volumen deseado).
2. En el tanteo: punto de origen, radio de expansión y tamaño del paso.
3. El intervalo con cambio de signo a resolver y el método de aproximación.