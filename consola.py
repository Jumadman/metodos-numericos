"""Configuración de la consola para los módulos del framework.

Se importa por efecto secundario: basta con `import consola` en cualquier
módulo que imprima resultados.

Motivo: las consolas heredadas de Windows usan la codificación cp1252, que no
puede representar los indicadores usados en las tablas de resultados (✅ / ⚠️ /
❌) ni los subíndices matemáticos (x₀). Sin esta corrección, cualquier print
de esos caracteres lanza UnicodeEncodeError.
"""

import sys

def configurar_consola():
    """Fuerza UTF-8 en stdout y degrada a 'replace' ante caracteres no representables."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                # Flujo ya cerrado o sin soporte: no es motivo para abortar.
                pass

configurar_consola()