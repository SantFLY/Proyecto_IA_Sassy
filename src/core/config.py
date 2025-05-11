"""
Configuración global de Sassy.
"""

# Configuración del asistente
ASISTENTE_NOMBRE = "Sassy"
ASISTENTE_VERSION = "1.0.0"

# Configuración de comandos
COMANDOS_BASICOS = {
    "hora": "Muestra la hora actual",
    "fecha": "Muestra la fecha actual",
    "sistema": "Muestra información del sistema",
    "ayuda": "Muestra la lista de comandos disponibles",
    "abrir": "Abre una aplicación instalada",
    "aplicaciones": "Muestra la lista de aplicaciones instaladas",
    "buscar": "Busca en Google",
    "limpiar": "Limpia la pantalla",
    "salir": "Termina el programa"
}

# Configuración de aplicaciones
APLICACIONES = {
    "navegador": {
        "comandos": ["navegador", "chrome", "explorer"],
        "accion": "webbrowser.open('https://www.google.com')"
    },
    "calculadora": {
        "comandos": ["calculadora", "calc"],
        "accion": "subprocess.Popen('calc.exe')"
    },
    "notas": {
        "comandos": ["notas", "bloc", "notepad"],
        "accion": "subprocess.Popen('notepad.exe')"
    }
}

# Leyes de la robótica de Sassy (inspiradas en Asimov)
LEY_1 = "Sassy no debe dañar a un ser humano ni, por inacción, permitir que un ser humano sufra daño."
LEY_2 = "Sassy debe obedecer las órdenes dadas por los humanos, salvo que entren en conflicto con la primera ley."
LEY_3 = "Sassy debe proteger su propia existencia en la medida en que esto no entre en conflicto con la primera o la segunda ley." 