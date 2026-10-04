# Framework de Métodos Numéricos

Este repositorio contiene un motor reutilizable para cálculo numérico. 
Todo ejercicio debe iniciarse ejecutando el motor de tanteo y luego seleccionando el método de aproximación.

## Estructura
```
metodos/                     Catálogo de técnicas de búsqueda de raíces
├── base.py                  Contrato común: descriptores Metodo y Contexto
├── __init__.py              Registro METODOS y dispatcher de ejecución
├── tanteo.py                Expansión bidireccional y graficación (Fase 1)
├── interpolacion_lineal.py  Regla Falsa
├── biseccion.py             Bisección
├── newton_raphson.py        Newton-Raphson + análisis de convergencia
└── iteracion.py             Iteración de punto fijo y su aceleración de Aitken

orquestador.py               Menú interactivo que une las fases
consola.py                   Fuerza UTF-8 en la salida (consolas Windows)
ejercicio1.py                Ejemplo: profundidad de un tanque esférico
ejercicio2.py                Ejemplo: punto de equilibrio de la compañía
ejercicio3.py                Ejemplo: equilibrio con publicidad variable
```

## Métodos disponibles

El menú se arma a partir del registro `METODOS` de `metodos/__init__.py`. Cada
método declara qué datos exige y cuáles son sus condiciones de aplicación, así
que el orquestador pide solo lo necesario y avisa antes de usar una técnica que
no puede converger.

| Método | Exige | Condiciones que verifica |
|---|---|---|
| Bisección | intervalo `[a, b]` | cambio de signo `f(a)·f(b) < 0` |
| Regla Falsa | intervalo `[a, b]` | cambio de signo y `f(a) != f(b)` (secante no horizontal) |
| Newton-Raphson | intervalo `[a, b]` + `x0` | las 4 condiciones suficientes + `f'(x0) != 0` + `x0 ∈ [a, b]` |
| Punto fijo | intervalo `[a, b]` + `x0` | contracción `\|g'(x)\| < 1` en el intervalo |
| Punto fijo + Aitken | intervalo `[a, b]` + `x0` | las del punto fijo y además `g' != 1` (si no, Aitken se indefiniría) |

La iteración usa la relajación `g(x) = x - λ·f(x)`, cuyo parámetro `λ` controla
la convergencia: es estable cuando `|1 - λ·f'(x)| < 1`, es decir cuando
`0 < λ < 2/max|f'(x)|`. Si el `λ` no cumple, el diagnóstico indica el rango
admisible.

Al elegir un intervalo, el menú marca cuáles métodos pueden aplicarse:

```
Métodos disponibles:
  1. Bisección                        ✅ condiciones satisfechas
  2. Interpolación Lineal (Regla Falsa) ✅ condiciones satisfechas
  3. Newton-Raphson                   ⚠️  requiere x0 (se analiza al elegir)
  0. Volver a elegir intervalo
```

### Agregar un método nuevo
1. Crear el módulo dentro de `metodos/` con su función `ejecutar_<nombre>` y una función `comprobar_<nombre>(contexto) -> (cumple, mensajes)`.
2. Declarar el descriptor `METODO = Metodo(clave, nombre, ayuda, requiere, ejecutar, comprobar)`.
3. Agregar el módulo a la tupla `METODOS` en `metodos/__init__.py`.

No hace falta tocar el orquestador.

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
Para resolver un nuevo ejercicio, duplica `ejercicio1.py`, define la función matemática `f(x)` y pásala a `iniciar_resolucion`:
```python
from orquestador import iniciar_resolucion

iniciar_resolucion(f, *args, titulo="Mi ejercicio")
```

El flujo interactivo pide:
1. Las constantes del problema (las que pida tu ejercicio).
2. En el tanteo: punto de origen, radio de expansión y tamaño del paso.
3. El intervalo con cambio de signo a resolver.
4. El método de aproximación, y los datos que ese método exija (`x0` en el caso de Newton-Raphson, que además propone un valor por defecto).
5. La tolerancia.

## Ejercicios
* `ejercicio1.py` — profundidad del agua en un tanque esférico. Raíz ≈ 0.6355 para R=1 m y V=1 m³.
* `ejercicio2.py` — punto de equilibrio de la compañía: `P(x) = 8x + 0.3x² − 0.0013x³ − 372`. Raíces ≈ 25.2335 y 250.7593 impresoras/mes.
* `ejercicio3.py` — `R(x) = 5x − 200·ln(400/(500−x))`, busca `R(x) = 1000`. Raíz ≈ 213.3245 unidades/semana, alcanzada con punto fijo y con Aitken.