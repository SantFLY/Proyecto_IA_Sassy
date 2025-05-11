"""
Módulo principal del asistente.
Contiene la clase principal del asistente y sus métodos básicos.
"""

import os
from src.commands.command_handler import CommandHandler
from src.core.config import ASISTENTE_NOMBRE, ASISTENTE_VERSION
from src.leyes import LEY_1, LEY_2, LEY_3
from src.memoria.memoria import MemoriaContextual
from src.memoria.contexto import ContextoConversacional
from src.emociones.emociones import GestorEmociones
from src.core.feedback import FeedbackEntrenamiento
from src.core.response_generator import ResponseGenerator
import random
import re
import threading
import logging

class Asistente:
    def __init__(self, nutricion_activa=True):
        """Inicializa el asistente con su nombre y manejador de comandos."""
        self.nombre = ASISTENTE_NOMBRE
        self.version = ASISTENTE_VERSION
        self.command_handler = CommandHandler(nutricion_activa=nutricion_activa)
        self.memoria = MemoriaContextual(nutricion_activa=nutricion_activa)
        self.contexto = ContextoConversacional()
        self.emociones = GestorEmociones()
        self.feedback = FeedbackEntrenamiento()
        self.response_generator = ResponseGenerator(self.memoria, self.contexto, self.emociones)

    def _saludar(self):
        """No hace nada: Sassy no debe saludar automáticamente ni usar mensajes quemados."""
        pass

    def hablar(self, mensaje):
        """Muestra el mensaje tal cual, sin adornos ni emojis predefinidos."""
        print(f"\n{mensaje}")

    def escuchar(self):
        """Escucha al usuario de forma interactiva y natural."""
        try:
            comando = input(f"\nTú: ").strip()
            return comando
        except KeyboardInterrupt:
            self.hablar("¡Hasta pronto! Que tengas un excelente día 👋")
            return "salir"
        except Exception:
            self.hablar("Ups, algo no salió bien. ¿Podrías repetirlo? 🤔")
            return ""

    def _procesar_entrada(self, entrada):
        """Procesa la entrada del usuario de forma natural y contextual usando siempre el modelo Llama."""
        # Actualizar emoción según la entrada
        self.emociones.actualizar_emocion(entrada, self.contexto.obtener_contexto())
        
        # Procesar comando especial de salida
        if entrada.lower() == "salir":
            # Generar respuesta de despedida usando el modelo, sin mensajes quemados
            respuesta = self.response_generator.generar_respuesta(entrada)
            self.memoria.guardar_recuerdo(respuesta, tipo="asistente", contexto=self.contexto.obtener_contexto())
            return "salir", respuesta
        
        # TODO lo demás va al modelo Llama
        respuesta = self.response_generator.generar_respuesta(entrada)
        self.memoria.guardar_recuerdo(respuesta, tipo="asistente", contexto=self.contexto.obtener_contexto())
        return "conversacion", respuesta

    def _extraer_dato_personal(self, texto):
        patrones = [
            (r"mi nombre es ([\wáéíóúüñ]+)", "nombre"),
            (r"me llamo ([\wáéíóúüñ]+)", "nombre"),
            (r"nací el ([\w\d/\- ]+)", "cumpleaños"),
            (r"mi cumpleaños es ([\w\d/\- ]+)", "cumpleaños"),
            (r"vivo en ([\wáéíóúüñ ]+)", "ciudad"),
            (r"soy de ([\wáéíóúüñ ]+)", "ciudad"),
            (r"mi color favorito es ([\wáéíóúüñ]+)", "color_favorito"),
            (r"mi comida favorita es ([\wáéíóúüñ ]+)", "comida_favorita")
        ]
        for patron, clave in patrones:
            m = re.search(patron, texto.lower())
            if m:
                return clave, m.group(1).strip()
        return None, None

    def _buscar_dato_personal(self, clave):
        # Buscar en recuerdos recientes y en la base de datos
        recuerdos = self.memoria.buscar_recuerdos(clave, limite=10, tipo=None)
        for r in recuerdos:
            if clave in r['contenido'].lower():
                partes = r['contenido'].split(":", 1)
                if len(partes) == 2:
                    return partes[1].strip()
                else:
                    return r['contenido']
        return None

    def _buscar_tema(self, tema):
        # Buscar recuerdos relacionados con un tema
        recuerdos = self.memoria.buscar_recuerdos(tema, limite=5)
        if recuerdos:
            return [r['contenido'] for r in recuerdos]
        return []

    def _procesar_conversacion(self, entrada):
        """Procesa la entrada como una conversación natural, emocional y contextual usando el modelo Llama y los recuerdos."""
        self.emociones.actualizar_emocion(entrada)
        # Si el usuario pregunta por su nombre
        if any(x in entrada.lower() for x in ["como me llamo", "cual es mi nombre", "quien soy", "quien es mi creador"]):
            nombre = self._buscar_dato_personal("nombre")
            if nombre:
                return f"¡Claro! Me dijiste que tu nombre es {nombre}."
            else:
                return "Aún no me has dicho tu nombre. ¿Cómo te llamas?"
        # Si el usuario pregunta por temas anteriores
        if any(x in entrada.lower() for x in ["de que hablamos", "que te dije sobre", "recuerdas cuando"]):
            tema = entrada.lower().split("sobre")[-1].strip() if "sobre" in entrada.lower() else ""
            recuerdos = self._buscar_tema(tema)
            if recuerdos:
                return "Esto es lo que recuerdo sobre ese tema: " + " | ".join(recuerdos)
            else:
                return "No tengo recuerdos sobre ese tema aún. ¿Quieres contarme algo para recordarlo?"
        # Usar el modelo Llama para generar la respuesta y guardar la interacción
        respuesta = self.response_generator.generar_respuesta(entrada)
        self.memoria.agregar_interaccion(entrada, respuesta)
        return respuesta

    def ejecutar(self):
        """Ejecuta el asistente de forma autónoma, con servicios en segundo plano (silenciosos)."""
        try:
            self._saludar()
            # Lanzar servicios en segundo plano (silenciosos)
            def run_bg(target):
                try:
                    target()
                except Exception as e:
                    logging.error(f"[ERROR Servicio BG]: {e}")
            if hasattr(self, 'antivirus'):
                threading.Thread(target=lambda: run_bg(self.antivirus.iniciar_monitoreo_continuo), daemon=True).start()
            if hasattr(self, 'firewall'):
                threading.Thread(target=lambda: run_bg(self.firewall.iniciar_monitoreo), daemon=True).start()
            if hasattr(self, 'proactivo'):
                threading.Thread(target=lambda: run_bg(self.proactivo.iniciar), daemon=True).start()
            if hasattr(self, 'aprendizaje'):
                threading.Thread(target=lambda: run_bg(self.aprendizaje.iniciar), daemon=True).start()
            while True:
                try:
                    entrada = input("\nTú: ")
                    if entrada.strip().lower() == "salir":
                        break
                    respuesta = self._procesar_entrada(entrada)[1]
                    self.hablar(respuesta)
                except KeyboardInterrupt:
                    break
        except Exception as e:
            logging.error(f"[ERROR Asistente]: {e}")
            print(f"[ERROR Asistente]: {e}")
        finally:
            # Guardar estado antes de salir
            self.memoria.guardar_estado_final()
            self.emociones.guardar_estado()
            if hasattr(self.contexto, 'guardar_contexto_final'):
                self.contexto.guardar_contexto_final() 