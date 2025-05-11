"""
Módulo para manejar los comandos del asistente.
Contiene la lógica para procesar y ejecutar comandos de forma natural.
"""

import os
import webbrowser
import subprocess
import json
import ctypes
from src.core.config import COMANDOS_BASICOS, ASISTENTE_NOMBRE
from src.utils.system_utils import (
    obtener_hora,
    obtener_fecha,
    obtener_info_sistema,
    formatear_info_sistema
)
from src.utils.app_scanner import AppScanner
from difflib import SequenceMatcher
from src.utils.web_search import buscar_duckduckgo
from src.memoria.memoria import MemoriaContextual
from src.memoria.contexto import ContextoConversacional
from src.emociones.emociones import GestorEmociones
from src.core.feedback import FeedbackEntrenamiento
import re
import random
import psutil
import platform
import threading
import time

class CommandHandler:
    def __init__(self, nutricion_activa=True):
        """Inicializa el manejador de comandos con los comandos disponibles."""
        self.comandos = {
            "hora": self._comando_hora,
            "fecha": self._comando_fecha,
            "sistema": self._comando_sistema,
            "ayuda": self._comando_ayuda,
            "abrir": self._comando_abrir,
            "aplicaciones": self._comando_aplicaciones,
            "buscar": self._comando_buscar,
            "limpiar": self._comando_limpiar,
            "recuerda": self._comando_recuerda,
            "recuerdos": self._comando_recuerdos,
            "escanear": self._comando_escanear
        }
        self.app_scanner = AppScanner()
        self.memoria = MemoriaContextual(nutricion_activa=nutricion_activa)
        self.contexto = ContextoConversacional()
        self.emociones = GestorEmociones()
        self.feedback = FeedbackEntrenamiento()
        self.personalizadas_path = 'data/apps_personalizadas.json'
        self.personalizadas = self._cargar_personalizadas()
        self.ultima_app_fallida = None
        self.esperando_ruta_personalizada = False
        self.ruta_temp = None
        self.esperando_nombre_personalizado = False
        # Plugins y APIs pueden inicializarse aquí

    def _cargar_personalizadas(self):
        try:
            with open(self.personalizadas_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {k.lower(): v for k, v in data.items() if not k.startswith('_')}
        except Exception:
            return {}

    def _guardar_personalizadas(self):
        try:
            with open(self.personalizadas_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
        for k, v in self.personalizadas.items():
            data[k] = v
        with open(self.personalizadas_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def procesar_comando(self, entrada):
        """Procesa la entrada del usuario de forma natural."""
        # Convertir entrada a minúsculas para comparación
        entrada_lower = entrada.lower()
        
        # Patrones de reconocimiento para comandos
        patrones = {
            r"(?:qué|que) hora es": self._comando_hora,
            r"(?:qué|que) fecha es": self._comando_fecha,
            r"(?:muestra|dame|quiero ver) (?:la )?hora": self._comando_hora,
            r"(?:muestra|dame|quiero ver) (?:la )?fecha": self._comando_fecha,
            r"(?:muestra|dame|quiero ver) (?:información|info) del sistema": self._comando_sistema,
            r"(?:abre|inicia|ejecuta) (.+)": self._comando_abrir_natural,
            r"(?:busca|encuentra|busca en internet) (.+)": self._comando_buscar_natural,
            r"(?:recuerda|guarda|memoriza) que (.+)": self._comando_recuerda_natural,
            r"(?:qué|que) recuerdos tienes": self._comando_recuerdos,
            r"(?:muestra|dame|quiero ver) (?:los )?comandos": self._comando_ayuda
        }
        
        # Buscar coincidencias con patrones
        for patron, funcion in patrones.items():
            match = re.search(patron, entrada_lower)
            if match:
                # Si hay grupos capturados, pasarlos como argumentos
                if match.groups():
                    return funcion([match.group(0)] + list(match.groups()))
                return funcion([match.group(0)])
        
        # Si no hay coincidencias con patrones, intentar con comandos directos
        palabras = entrada_lower.split()
        if palabras[0] in self.comandos:
            return self.comandos[palabras[0]](palabras)
            
        return None

    def _comando_abrir_natural(self, partes):
        """Versión natural del comando abrir."""
        app_name = partes[1]
        return self._comando_abrir(["abrir", app_name])

    def _comando_buscar_natural(self, partes):
        """Versión natural del comando buscar."""
        busqueda = partes[1]
        return self._comando_buscar(["buscar", busqueda])

    def _comando_recuerda_natural(self, partes):
        """Versión natural del comando recuerda."""
        contenido = partes[1]
        return self._comando_recuerda(["recuerda", contenido])

    def _comando_hora(self, partes):
        """Maneja el comando de hora de forma natural."""
        hora = obtener_hora()
        respuestas = [
            f"Son las {hora} ⌚",
            f"La hora actual es {hora} ⌚",
            f"Ahora mismo son las {hora} ⌚"
        ]
        return random.choice(respuestas)

    def _comando_fecha(self, partes):
        """Maneja el comando de fecha de forma natural."""
        fecha = obtener_fecha()
        respuestas = [
            f"Hoy es {fecha} 📅",
            f"La fecha actual es {fecha} 📅",
            f"Estamos a {fecha} 📅"
        ]
        return random.choice(respuestas)

    def _comando_sistema(self, partes):
        """Maneja el comando de información del sistema de forma natural."""
        info = obtener_info_sistema()
        return f"📊 Aquí tienes la información del sistema:\n{formatear_info_sistema(info)}"

    def _comando_ayuda(self, partes):
        """Maneja el comando de ayuda de forma natural."""
        mensaje = "Claro, puedo ayudarte con varias cosas:\n"
        for comando, descripcion in COMANDOS_BASICOS.items():
            mensaje += f"- {descripcion}\n"
        mensaje += "\nPuedes preguntarme de forma natural, por ejemplo:\n"
        mensaje += "- '¿Qué hora es?'\n"
        mensaje += "- 'Abre Chrome'\n"
        mensaje += "- 'Busca información sobre...'\n"
        return mensaje

    def _abrir_ruta(self, ruta):
        try:
            if not os.path.exists(ruta):
                return False, f"La ruta '{ruta}' no existe."
            if ruta.lower().endswith('.lnk'):
                os.startfile(ruta)
                return True, None
            elif ruta.lower().endswith('.exe'):
                if ctypes.windll.shell32.IsUserAnAdmin():
                    subprocess.Popen(ruta)
                    return True, None
                else:
                    try:
                        subprocess.Popen(["runas", "/user:Administrator", ruta], shell=True)
                        return True, None
                    except Exception as e:
                        return False, str(e)
            else:
                os.startfile(ruta)
                return True, None
        except Exception as e:
            return False, str(e)

    def _comando_abrir(self, texto):
        """Abre una aplicación por nombre o ruta."""
        import os
        import subprocess
        import shutil
        texto = texto.lower().replace('abrir', '').strip()
        apps = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'word': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
            'excel': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
            'notepad': 'notepad.exe',
            'calculadora': 'calc.exe',
            'explorador': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'paint': 'mspaint.exe',
            'bloc de notas': 'notepad.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        }
        for nombre, ruta in apps.items():
            if nombre in texto:
                try:
                    if os.path.exists(ruta):
                        os.startfile(ruta)
                    else:
                        subprocess.Popen(ruta, shell=True)
                    return f"Abriendo {nombre.capitalize()}..."
                except Exception as e:
                    return f"No pude abrir {nombre}: {e}"
        if os.path.exists(texto):
            try:
                os.startfile(texto)
                return f"Abriendo {texto}..."
            except Exception as e:
                return f"No pude abrir {texto}: {e}"
        return "No reconozco esa aplicación o ruta. Puedes intentar con el nombre exacto o la ruta completa."

    def _registrar_ruta_personalizada(self):
        return "Por favor, pega la ruta completa del ejecutable (.exe) o acceso directo (.lnk) de la aplicación que quieres registrar."

    def _guardar_ruta_personalizada_final(self, nombre, ruta):
        self.personalizadas[nombre] = ruta
        self._guardar_personalizadas()
        self.ultima_app_fallida = None
        self.ruta_temp = None
        self.esperando_nombre_personalizado = False
        return f"¡Ruta registrada! Ahora podré abrir '{nombre}' usando: {ruta}"

    def _comando_aplicaciones(self, partes):
        """Maneja el comando para listar aplicaciones disponibles."""
        apps = self.app_scanner.get_all_apps()
        if apps:
            mensaje = "📱 Aplicaciones instaladas por el usuario:\n"
            for app in sorted(apps):
                mensaje += f"- {app}\n"
            return mensaje
        return "No se encontraron aplicaciones instaladas por el usuario 😕"

    def _comando_buscar(self, partes):
        """Maneja el comando de búsqueda web."""
        if len(partes) < 2:
            return "Por favor, especifica qué quieres buscar. Por ejemplo: 'buscar gatos' 🔍"
        busqueda = " ".join(partes[1:])
        resultado = buscar_duckduckgo(busqueda)
        return f"🔎 Resultado de la web para '{busqueda}':\n{resultado}"

    def _comando_limpiar(self, partes):
        """Maneja el comando de limpiar pantalla."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return "¡Pantalla limpia! ✨"

    def _comando_recuerda(self, partes):
        contenido = " ".join(partes[1:])
        if not contenido:
            return "¿Qué quieres que recuerde? Ejemplo: 'recuerda que mi color favorito es azul'"
        self.memoria.guardar_recuerdo(contenido, tipo="hecho_usuario")
        return f"¡Hecho recordado! Siempre lo tendré presente."

    def _comando_recuerdos(self, partes):
        if len(partes) > 1:
            palabra = " ".join(partes[1:])
            recuerdos = self.memoria.buscar_recuerdos(palabra)
            if recuerdos:
                return "📚 Recuerdos encontrados:\n" + "\n".join([f"- {r[0]} ({r[1][:19]})" for r in recuerdos])
            else:
                return "No tengo recuerdos sobre eso todavía."
        else:
            ultimos = self.memoria.ultimos_recuerdos()
            if ultimos:
                return "🧠 Mis últimos recuerdos:\n" + "\n".join([f"- {r[0]} ({r[1][:19]})" for r in ultimos])
            else:
                return "Aún no tengo recuerdos almacenados."

    def _comando_escanear(self, partes):
        """Muestra un escaneo básico del equipo: CPU, RAM, disco y red."""
        info = []
        info.append(f"Sistema operativo: {platform.system()} {platform.release()} ({platform.version()})")
        info.append(f"Procesador: {platform.processor()}")
        info.append(f"Núcleos físicos: {psutil.cpu_count(logical=False)} | Lógicos: {psutil.cpu_count(logical=True)}")
        info.append(f"Uso de CPU: {psutil.cpu_percent()}%")
        info.append(f"RAM usada: {psutil.virtual_memory().used // (1024**2)} MB / {psutil.virtual_memory().total // (1024**2)} MB")
        info.append(f"Disco principal: {psutil.disk_usage('/').used // (1024**3)} GB usados de {psutil.disk_usage('/').total // (1024**3)} GB")
        net = psutil.net_io_counters()
        info.append(f"Red: enviados {net.bytes_sent // (1024**2)} MB, recibidos {net.bytes_recv // (1024**2)} MB")
        return "\n".join(info)

    def iniciar_monitoreo_procesos(self, intervalo=10):
        """Inicia un hilo que monitorea procesos y alerta si detecta algo raro."""
        if hasattr(self, '_monitoreo_procesos_activo') and self._monitoreo_procesos_activo:
            return  # Ya está corriendo
        self._monitoreo_procesos_activo = True
        self._procesos_previos = set(p.info['name'] for p in psutil.process_iter(['name']))
        self._alertas_previas = set()
        def monitor():
            while self._monitoreo_procesos_activo:
                try:
                    procesos_actuales = {p.info['name']: p.info for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info'])}
                    nuevos = set(procesos_actuales.keys()) - self._procesos_previos
                    for nombre in nuevos:
                        alerta = f"[ALERTA] Nuevo proceso detectado: {nombre}"
                        if alerta not in self._alertas_previas:
                            print(alerta)
                            self._alertas_previas.add(alerta)
                    # Alto consumo de CPU o RAM
                    for nombre, info in procesos_actuales.items():
                        cpu = info.get('cpu_percent', 0)
                        mem = info.get('memory_info').rss // (1024**2) if info.get('memory_info') else 0
                        if cpu > 50:
                            alerta = f"[ALERTA] Proceso {nombre} usa mucha CPU: {cpu}%"
                            if alerta not in self._alertas_previas:
                                print(alerta)
                                self._alertas_previas.add(alerta)
                        if mem > 500:
                            alerta = f"[ALERTA] Proceso {nombre} usa mucha RAM: {mem} MB"
                            if alerta not in self._alertas_previas:
                                print(alerta)
                                self._alertas_previas.add(alerta)
                    self._procesos_previos = set(procesos_actuales.keys())
                except Exception as e:
                    print(f"[ERROR Monitoreo Procesos]: {e}")
                time.sleep(intervalo)
        threading.Thread(target=monitor, daemon=True).start()

    def iniciar_monitoreo_red(self, intervalo=10, umbral_mb=100):
        """Inicia un hilo que monitorea la red y alerta si detecta tráfico elevado o conexiones sospechosas."""
        if hasattr(self, '_monitoreo_red_activo') and self._monitoreo_red_activo:
            return  # Ya está corriendo
        self._monitoreo_red_activo = True
        self._alertas_red_previas = set()
        import socket
        def monitor():
            net_prev = psutil.net_io_counters()
            while self._monitoreo_red_activo:
                try:
                    net_now = psutil.net_io_counters()
                    enviados = (net_now.bytes_sent - net_prev.bytes_sent) // (1024**2)
                    recibidos = (net_now.bytes_recv - net_prev.bytes_recv) // (1024**2)
                    if enviados > umbral_mb:
                        alerta = f"[ALERTA RED] Tráfico de subida elevado: {enviados} MB en {intervalo}s"
                        if alerta not in self._alertas_red_previas:
                            print(alerta)
                            self._alertas_red_previas.add(alerta)
                    if recibidos > umbral_mb:
                        alerta = f"[ALERTA RED] Tráfico de bajada elevado: {recibidos} MB en {intervalo}s"
                        if alerta not in self._alertas_red_previas:
                            print(alerta)
                            self._alertas_red_previas.add(alerta)
                    # Conexiones activas
                    conexiones = psutil.net_connections(kind='inet')
                    conexiones_externas = [c for c in conexiones if c.raddr and c.status == 'ESTABLISHED']
                    if len(conexiones_externas) > 50:
                        alerta = f"[ALERTA RED] Muchas conexiones externas activas: {len(conexiones_externas)}"
                        if alerta not in self._alertas_red_previas:
                            print(alerta)
                            self._alertas_red_previas.add(alerta)
                    # Conexiones a puertos inusuales
                    puertos_sospechosos = [c for c in conexiones_externas if c.raddr.port not in (80, 443, 53, 22, 25, 110, 143)]
                    if puertos_sospechosos:
                        alerta = f"[ALERTA RED] Conexiones a puertos inusuales: {[c.raddr.port for c in puertos_sospechosos]}"
                        if alerta not in self._alertas_red_previas:
                            print(alerta)
                            self._alertas_red_previas.add(alerta)
                    net_prev = net_now
                except Exception as e:
                    print(f"[ERROR Monitoreo Red]: {e}")
                time.sleep(intervalo)
        threading.Thread(target=monitor, daemon=True).start() 