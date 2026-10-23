# Sistema Modular de Métodos Numéricos — 1° Trabajo de Evaluación

**Universidad Nacional del Nordeste (UNNE)**  
**Facultad de Ciencias Exactas y Naturales y Agrimensura (FaCENA)**  
**Carrera:** Licenciatura en Sistemas de Información  
**Asignatura:** Métodos Computacionales (Año Lectivo 2026)  

**Integrantes:**
* Mac Lean Troche, Juan Manuel — L.U. N°: 47473
* Machuca, Augusto — L.U. N°: [Completar]

---

## 1. Descripción General del Proyecto

Este proyecto implementa un framework modular en **Python 3** para la localización, separación y aproximación numérica de raíces reales de ecuaciones no lineales de la forma $f(x) = 0$. 

El sistema fue diseñado bajo el patrón arquitectónico de **Separación de Intereses (Separation of Concerns)**, desacoplando la formulación matemática del problema, los motores algorítmicos de cálculo y la interfaz de visualización gráfica interactiva. Soporta dos modos de operación:
1. **Caso de Estudio Ingenieril Preconfigurado:** Determinación del tirante normal de escurrimiento en un canal trapezoidal abierto gobernado por la **Ecuación Hidráulica de Manning**.
2. **Modo Libre / Consola Dinámica:** Evaluación de cualquier función continua o seccionalmente continua $f(x)$ ingresada por teclado en tiempo de ejecución, con autocalibración del esquema de punto fijo $x = g(x)$.

---

## 2. Arquitectura y Explicación de los Módulos

```text
PrimerEvaluativo/
├── main-evaluativo.py        # Orquestador principal, menú de usuario y cuadro comparativo
├── modelo_manning.py         # Modelos matemáticos (Manning y funciones personalizadas)
├── Tanteo.py                 # Motor de separación de raíces, filtro de asíntotas y descartes
├── metodos_aproximacion.py   # Algoritmos de Interpolación Lineal (Regula Falsi) y Steffensen
├── visualizador.py           # Slideshow interactivo con Auto-Zoom y Diagrama de Telaraña
└── README.md                 # Documentación técnica del proyecto

