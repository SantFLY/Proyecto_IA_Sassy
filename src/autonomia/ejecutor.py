from typing import Dict, Any, Optional, Callable, List
import importlib
import sys
from pathlib import Path
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from queue import PriorityQueue

class EjecutorAcciones:
    def __init__(self):
        self.acciones_registradas: Dict[str, Callable] = {}
        self.acciones_en_ejecucion = set()
        self.cola_prioridades = PriorityQueue()
        self.timeout_default = 30  # segundos
        self.max_workers = 3
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._cargar_acciones()
        
    def _cargar_acciones(self):
        """Carga todas las acciones disponibles desde los módulos"""
        # Cargar acciones del sistema (eliminado para evitar error de importación)
        # self._cargar_modulo_acciones("src.commands.sistema")
        # Cargar acciones de plugins
        self._cargar_modulo_acciones("src.plugins")
        
    def _cargar_modulo_acciones(self, ruta_modulo: str):
        """Carga las acciones desde un módulo específico"""
        try:
            modulo = importlib.import_module(ruta_modulo)
            if hasattr(modulo, "registrar_acciones"):
                acciones = modulo.registrar_acciones()
                for nombre, accion in acciones.items():
                    self.registrar_nueva_accion(nombre, accion)
        except Exception as e:
            logging.error(f"Error al cargar módulo {ruta_modulo}: {e}")
            
    def ejecutar_accion(self, tipo_accion: str, parametros: Dict[str, Any], prioridad: int = 1) -> Dict[str, Any]:
        """
        Ejecuta una acción específica con los parámetros dados.
        Retorna un diccionario con el resultado de la ejecución.
        
        Args:
            tipo_accion: Nombre de la acción a ejecutar
            parametros: Parámetros para la acción
            prioridad: Prioridad de la acción (1-5, 1 es más alta)
        """
        if tipo_accion not in self.acciones_registradas:
            return {
                "exito": False,
                "error": f"Acción '{tipo_accion}' no encontrada",
                "resultado": None
            }
            
        # Verificar si la acción ya está en ejecución
        if tipo_accion in self.acciones_en_ejecucion:
            return {
                "exito": False,
                "error": f"La acción '{tipo_accion}' ya está en ejecución",
                "resultado": None
            }
            
        try:
            # Añadir a la cola de prioridades
            self.cola_prioridades.put((prioridad, (tipo_accion, parametros)))
            
            # Ejecutar la acción con timeout
            accion = self.acciones_registradas[tipo_accion]
            self.acciones_en_ejecucion.add(tipo_accion)
            
            future = self.executor.submit(self._ejecutar_con_timeout, accion, parametros)
            resultado = future.result(timeout=self.timeout_default)
            
            return {
                "exito": True,
                "error": None,
                "resultado": resultado,
                "tiempo_ejecucion": time.time() - future.start_time
            }
            
        except TimeoutError:
            return {
                "exito": False,
                "error": f"La acción '{tipo_accion}' excedió el tiempo máximo de ejecución",
                "resultado": None
            }
        except Exception as e:
            logging.error(f"Error al ejecutar acción {tipo_accion}: {e}")
            return {
                "exito": False,
                "error": str(e),
                "resultado": None
            }
        finally:
            self.acciones_en_ejecucion.discard(tipo_accion)
            
    def _ejecutar_con_timeout(self, accion: Callable, parametros: Dict[str, Any]) -> Any:
        """Ejecuta una acción con timeout"""
        start_time = time.time()
        try:
            return accion(**parametros)
        finally:
            tiempo_ejecucion = time.time() - start_time
            if tiempo_ejecucion > self.timeout_default:
                logging.warning(f"Acción tardó {tiempo_ejecucion:.2f}s en ejecutarse")
                
    def registrar_nueva_accion(self, nombre: str, funcion: Callable, prioridad_default: int = 3):
        """Registra una nueva acción en el sistema"""
        self.acciones_registradas[nombre] = funcion
        self._guardar_accion(nombre, funcion, prioridad_default)
        
    def _guardar_accion(self, nombre: str, funcion: Callable, prioridad_default: int):
        """Guarda la información de la acción en el archivo de acciones conocidas"""
        ruta_archivo = Path("data/acciones_conocidas.json")
        try:
            if ruta_archivo.exists():
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    acciones = json.load(f)
            else:
                acciones = {}
                
            acciones[nombre] = {
                "nombre": nombre,
                "descripcion": funcion.__doc__ or "",
                "parametros": list(funcion.__annotations__.keys()),
                "prioridad_default": prioridad_default,
                "ultima_ejecucion": None,
                "tiempo_promedio": None
            }
            
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(acciones, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error al guardar acción {nombre}: {e}")
            
    def obtener_estado_acciones(self) -> Dict[str, Any]:
        """Obtiene el estado actual de las acciones"""
        return {
            "acciones_registradas": list(self.acciones_registradas.keys()),
            "acciones_en_ejecucion": list(self.acciones_en_ejecucion),
            "cola_prioridades": self.cola_prioridades.qsize(),
            "workers_activos": len(self.executor._threads)
        }
        
    def cancelar_accion(self, tipo_accion: str) -> bool:
        """Intenta cancelar una acción en ejecución"""
        if tipo_accion in self.acciones_en_ejecucion:
            self.acciones_en_ejecucion.discard(tipo_accion)
            return True
        return False 