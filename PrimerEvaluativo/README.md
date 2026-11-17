# Sistema Integral de Métodos Computacionales — Trabajo Evaluativo y Guías 1, 2 y 3

**Universidad Nacional del Nordeste (UNNE)**
**Facultad de Ciencias Exactas y Naturales y Agrimensura (FaCENA)**  
**Carrera:** Licenciatura en Sistemas de Información  
**Asignatura:** Métodos Computacionales — Año Lectivo 2026  
**Día y Horario de Clase:** Jueves, 15:00 hs.  

**Integrantes:**
* **Mac Lean Troche, Juan Manuel** — L.U. N°: 4747
* **Machuca, Augusto** — L.U. N°: 45893

**Repositorio de Control de Versiones (Git/GitHub):**  
[https://github.com/Jumadman/metodos-numericos](https://github.com/Jumadman/metodos-numericos)

---

## 1. Descripción General del Sistema

Este software implementa en **Python 3** una plataforma modular e interactiva que abarca las tres unidades temáticas del primer tramo de la asignatura:
* **Tema 1 (Guía N° 1):** Formulación de modelos matemáticos, complejidad algorítmica, procesos iterativos vs. recursivos y análisis de convergencia en series infinitas.
* **Tema 2 (Guía N° 2):** Aproximaciones numéricas, representación en punto flotante normalizado de k dígitos, redondeo vs. truncamiento, cancelación sustractiva y esquema anidado de Horner.
* **Tema 3 (Guía N° 3 y 1° Trabajo Evaluativo):** Localización, separación y aproximación de raíces de ecuaciones no lineales f(x) = 0 mediante el Método de Tanteo Optimizado, Intervalo Medio (Bisección), Interpolación Lineal (Regula Falsi), Newton-Raphson (con análisis de Fourier), Iteración Simple de Punto Fijo y Aceleración Delta^2 de Aitken bajo el esquema de reinicio activo de Steffensen.

---

## 2. Arquitectura y Estructura del Proyecto

El código fuente está organizado bajo el patrón arquitectónico de **Separación de Intereses (Separation of Concerns)**, aislando los modelos matemáticos, los motores numéricos de cálculo y el sistema de visualización gráfica:

PrimerEvaluativo/
├── main-evaluativo.py         # Orquestador general y menú iterativo principal
├── controlador_funciones.py   # Modelos del Canal de Manning y Función Libre de usuario
├── Tanteo.py                  # Motor de separación de raíces, filtro de polos y descartes
├── metodos_aproximacion.py    # Los 4 métodos dinámicos de aproximación de raíces
├── visualizador.py            # Graficador estático y Slideshow interactivo paso a paso
├── guia_1.py                  # Módulo de resolución de la Guía de Laboratorio N° 1
├── aritmetica_flotante.py     # Emulador de punto flotante normalizado a k dígitos (Guía 2)
├── guia_2.py                  # Módulo de resolución de la Guía de Laboratorio N° 2
├── guia_3.py                  # Módulo de resolución de la Guía de Laboratorio N° 3
├── requirements.txt           # Especificación de librerías científicas requeridas
└── README.md                  # Documentación técnica e instrucciones de uso

---

## 3. Detalle Técnico de los Módulos

### 3.1. Núcleo del Trabajo Evaluativo y Motores de Raíces
* **main-evaluativo.py**: Punto de entrada único del sistema. Presenta un menú iterativo sin bloqueo de consola que permite ejecutar el caso de estudio del Trabajo Evaluativo (Manning), ingresar cualquier función en el Modo Libre (aplicando los métodos asignados o la batería completa de 4 métodos) o acceder a los submenús de las Guías 1, 2 y 3.
* **controlador_funciones.py**:
  * ProblemaManning: Modela el flujo estacionario en un canal trapezoidal abierto mediante f(x) = [sqrt(S0)/n] * [(Bx + zx^2)^(5/3) / (B + 2x*sqrt(1 + z^2))^(2/3)] - Q = 0 y su despeje contractivo x = g(x). Preserva el signo real en potencias fraccionarias con math.copysign, valida entradas positivas con pedir_positivo() y filtra el dominio físico admisible 0 <= x <= H_max.
  * ProblemaPersonalizado: Analizador de expresiones matemáticas ingresadas por consola en un entorno seguro sin acceso a __builtins__. Si el usuario solo ingresa f(x), el método calibrar_g(x0) construye automáticamente la función de relajación g(x) = x - alfa*f(x) con alfa = 0.5 / f'(x0), garantizando analíticamente que |g'(x0)| ≈ 0.5 < 1.
* **Tanteo.py**: Explora un intervalo [x_inicio, x_fin] con incremento configurable Delta x. Supera las limitaciones del tanteo elemental mediante:
  1. Manejo seguro de regiones fuera del dominio real (NaN) en logaritmos o radicales pares.
  2. Detección heurística de asíntotas verticales (es_discontinuidad_o_asintota) evaluando la divergencia en el punto medio del subintervalo.
  3. Captura de raíces tangenciales de multiplicidad par mediante el cambio de signo de la derivada numérica central f'(x_k) * f'(x_k+1) <= 0.
* **metodos_aproximacion.py**: Implementa de forma desacoplada los cuatro algoritmos de la cátedra, retornando un diccionario estandarizado de métricas y una lista con el historial paso a paso:
  1. ejecutar_biseccion: Calcula e informa la cota de iteraciones teóricas n >= log2((b - a) / E) y subdivide por punto medio.
  2. ejecutar_interpolacion_lineal: Verifica la condición de encierro de Bolzano y traza cuerdas secantes sucesivas.
  3. analizar_condiciones_fourier y ejecutar_newton_raphson: Evalúa computacionalmente las 4 hipótesis de Fourier (Bolzano, monotonía f'(x) != 0, concavidad constante f''(x) != 0 y condición de extremo f(x0)*f''(x0) > 0) antes de iterar por rectas tangentes.
  4. analizar_convergencia_punto_fijo, ejecutar_iteracion_simple y ejecutar_steffensen: Verifica la condición suficiente de Lipschitz (|g'(x0)| < 1) y ejecuta tanto el esquema de punto fijo simple como la aceleración Delta^2 de Aitken por ciclos con reinicio activo (Steffensen), detallando las ternas utilizadas (x1, x2, x3) -> x4.
* **visualizador.py**:
  * graficar_inspeccion_inicial: Trazado general de f(x) junto con el eje y = 0 y las raíces destacadas (equivalente a fplot).
  * VisualizadorInteractivo y mostrar_visualizador: Presentación interactiva controlada por los botones '< Anterior' y 'Siguiente >'. Aplica recorte estadístico por percentiles intercuartílicos (P5 a P95) para evitar deformaciones por asíntotas, realiza Auto-Zoom dinámico hacia la raíz y despliega un panel doble con el Diagrama de Telaraña (Cobweb Plot de y = g(x) vs y = x) en los métodos de punto fijo.

### 3.2. Módulos de las Guías de Laboratorio N° 1, 2 y 3
* **guia_1.py**: Contiene la resolución interactiva de los Ejercicios 1 al 6 y Complementarios de la Guía N° 1 (sumatoria de N positivos, filtrado de pares, sucesión de Fibonacci iterativa O(N) vs recursiva O(2^N) para N = 200, ecuación cuadrática, serie factorial del número e y serie de Gregory-Leibniz para pi con medición de tiempos para 3, 4 y 5 decimales).
* **aritmetica_flotante.py y guia_2.py**: Emulan un procesador de precisión finita en base 10 con mantisa normalizada a k dígitos significativos (ROUND_HALF_UP para redondeo simétrico y ROUND_DOWN para truncamiento). Resuelven los Ejercicios 1 al 5 de la Guía N° 2 (errores absoluto y relativo, pérdida de asociatividad en punto flotante, cancelación catastrófica en ecuaciones cuadráticas con racionalización del numerador y evaluación polinómica directa vs forma anidada de Horner).
* **guia_3.py**: Modela y resuelve de forma guiada los problemas de la Guía N° 3 reutilizando los motores principales:
  * Ejercicio1TanqueEsferico: Profundidad de llenado en tanque esférico (R = 3 m, V = 30 m^3) comparando Bisección vs Interpolación Lineal.
  * Ejercicio2PuntoEquilibrio: Niveles de equilibrio en producción de impresoras (P(x) = 8x + 0.3x^2 - 0.0013x^3 - 372 = 0) mediante análisis de Fourier en  y Newton-Raphson.
  * Ejercicio3UtilidadPublicidad: Ecuación trascendente de gasto publicitario en entorno de x0 = 200 (E < 1e-4), contrastando Iteración Simple frente a Aceleración de Aitken/Steffensen.
  * laboratorio_dinamico_guia_3: Permite aplicar cualquiera de los 4 métodos a cualquiera de los 3 ejercicios en tiempo real.

---

## 4. Requisitos e Instalación

1. Asegúrese de contar con Python 3.8 o superior.
2. Instale las dependencias ejecutando en la terminal:

pip install -r requirements.txt

---

## 5. Instrucciones de Ejecución

Desde la consola o terminal situada en la carpeta del código fuente, ejecute:

python main-evaluativo.py

El sistema desplegará el menú interactivo principal:
* **Opción 1:** Ejecuta el 1° Trabajo Evaluativo (Canal Hidráulico de Manning). Presione Enter en cada parámetro si desea utilizar los valores de diseño por defecto (Q = 45.0, B = 1.5, z = 3.5, S0 = 0.0008, n = 0.028, H_max = 5.0, Delta x = 2.5, E = 0.001).
* **Opción 2:** Abre el Modo Libre, permitiendo ingresar cualquier función f(x) (por ejemplo: pi * x^2 * (9 - x)/3 - 30 o x^3 - x - 1) y evaluarla con los métodos del evaluativo o con los 4 métodos de la cátedra.
* **Opción 3:** Abre el submenú interactivo de la Guía de Laboratorio N° 1.
* **Opción 4:** Abre el submenú interactivo de la Guía de Laboratorio N° 2.
* **Opción 5:** Abre el submenú interactivo de la Guía de Laboratorio N° 3.

---

## 6. Estándares de Codificación Adoptados

Todo el código fuente cumple con la guía de estilo PEP 8 de Python:
* **Clases:** Notación PascalCase (ProblemaManning, ProblemaPersonalizado, VisualizadorInteractivo).
* **Funciones, métodos y variables:** Notación snake_case (metodo_tanteo_optimizado, ejecutar_steffensen, normalizar_k_digitos).
* **Parámetros físicos del modelo hidráulico:** Notación simbólica ingenieril (Q, B, z, S0, n, H_max) en correspondencia directa con las ecuaciones del informe técnico.