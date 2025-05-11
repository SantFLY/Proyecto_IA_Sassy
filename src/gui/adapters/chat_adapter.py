from src.core.asistente import Asistente
from src.core.response_generator import ResponseGenerator
from src.modelos.modelo_llama import ModeloLlama
from src.modelos.modelo_openrouter import ModeloOpenRouter
from src.memoria.memoria import MemoriaContextual
from src.emociones.emociones import GestorEmociones
from src.config.modelo_config import MODELO_CONFIG, GENERACION_CONFIG, SISTEMA_PROMPT
import os
import logging

class ChatAdapter:
    def __init__(self):
        try:
            # Verificar que el modelo existe
            if not os.path.exists(MODELO_CONFIG['ruta_modelo']):
                raise FileNotFoundError(f"No se encontró el modelo en: {MODELO_CONFIG['ruta_modelo']}")
            
            # Inicializar componentes del backend
            self.modelo_local = ModeloLlama(
                model_path=MODELO_CONFIG['ruta_modelo'],
                n_ctx=MODELO_CONFIG['n_ctx'],
                n_threads=MODELO_CONFIG['n_threads'],
                n_batch=MODELO_CONFIG['n_batch'],
                temperatura=GENERACION_CONFIG['temperatura'],
                top_p=GENERACION_CONFIG['top_p'],
                max_tokens=GENERACION_CONFIG['max_tokens']
            )
            
            self.modelo_openrouter = ModeloOpenRouter()
            self.memoria = MemoriaContextual()
            self.emociones = GestorEmociones()
            self.response_generator = ResponseGenerator(
                memoria=self.memoria,
                contexto={},
                emociones=self.emociones
            )
            self.asistente = Asistente(nutricion_activa=False)
            
            logging.info("[ChatAdapter] Inicializado correctamente")
            
        except Exception as e:
            logging.error(f"[ERROR ChatAdapter] Error al inicializar: {e}")
            raise
        
    def procesar_mensaje(self, mensaje: str) -> str:
        """Procesa un mensaje del usuario y retorna la respuesta de Sassy."""
        try:
            # Obtener las 2 últimas interacciones recientes
            historial = self.memoria.obtener_ultimas_interacciones(2)
            
            # Buscar hasta 3 recuerdos relevantes, priorizando datos personales y hechos importantes
            recuerdos_relevantes = self.memoria.buscar_recuerdos(mensaje, limite=10)
            
            # Filtrar y priorizar recuerdos importantes
            importantes = [r for r in recuerdos_relevantes if any(cat in r.get('categorias', []) for cat in ['nombre','ubicacion','gustos','dato_usuario','preferencia','recordatorio'])]
            if len(importantes) < 3:
                importantes += [r for r in recuerdos_relevantes if r not in importantes]
            recuerdos_finales = importantes[:3]
            
            # Resumir recuerdos largos
            recuerdos_resumidos = [r['contenido'][:200] + ('...' if len(r['contenido']) > 200 else '') for r in recuerdos_finales]
            
            # Construir prompt con contexto
            prompt = self.response_generator._construir_prompt_memoria(
                entrada=mensaje,
                historial=historial,
                recuerdos=recuerdos_resumidos
            )
            
            # Generar respuesta
            respuesta_local = self.modelo_local.generar_respuesta(prompt)
            if not self.response_generator.es_respuesta_generica(respuesta_local):
                # Guardar la interacción en memoria persistente
                self.memoria.agregar_interaccion(mensaje, respuesta_local)
                return respuesta_local
                
            respuesta_api = self.modelo_openrouter.generar_respuesta(prompt)
            self.memoria.agregar_interaccion(mensaje, respuesta_api)
            return respuesta_api
            
        except Exception as e:
            logging.error(f"[ERROR ChatAdapter] Error al procesar mensaje: {e}")
            return "Lo siento, tuve un problema para procesar tu mensaje. ¿Podrías intentarlo de nuevo?" 