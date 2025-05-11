"""
Módulo de utilidades del sistema.
Contiene funciones para obtener información del sistema.
"""

import psutil
import datetime

def obtener_hora():
    """Obtener la hora actual"""
    return datetime.datetime.now().strftime("%H:%M:%S")

def obtener_fecha():
    """Obtener la fecha actual"""
    return datetime.datetime.now().strftime("%d/%m/%Y")

def obtener_info_sistema():
    """Obtener información del sistema"""
    cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory().percent
    disco = psutil.disk_usage('/').percent
    return {
        "cpu": cpu,
        "memoria": memoria,
        "disco": disco
    }

def formatear_info_sistema(info):
    """Formatear la información del sistema para mostrarla"""
    return f"CPU: {info['cpu']}%, Memoria: {info['memoria']}%, Disco: {info['disco']}%" 