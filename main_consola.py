"""
Archivo principal del asistente.
Punto de entrada de la aplicación.
"""

import os
import sys
import ctypes
import subprocess
import logging
from pathlib import Path
from typing import Optional
import threading
import time
import select

# Forzar cwd a la raíz del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Asegura que la raíz esté en sys.path
root_path = os.path.abspath(os.path.dirname(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Asegura que la carpeta logs exista
os.makedirs("logs", exist_ok=True)

# Configurar logging a archivo y consola SOLO para errores
logging.basicConfig(
    level=logging.ERROR,  # Solo errores
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sassy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Silenciar logs de librerías externas
logging.getLogger("faiss.loader").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("faiss").setLevel(logging.WARNING)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Solicitando permisos de administrador...")
    # Forzar cwd a la raíz del proyecto
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    try:
        print(f"Relanzando como admin en: {script_dir}")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
    except Exception as e:
        print(f"No se pudo solicitar permisos de administrador: {e}")
        input("Presiona Enter para salir...")
    sys.exit()
else:
    print(f"🛡️ El asistente se está ejecutando en modo administrador.\nCWD: {os.getcwd()}")

print('Importando Asistente...')
from src.core.asistente import Asistente
print('Importando AnalizadorIntencion, EjecutorAcciones, SistemaAprendizaje, SistemaProactivo...')
from src.autonomia import (
    AnalizadorIntencion,
    EjecutorAcciones,
    SistemaAprendizaje,
    SistemaProactivo
)
print('Importando AntivirusSassy...')
from src.proteccion.antivirus import AntivirusSassy
print('Importando ModeloLlama...')
from src.modelos.modelo_llama import ModeloLlama

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

class AsistenteAutonomo(Asistente):
    def __init__(self, nutricion_activa=False):
        super().__init__(nutricion_activa)
        self.modelo_local = ModeloLlama()
        self.analizador = AnalizadorIntencion(self.modelo_local)
        self.ejecutor = EjecutorAcciones()
        self.aprendizaje = SistemaAprendizaje()
        self.proactivo = SistemaProactivo()
        Path("data/aprendizaje").mkdir(parents=True, exist_ok=True)
        logging.info("Sistema de autonomía y protección inicializado")

    def _iniciar_sistemas_background(self):
        """Inicia todos los sistemas de protección y monitoreo en segundo plano"""
        # Hilo para el antivirus y firewall
        # self.hilo_seguridad = threading.Thread(
        #     target=self._ejecutar_seguridad_background,
        #     daemon=True
        # )
        # self.hilo_seguridad.start()

        # Hilo para el sistema proactivo
        self.hilo_proactivo = threading.Thread(
            target=self._ejecutar_proactivo_background,
            daemon=True
        )
        self.hilo_proactivo.start()

        # Hilo para el sistema de aprendizaje
        self.hilo_aprendizaje = threading.Thread(
            target=self._ejecutar_aprendizaje_background,
            daemon=True
        )
        self.hilo_aprendizaje.start()

    def _ejecutar_seguridad_background(self):
        """Ejecuta el antivirus y firewall en segundo plano"""
        while True:
            try:
                # Ejecutar escaneo de seguridad
                self.antivirus.ejecutar_escaneo()
                # Esperar antes del siguiente ciclo
                time.sleep(300)  # 5 minutos entre escaneos
            except Exception as e:
                logging.error(f"Error en sistema de seguridad: {e}")
                time.sleep(60)  # Esperar 1 minuto si hay error

    def _ejecutar_proactivo_background(self):
        """Ejecuta el sistema proactivo en segundo plano"""
        while True:
            try:
                # Ejecutar acciones proactivas
                self.proactivo.ejecutar_acciones_proactivas()
                # Esperar antes del siguiente ciclo
                time.sleep(60)  # 1 minuto entre ciclos
            except Exception as e:
                logging.error(f"Error en sistema proactivo: {e}")
                time.sleep(30)

    def _ejecutar_aprendizaje_background(self):
        """Ejecuta el sistema de aprendizaje en segundo plano"""
        while True:
            try:
                # Ejecutar aprendizaje continuo
                self.aprendizaje.ejecutar_aprendizaje_continuo()
                # Esperar antes del siguiente ciclo
                time.sleep(3600)  # 1 hora entre ciclos de aprendizaje
            except Exception as e:
                logging.error(f"Error en sistema de aprendizaje: {e}")
                time.sleep(300)

    def ejecutar(self):
        """Ejecuta el asistente de forma autónoma"""
        try:
            self._saludar()
            while True:
                try:
                    entrada = input("\nTú: ")
                    if entrada.lower() in ['salir', 'exit', 'quit']:
                        break
                    elif entrada.lower() == 'estado':
                        self._mostrar_estado_sistema()
                        continue
                    elif entrada.lower() == 'alertas':
                        self._mostrar_alertas()
                        continue
                    respuesta = self.procesar_entrada(entrada)
                    print(f"\nSassy: {respuesta}")
                except KeyboardInterrupt:
                    print("\nSassy: ¿Necesitas algo más?")
                    continue
                except Exception as e:
                    logging.error(f"Error en el bucle principal: {e}")
                    print("\nSassy: Lo siento, hubo un error. ¿Podrías repetir?")
                    continue
        except Exception as e:
            logging.error(f"Error en la ejecución del asistente: {e}")
            print(f"\nError: {e}")
        finally:
            self._detener_sistemas()

    def _mostrar_estado_sistema(self):
        """Muestra el estado actual de todos los sistemas"""
        print("\n=== Estado del Sistema ===")
        # print(f"Antivirus: {'Activo' if self.antivirus.monitoreo_activo else 'Inactivo'}")
        print(f"Sistema Proactivo: Activo")
        print(f"Sistema de Aprendizaje: {'Activo' if self.aprendizaje.activo else 'Inactivo'}")
        print("========================")

    def _mostrar_alertas(self):
        """Muestra las alertas activas del sistema"""
        # alertas = self.antivirus.obtener_alertas()
        # if alertas:
        #     print("\n=== Alertas Activas ===")
        #     for alerta in alertas:
        #         print(f"- {alerta}")
        #     print("======================")
        # else:
        print("\nNo hay alertas activas en este momento.")

    def _detener_sistemas(self):
        """Detiene todos los sistemas de forma segura"""
        try:
            # Detener antivirus
            if hasattr(self.antivirus, 'detener_monitoreo'):
                self.antivirus.detener_monitoreo()
            
            # Detener sistema proactivo
            if hasattr(self.proactivo, 'detener'):
                self.proactivo.detener()
            
            # Detener sistema de aprendizaje
            if hasattr(self.aprendizaje, 'detener'):
                self.aprendizaje.detener()
            
            logging.info("Todos los sistemas detenidos correctamente")
        except Exception as e:
            logging.error(f"Error al detener sistemas: {e}")

    def procesar_entrada(self, entrada: str) -> str:
        """Procesa la entrada del usuario y genera una respuesta SOLO usando el modelo y la memoria."""
        try:
            respuesta = self.response_generator.generar_respuesta(entrada)
            return respuesta
        except Exception as e:
            logging.error(f"Error al procesar entrada: {e}")
            print(f"[ERROR en procesar_entrada]: {e}")
            return "Lo siento, hubo un error al procesar tu mensaje. ¿Podrías reformularlo?"

if __name__ == "__main__":
    try:
        NUTRICION_ACTIVA = False
        asistente = AsistenteAutonomo(nutricion_activa=NUTRICION_ACTIVA)
        asistente.ejecutar()
    except Exception as e:
        print(f"Error crítico al iniciar el asistente: {e}")
        logging.error(f"Error crítico al iniciar el asistente: {e}")
        input("Presiona Enter para salir...")
