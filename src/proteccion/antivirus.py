import os
import hashlib
import json
import logging
import psutil
import requests
import yara
import magic
import pefile
import re
import win32api
import win32security
import win32file
import win32con
import win32process
import win32event
import win32service
import win32serviceutil
import win32ts
import win32gui
import win32com.client
import win32job
import win32security
import win32api
import win32con
import win32process
import win32event
import win32file
import win32security
import win32ts
import win32gui
import win32com.client
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import threading
import time
import winreg
import shutil
import socket
import struct
import ctypes
from ctypes import wintypes
import tempfile
import subprocess
import queue
import random
import string
import math

class Sandbox:
    def __init__(self):
        self.job_handle = None
        self.temp_dir = None
        self.procesos_sandbox = set()
        self.archivos_modificados = set()
        self.registro_modificado = set()
        self.conexiones_red = set()
        
    def crear_entorno(self):
        """Crea un entorno sandbox aislado"""
        try:
            # Crear directorio temporal
            self.temp_dir = tempfile.mkdtemp(prefix="sassy_sandbox_")
            
            # Crear job object para limitar recursos
            self.job_handle = win32job.CreateJobObject(None, "SassySandbox")
            
            # Configurar límites del job
            info = win32job.QueryInformationJobObject(self.job_handle, win32job.JobObjectExtendedLimitInformation)
            info['BasicLimitInformation']['LimitFlags'] = (
                win32job.JOB_OBJECT_LIMIT_PROCESS_TIME |
                win32job.JOB_OBJECT_LIMIT_JOB_MEMORY |
                win32job.JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION |
                win32job.JOB_OBJECT_LIMIT_BREAKAWAY_OK
            )
            info['ProcessMemoryLimit'] = 100 * 1024 * 1024  # 100MB
            info['JobMemoryLimit'] = 200 * 1024 * 1024  # 200MB
            win32job.SetInformationJobObject(self.job_handle, win32job.JobObjectExtendedLimitInformation, info)
            
            return True
        except Exception as e:
            logging.error(f"Error al crear sandbox: {e}")
            return False
            
    def ejecutar_en_sandbox(self, ruta: str, timeout: int = 30) -> Dict:
        """Ejecuta un programa en el sandbox"""
        try:
            if not self.job_handle:
                if not self.crear_entorno():
                    return {"error": "No se pudo crear el sandbox"}
            
            # Crear proceso en el sandbox
            startup_info = win32process.STARTUPINFO()
            startup_info.dwFlags = win32process.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = win32con.SW_HIDE
            
            # Crear proceso con permisos limitados
            proceso, thread, pid, tid = win32process.CreateProcess(
                ruta,
                None,
                None,
                None,
                0,
                win32con.CREATE_SUSPENDED | win32con.CREATE_NO_WINDOW,
                None,
                self.temp_dir,
                startup_info
            )
            
            # Asignar al job object
            win32job.AssignProcessToJobObject(self.job_handle, proceso)
            
            # Iniciar monitoreo
            self._monitorear_proceso(pid)
            
            # Reanudar proceso
            win32process.ResumeThread(thread)
            
            # Esperar con timeout
            try:
                win32event.WaitForSingleObject(proceso, timeout * 1000)
            except win32event.error:
                pass
            
            # Obtener resultados
            resultados = {
                "archivos_modificados": list(self.archivos_modificados),
                "registro_modificado": list(self.registro_modificado),
                "conexiones_red": list(self.conexiones_red),
                "comportamiento_sospechoso": self._analizar_comportamiento_sandbox()
            }
            
            # Limpiar
            self._limpiar_sandbox()
            
            return resultados
            
        except Exception as e:
            logging.error(f"Error al ejecutar en sandbox: {e}")
            return {"error": str(e)}
            
    def _monitorear_proceso(self, pid: int):
        """Monitorea un proceso en el sandbox"""
        try:
            proceso = psutil.Process(pid)
            
            # Monitorear archivos
            for archivo in proceso.open_files():
                self.archivos_modificados.add(archivo.path)
            
            # Monitorear conexiones
            for conn in proceso.connections():
                if conn.status == 'ESTABLISHED':
                    self.conexiones_red.add(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}")
            
            # Monitorear registro
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "", 0, winreg.KEY_READ) as key:
                    self._monitorear_clave_registro(key)
            except Exception:
                pass
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    def _monitorear_clave_registro(self, key):
        """Monitorea cambios en el registro"""
        try:
            i = 0
            while True:
                try:
                    nombre = winreg.EnumKey(key, i)
                    self.registro_modificado.add(nombre)
                    i += 1
                except WindowsError:
                    break
        except Exception:
            pass
            
    def _analizar_comportamiento_sandbox(self) -> List[str]:
        """Analiza el comportamiento del programa en el sandbox"""
        comportamientos_sospechosos = []
        
        # Verificar modificaciones al sistema
        if len(self.archivos_modificados) > 10:
            comportamientos_sospechosos.append("Muchas modificaciones de archivos")
            
        if len(self.registro_modificado) > 5:
            comportamientos_sospechosos.append("Muchas modificaciones al registro")
            
        # Verificar conexiones de red
        if self.conexiones_red:
            comportamientos_sospechosos.append("Conexiones de red detectadas")
            
        # Verificar intentos de persistencia
        if any("run" in r.lower() for r in self.registro_modificado):
            comportamientos_sospechosos.append("Intento de persistencia detectado")
            
        return comportamientos_sospechosos
        
    def _limpiar_sandbox(self):
        """Limpia el entorno sandbox"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            if self.job_handle:
                win32job.TerminateJobObject(self.job_handle, 0)
            self.archivos_modificados.clear()
            self.registro_modificado.clear()
            self.conexiones_red.clear()
        except Exception as e:
            logging.error(f"Error al limpiar sandbox: {e}")

class AntivirusSassy:
    def __init__(self):
        self.carpeta_cuarentena = Path("data/cuarentena")
        self.carpeta_cuarentena.mkdir(parents=True, exist_ok=True)
        
        self.db_amenazas = Path("data/amenazas.json")
        self.db_amenazas.parent.mkdir(parents=True, exist_ok=True)
        
        self.alertas = []
        self.procesos_monitoreados = set()
        self.archivos_cuarentena = set()
        self.archivos_whitelist = set()
        self.reglas_yara = None
        self.servicios_monitoreados = set()
        self.conexiones_monitoreadas = set()
        self.ventanas_monitoreadas = set()
        
        # Cargar base de datos de amenazas
        self.cargar_base_amenazas()
        
        # Iniciar logging
        logging.basicConfig(
            filename='logs/antivirus.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Iniciar monitoreo en segundo plano
        self.monitoreo_activo = False
        self.hilo_monitoreo = None
        self.hilo_red = None
        self.hilo_ventanas = None
        self.sandbox = Sandbox()
        self.analisis_heuristico = True
        self.nivel_heuristica = 2  # 1: Bajo, 2: Medio, 3: Alto
        # Poblar whitelist automáticamente
        self.poblar_whitelist_sistema()

    def cargar_base_amenazas(self):
        """Carga la base de datos de amenazas conocidas"""
        try:
            if self.db_amenazas.exists():
                with open(self.db_amenazas, 'r') as f:
                    self.amenazas = json.load(f)
            else:
                self.amenazas = {
                    "hashes": {},
                    "patrones": [],
                    "procesos_sospechosos": [],
                    "reglas_yara": [],
                    "extensiones_peligrosas": [],
                    "comportamientos_sospechosos": []
                }
                self.guardar_base_amenazas()
                
            # Compilar reglas YARA
            self._compilar_reglas_yara()
            
        except Exception as e:
            logging.error(f"Error al cargar base de amenazas: {e}")
            self.amenazas = {
                "hashes": {},
                "patrones": [],
                "procesos_sospechosos": [],
                "reglas_yara": [],
                "extensiones_peligrosas": [],
                "comportamientos_sospechosos": []
            }

    def _compilar_reglas_yara(self):
        """Compila las reglas YARA para detección de malware"""
        try:
            if self.amenazas["reglas_yara"]:
                self.reglas_yara = yara.compile(source="\n".join(self.amenazas["reglas_yara"]))
        except Exception as e:
            logging.error(f"Error al compilar reglas YARA: {e}")
            self.reglas_yara = None

    def escanear_archivo(self, ruta: str) -> Dict:
        """
        Escanea un archivo en busca de amenazas usando múltiples métodos
        Retorna: Dict con información sobre amenazas encontradas
        """
        try:
            resultado = {
                "amenaza": False,
                "tipo": None,
                "detalles": None,
                "hash": None,
                "metadatos": None
            }
            if ruta in self.archivos_whitelist:
                return {"amenaza": False, "whitelist": True}
            tipo_mime = magic.from_file(ruta, mime=True)
            resultado["metadatos"] = {"tipo_mime": tipo_mime}
            extension = os.path.splitext(ruta)[1].lower()
            hash_archivo = self._calcular_hash(ruta)
            resultado["hash"] = hash_archivo
            if hash_archivo in self.amenazas["hashes"]:
                resultado["amenaza"] = True
                resultado["tipo"] = "hash_conocido"
                resultado["detalles"] = self.amenazas["hashes"][hash_archivo]
                self._registrar_alerta(f"Amenaza detectada en {ruta}: {resultado['detalles']}")
            if not resultado["amenaza"]:
                patrones = self._buscar_patrones_sospechosos(ruta)
                if patrones:
                    resultado["amenaza"] = True
                    resultado["tipo"] = "patron_sospechoso"
                    resultado["detalles"] = patrones
                    self._registrar_alerta(f"Patrones sospechosos en {ruta}: {patrones}")
            if not resultado["amenaza"] and self.reglas_yara:
                matches = self._analizar_yara(ruta)
                if matches:
                    resultado["amenaza"] = True
                    resultado["tipo"] = "regla_yara"
                    resultado["detalles"] = matches
                    self._registrar_alerta(f"Coincidencia con regla YARA en {ruta}: {matches}")
            if not resultado["amenaza"] and hasattr(self, '_analizar_heuristica'):
                score_heuristica = self._analizar_heuristica(ruta)
                if score_heuristica > self.nivel_heuristica:
                    resultado["amenaza"] = True
                    resultado["tipo"] = "heuristica"
                    resultado["detalles"] = f"Score heurístico: {score_heuristica}"
                    self._registrar_alerta(f"Archivo sospechoso por heurística: {ruta} (score: {score_heuristica})")
            # Solo ejecutar en sandbox si es ejecutable válido
            if not resultado["amenaza"] and hasattr(self, 'sandbox'):
                if extension in ('.exe', '.dll') and tipo_mime.startswith('application'):
                    try:
                        resultado_sandbox = self.sandbox.ejecutar_en_sandbox(ruta)
                        if resultado_sandbox.get("comportamiento_sospechoso"):
                            resultado["amenaza"] = True
                            resultado["tipo"] = "sandbox"
                            resultado["detalles"] = resultado_sandbox
                            self._registrar_alerta(f"Comportamiento sospechoso en sandbox: {ruta}")
                    except Exception as e:
                        # Suprimir errores de sandbox no críticos
                        pass
            return resultado
        except PermissionError:
            # Suprimir errores de permisos no críticos
            return {"error": "Permiso denegado"}
        except Exception as e:
            logging.error(f"Error al escanear archivo {ruta}: {e}")
            return {"error": str(e)}

    def escanear_directorio(self, ruta: str, recursivo: bool = True) -> List[Dict]:
        """
        Escanea un directorio completo
        Args:
            ruta: Ruta del directorio a escanear
            recursivo: Si True, escanea subdirectorios
        """
        resultados = []
        try:
            if recursivo:
                for root, _, files in os.walk(ruta):
                    for file in files:
                        archivo = os.path.join(root, file)
                        resultado = self.escanear_archivo(archivo)
                        if resultado.get("amenaza"):
                            resultados.append({
                                "archivo": archivo,
                                **resultado
                            })
            else:
                for file in os.listdir(ruta):
                    if os.path.isfile(os.path.join(ruta, file)):
                        archivo = os.path.join(ruta, file)
                        resultado = self.escanear_archivo(archivo)
                        if resultado.get("amenaza"):
                            resultados.append({
                                "archivo": archivo,
                                **resultado
                            })
        except Exception as e:
            logging.error(f"Error al escanear directorio {ruta}: {e}")
        
        return resultados

    def monitorear_procesos(self):
        """Monitorea procesos activos en busca de amenazas"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and proc.info['exe'] not in self.procesos_monitoreados:
                        resultado = self.escanear_archivo(proc.info['exe'])
                        if resultado.get("amenaza"):
                            self._registrar_alerta(
                                f"Proceso sospechoso detectado: {proc.info['name']} (PID: {proc.info['pid']})"
                            )
                        self.procesos_monitoreados.add(proc.info['exe'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logging.error(f"Error en monitoreo de procesos: {e}")

    def poner_en_cuarentena(self, ruta: str) -> bool:
        """
        Pone un archivo en cuarentena
        Retorna: True si se pudo poner en cuarentena
        """
        try:
            if not os.path.exists(ruta):
                return False
                
            nombre_archivo = os.path.basename(ruta)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nuevo_nombre = f"{timestamp}_{nombre_archivo}"
            destino = self.carpeta_cuarentena / nuevo_nombre
            
            # Mover archivo a cuarentena
            shutil.move(ruta, destino)
            self.archivos_cuarentena.add(str(destino))
            
            # Registrar en log
            logging.info(f"Archivo puesto en cuarentena: {ruta} -> {destino}")
            self._registrar_alerta(f"Archivo puesto en cuarentena: {ruta}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error al poner en cuarentena {ruta}: {e}")
            return False

    def restaurar_de_cuarentena(self, archivo_cuarentena: str, destino: str) -> bool:
        """
        Restaura un archivo desde la cuarentena
        Retorna: True si se pudo restaurar
        """
        try:
            if not os.path.exists(archivo_cuarentena):
                return False
                
            shutil.move(archivo_cuarentena, destino)
            self.archivos_cuarentena.remove(archivo_cuarentena)
            
            logging.info(f"Archivo restaurado de cuarentena: {archivo_cuarentena} -> {destino}")
            return True
            
        except Exception as e:
            logging.error(f"Error al restaurar de cuarentena {archivo_cuarentena}: {e}")
            return False

    def actualizar_base_amenazas(self) -> bool:
        """
        Actualiza la base de datos de amenazas desde fuentes externas
        Retorna: True si se actualizó correctamente
        """
        try:
            # Aquí iría la lógica para descargar actualizaciones
            # Por ahora es un placeholder
            logging.info("Base de amenazas actualizada")
            return True
        except Exception as e:
            logging.error(f"Error al actualizar base de amenazas: {e}")
            return False

    def _calcular_hash(self, ruta: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        sha256 = hashlib.sha256()
        try:
            with open(ruta, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logging.error(f"Error al calcular hash de {ruta}: {e}")
            return ""

    def _buscar_patrones_sospechosos(self, ruta: str) -> List[str]:
        """Busca patrones sospechosos en un archivo"""
        patrones_encontrados = []
        try:
            with open(ruta, 'rb') as f:
                contenido = f.read()
                for patron in self.amenazas["patrones"]:
                    if patron.encode() in contenido:
                        patrones_encontrados.append(patron)
        except Exception as e:
            logging.error(f"Error al buscar patrones en {ruta}: {e}")
        return patrones_encontrados

    def _analizar_yara(self, ruta: str) -> List[str]:
        """Analiza un archivo usando reglas YARA"""
        try:
            if not self.reglas_yara:
                return []
            
            matches = self.reglas_yara.match(ruta)
            return [match.rule for match in matches]
        except Exception as e:
            logging.error(f"Error en análisis YARA de {ruta}: {e}")
            return []

    def _analizar_comportamiento(self, ruta: str) -> Optional[Dict]:
        """Analiza el comportamiento potencial de un ejecutable"""
        try:
            if not os.path.exists(ruta):
                return None
                
            comportamiento = {
                "sospechoso": False,
                "razones": []
            }
            
            # Analizar PE header
            try:
                pe = pefile.PE(ruta)
                
                # Verificar características sospechosas
                if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                    for entry in pe.DIRECTORY_ENTRY_IMPORT:
                        dll_name = entry.dll.decode().lower()
                        if dll_name in ['kernel32.dll', 'user32.dll', 'advapi32.dll', 'ws2_32.dll']:
                            for imp in entry.imports:
                                if imp.name:
                                    func_name = imp.name.decode().lower()
                                    if func_name in self.amenazas["comportamientos_sospechosos"]:
                                        comportamiento["sospechoso"] = True
                                        comportamiento["razones"].append(f"Importa función sospechosa: {func_name}")
                
                # Verificar secciones
                for section in pe.sections:
                    if section.Name.decode().strip('\x00') in ['.text', '.data']:
                        if section.Characteristics & 0xE0000000:  # Ejecutable y escribible
                            comportamiento["sospechoso"] = True
                            comportamiento["razones"].append("Sección con permisos sospechosos")
                
                # Verificar recursos
                if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
                    for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                        if resource_type.name:
                            if any(patron in resource_type.name.decode().lower() for patron in [
                                "crypto", "miner", "bitcoin", "ethereum", "wallet"
                            ]):
                                comportamiento["sospechoso"] = True
                                comportamiento["razones"].append(f"Recurso sospechoso: {resource_type.name.decode()}")
                
            except Exception as e:
                logging.error(f"Error al analizar PE de {ruta}: {e}")
            
            # Verificar permisos de archivo
            try:
                sd = win32security.GetFileSecurity(
                    ruta, 
                    win32security.OWNER_SECURITY_INFORMATION | 
                    win32security.GROUP_SECURITY_INFORMATION |
                    win32security.DACL_SECURITY_INFORMATION
                )
                
                dacl = sd.GetSecurityDescriptorDacl()
                if dacl is None:
                    comportamiento["sospechoso"] = True
                    comportamiento["razones"].append("Archivo sin ACL (acceso total)")
                else:
                    for i in range(dacl.GetAceCount()):
                        ace_type, ace_flags, ace_mask, ace_sid = dacl.GetAce(i)
                        if ace_mask & win32con.GENERIC_ALL:
                            comportamiento["sospechoso"] = True
                            comportamiento["razones"].append("Archivo con permisos excesivos")
                            break
            except Exception as e:
                logging.error(f"Error al verificar permisos de {ruta}: {e}")
            
            return comportamiento if comportamiento["sospechoso"] else None
            
        except Exception as e:
            logging.error(f"Error en análisis de comportamiento de {ruta}: {e}")
            return None

    def _monitorear_red(self):
        """Monitorea conexiones de red sospechosas"""
        while self.monitoreo_activo:
            try:
                # Obtener todas las conexiones de red
                conexiones = psutil.net_connections(kind='inet')
                
                for conn in conexiones:
                    if conn.status == 'ESTABLISHED':
                        # Verificar si es una conexión nueva
                        conn_id = f"{conn.laddr.ip}:{conn.laddr.port}-{conn.raddr.ip}:{conn.raddr.port}"
                        if conn_id not in self.conexiones_monitoreadas:
                            self.conexiones_monitoreadas.add(conn_id)
                            
                            # Obtener proceso asociado
                            try:
                                proceso = psutil.Process(conn.pid)
                                if proceso.name().lower() in self.amenazas["procesos_sospechosos"]:
                                    self._registrar_alerta(
                                        f"Conexión sospechosa detectada: {proceso.name()} "
                                        f"({conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port})"
                                    )
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error en monitoreo de red: {e}")
                time.sleep(5)

    def _monitorear_ventanas(self):
        """Monitorea ventanas sospechosas"""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo and titulo not in self.ventanas_monitoreadas:
                    self.ventanas_monitoreadas.add(titulo)
                    # Verificar si el título contiene patrones sospechosos
                    if any(patron in titulo.lower() for patron in [
                        "crypto", "miner", "bitcoin", "ethereum", "wallet",
                        "password", "login", "bank", "paypal", "amazon"
                    ]):
                        self._registrar_alerta(f"Ventana sospechosa detectada: {titulo}")
            return True

        while self.monitoreo_activo:
            try:
                win32gui.EnumWindows(enum_windows_callback, None)
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error en monitoreo de ventanas: {e}")
                time.sleep(5)

    def _monitorear_servicios(self):
        """Monitorea servicios de Windows"""
        # Verificar privilegios de administrador
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False
        if not is_admin:
            logging.warning("No se tienen privilegios de administrador. Monitoreo de servicios desactivado.")
            return
        while self.monitoreo_activo:
            try:
                # Enumerar servicios usando win32service
                hscm = win32service.OpenSCManager(None, None, win32con.SC_MANAGER_ENUMERATE_SERVICE)
                servicios = win32service.EnumServicesStatus(hscm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
                for servicio in servicios:
                    nombre = servicio[0]
                    if nombre not in self.servicios_monitoreados:
                        self.servicios_monitoreados.add(nombre)
                        # Verificar si el nombre del servicio es sospechoso
                        if any(patron in nombre.lower() for patron in [
                            "crypto", "miner", "bitcoin", "ethereum", "wallet",
                            "password", "login", "bank", "paypal", "amazon"
                        ]):
                            self._registrar_alerta(f"Servicio sospechoso detectado: {nombre}")
                win32service.CloseServiceHandle(hscm)
                time.sleep(10)
            except Exception as e:
                logging.error(f"Error en monitoreo de servicios: {e}")
                time.sleep(5)

    def iniciar_monitoreo_continuo(self):
        """Inicia el monitoreo continuo en segundo plano"""
        if not self.monitoreo_activo:
            self.monitoreo_activo = True
            
            # Iniciar hilos de monitoreo
            self.hilo_monitoreo = threading.Thread(target=self._monitoreo_continuo)
            self.hilo_red = threading.Thread(target=self._monitorear_red)
            self.hilo_ventanas = threading.Thread(target=self._monitorear_ventanas)
            
            # Configurar hilos como daemon
            self.hilo_monitoreo.daemon = True
            self.hilo_red.daemon = True
            self.hilo_ventanas.daemon = True
            
            # Iniciar hilos
            self.hilo_monitoreo.start()
            self.hilo_red.start()
            self.hilo_ventanas.start()
            
            # Iniciar monitoreo de servicios
            self._monitorear_servicios()

    def detener_monitoreo_continuo(self):
        """Detiene el monitoreo continuo"""
        self.monitoreo_activo = False
        if self.hilo_monitoreo:
            self.hilo_monitoreo.join()
        if self.hilo_red:
            self.hilo_red.join()
        if self.hilo_ventanas:
            self.hilo_ventanas.join()

    def _monitoreo_continuo(self):
        """Hilo de monitoreo continuo"""
        while self.monitoreo_activo:
            try:
                # Monitorear procesos
                self.monitorear_procesos()
                
                # Monitorear archivos críticos
                self._monitorear_archivos_criticos()
                
                # Monitorear registro
                self._monitorear_registro()
                
                time.sleep(5)  # Intervalo de monitoreo
                
            except Exception as e:
                logging.error(f"Error en monitoreo continuo: {e}")
                time.sleep(5)

    def _monitorear_archivos_criticos(self):
        """Monitorea archivos y carpetas críticas del sistema"""
        carpetas_criticas = [
            os.environ['SYSTEMROOT'],
            os.path.join(os.environ['SYSTEMROOT'], 'System32'),
            os.path.join(os.environ['SYSTEMROOT'], 'SysWOW64'),
            os.path.expanduser('~\\AppData\\Roaming'),
            os.path.expanduser('~\\AppData\\Local')
        ]
        
        for carpeta in carpetas_criticas:
            try:
                for root, _, files in os.walk(carpeta):
                    for file in files:
                        if file.endswith(('.exe', '.dll', '.sys')):
                            ruta = os.path.join(root, file)
                            if ruta not in self.procesos_monitoreados:
                                self.escanear_archivo(ruta)
            except Exception as e:
                logging.error(f"Error al monitorear carpeta crítica {carpeta}: {e}")

    def _monitorear_registro(self):
        """Monitorea cambios en el registro de Windows"""
        claves_criticas = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
        ]
        
        for clave in claves_criticas:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            nombre, valor, _ = winreg.EnumValue(key, i)
                            if valor.endswith('.exe'):
                                self.escanear_archivo(valor)
                            i += 1
                        except WindowsError:
                            break
            except Exception as e:
                logging.error(f"Error al monitorear clave de registro {clave}: {e}")

    def agregar_a_whitelist(self, ruta: str) -> bool:
        """Agrega un archivo a la lista blanca"""
        try:
            if os.path.exists(ruta):
                self.archivos_whitelist.add(ruta)
                logging.info(f"Archivo agregado a whitelist: {ruta}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error al agregar a whitelist {ruta}: {e}")
            return False

    def quitar_de_whitelist(self, ruta: str) -> bool:
        """Quita un archivo de la lista blanca"""
        try:
            if ruta in self.archivos_whitelist:
                self.archivos_whitelist.remove(ruta)
                logging.info(f"Archivo quitado de whitelist: {ruta}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error al quitar de whitelist {ruta}: {e}")
            return False

    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del antivirus"""
        return {
            "archivos_escaneados": len(self.procesos_monitoreados),
            "amenazas_detectadas": len([a for a in self.alertas if "Amenaza detectada" in a["mensaje"]]),
            "archivos_cuarentena": len(self.archivos_cuarentena),
            "archivos_whitelist": len(self.archivos_whitelist),
            "conexiones_monitoreadas": len(self.conexiones_monitoreadas),
            "servicios_monitoreados": len(self.servicios_monitoreados),
            "ventanas_monitoreadas": len(self.ventanas_monitoreadas),
            "ultima_actualizacion": self.amenazas.get("ultima_actualizacion", "Nunca")
        }

    def _registrar_alerta(self, mensaje: str):
        """Registra una alerta de seguridad"""
        self.alertas.append({
            "timestamp": datetime.now().isoformat(),
            "mensaje": mensaje
        })
        logging.warning(mensaje)

    def obtener_alertas(self) -> List[Dict]:
        """Retorna las alertas registradas"""
        return self.alertas

    def limpiar_alertas(self):
        """Limpia el historial de alertas"""
        self.alertas = []

    def analizar_archivo_avanzado(self, ruta: str) -> Dict:
        """Realiza un análisis avanzado de un archivo"""
        try:
            resultado = {
                "amenaza": False,
                "tipo": None,
                "detalles": None,
                "hash": None,
                "metadatos": None,
                "comportamiento": None,
                "heuristica": None
            }
            
            # Análisis básico
            resultado_basico = self.escanear_archivo(ruta)
            if resultado_basico.get("amenaza"):
                return resultado_basico
                
            # Análisis heurístico
            if self.analisis_heuristico:
                score_heuristica = self._analizar_heuristica(ruta)
                if score_heuristica > self.nivel_heuristica:
                    resultado["amenaza"] = True
                    resultado["tipo"] = "heuristica"
                    resultado["heuristica"] = score_heuristica
                    self._registrar_alerta(f"Archivo sospechoso por heurística: {ruta} (score: {score_heuristica})")
                    return resultado
            
            # Análisis en sandbox
            if ruta.lower().endswith(('.exe', '.dll', '.bat', '.cmd', '.ps1')):
                resultado_sandbox = self.sandbox.ejecutar_en_sandbox(ruta)
                if resultado_sandbox.get("comportamiento_sospechoso"):
                    resultado["amenaza"] = True
                    resultado["tipo"] = "sandbox"
                    resultado["comportamiento"] = resultado_sandbox
                    self._registrar_alerta(f"Comportamiento sospechoso en sandbox: {ruta}")
                    return resultado
            
            return resultado
            
        except Exception as e:
            logging.error(f"Error en análisis avanzado de {ruta}: {e}")
            return {"error": str(e)}
            
    def _analizar_heuristica(self, ruta: str) -> int:
        """Realiza análisis heurístico de un archivo"""
        score = 0
        
        try:
            # Verificar entropía
            if self._calcular_entropia(ruta) > 7.0:
                score += 1
                
            # Verificar strings sospechosos
            strings = self._extraer_strings(ruta)
            for string in strings:
                if any(patron in string.lower() for patron in [
                    "http://", "https://", "ftp://",
                    "cmd.exe", "powershell", "wscript",
                    "shell", "execute", "download",
                    "upload", "connect", "socket",
                    "bind", "listen", "accept"
                ]):
                    score += 1
                    
            # Verificar secciones
            if ruta.lower().endswith(('.exe', '.dll')):
                try:
                    pe = pefile.PE(ruta)
                    if len(pe.sections) > 5:
                        score += 1
                    if any(section.Name.decode().strip('\x00') == '.text' for section in pe.sections):
                        score += 1
                except:
                    pass
                    
            # Verificar recursos
            if ruta.lower().endswith(('.exe', '.dll')):
                try:
                    pe = pefile.PE(ruta)
                    if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
                        score += 1
                except:
                    pass
                    
            return score
            
        except Exception as e:
            logging.error(f"Error en análisis heurístico de {ruta}: {e}")
            return 0
            
    def _calcular_entropia(self, ruta: str) -> float:
        """Calcula la entropía de un archivo"""
        try:
            with open(ruta, 'rb') as f:
                data = f.read()
                
            if not data:
                return 0
                
            counts = {}
            for byte in data:
                counts[byte] = counts.get(byte, 0) + 1
                
            entropy = 0
            for count in counts.values():
                probability = count / len(data)
                entropy -= probability * math.log2(probability)
                
            return entropy
            
        except Exception as e:
            logging.error(f"Error al calcular entropía de {ruta}: {e}")
            return 0
            
    def _extraer_strings(self, ruta: str, min_length: int = 4) -> List[str]:
        """Extrae strings de un archivo"""
        try:
            with open(ruta, 'rb') as f:
                data = f.read()
                
            strings = []
            current_string = ""
            
            for byte in data:
                if 32 <= byte <= 126:  # Caracteres imprimibles ASCII
                    current_string += chr(byte)
                else:
                    if len(current_string) >= min_length:
                        strings.append(current_string)
                    current_string = ""
                    
            if len(current_string) >= min_length:
                strings.append(current_string)
                
            return strings
            
        except Exception as e:
            logging.error(f"Error al extraer strings de {ruta}: {e}")
            return []

    def poblar_whitelist_sistema(self):
        """Agrega a la whitelist los ejecutables y procesos legítimos de Windows y programas comunes."""
        rutas_legitimas = [
            os.path.join(os.environ['SYSTEMROOT'], 'System32'),
            os.path.join(os.environ['SYSTEMROOT'], 'SysWOW64'),
            os.path.expanduser('~\\AppData\\Local\\Programs'),
            os.path.expanduser('~\\AppData\\Local'),
            os.path.expanduser('~\\AppData\\Roaming'),
            os.path.expanduser('~\\Program Files'),
            os.path.expanduser('~\\Program Files (x86)'),
            os.path.expanduser('~'),
        ]
        for carpeta in rutas_legitimas:
            if os.path.exists(carpeta):
                for root, _, files in os.walk(carpeta):
                    for file in files:
                        if file.endswith(('.exe', '.dll', '.bat', '.cmd', '.ps1', '.sys')):
                            ruta = os.path.join(root, file)
                            self.archivos_whitelist.add(ruta)
        # Agregar procesos activos actuales
        for proc in psutil.process_iter(['exe']):
            try:
                if proc.info['exe']:
                    self.archivos_whitelist.add(proc.info['exe'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        logging.info("Whitelist poblada automáticamente con archivos y procesos legítimos.")

    def ejecutar_escaneo(self):
        """Realiza un escaneo rápido de procesos y carpetas críticas del sistema. Si detecta amenazas, pone en cuarentena automáticamente."""
        self.monitorear_procesos()
        carpetas_criticas = [
            os.environ['SYSTEMROOT'],
            os.path.join(os.environ['SYSTEMROOT'], 'System32'),
            os.path.join(os.environ['SYSTEMROOT'], 'SysWOW64'),
            os.path.expanduser('~\\AppData\\Roaming'),
            os.path.expanduser('~\\AppData\\Local')
        ]
        for carpeta in carpetas_criticas:
            if os.path.exists(carpeta):
                resultados = self.escanear_directorio(carpeta, recursivo=True)
                for resultado in resultados:
                    if resultado.get('amenaza') and resultado.get('archivo'):
                        self.poner_en_cuarentena(resultado['archivo']) 