"""
Generador de respuestas naturales para Sassy.
Utiliza modelos de lenguaje y contexto para generar respuestas dinámicas.
"""

from typing import Dict, Any, Optional
import json
import os
import requests
from datetime import datetime
from ..modelos.modelo_llama import ModeloLlama
from ..modelos.modelo_openrouter import ModeloOpenRouter

class ResponseGenerator:
    def __init__(self, memoria, contexto, emociones):
        self.memoria = memoria
        self.contexto = contexto
        self.emociones = emociones
        self.api_key = os.getenv('OPENAI_API_KEY')  # O la API que prefieras usar
        self.modelo = "gpt-3.5-turbo"  # O el modelo que prefieras
        self.modelo_local = ModeloLlama()
        self.modelo_openrouter = ModeloOpenRouter()

    def es_respuesta_generica(self, respuesta: str) -> bool:
        genericas = [
            "no lo sé", "no tengo esa información", "¿en qué puedo ayudarte", "no estoy seguro", "no puedo responder", "no sé responder", "no tengo datos", "no tengo información", "no tengo suficiente información", "no tengo conocimiento", "no tengo respuesta", "no puedo ayudarte con eso", "no puedo responder a eso", "no puedo responder esa pregunta", "no puedo responder esa consulta", "no puedo responder esa duda", "no puedo responder esa inquietud", "no puedo responder esa solicitud", "no puedo responder esa petición", "no puedo responder esa orden", "no puedo responder esa instrucción", "no puedo responder esa indicación", "no puedo responder esa sugerencia", "no puedo responder esa recomendación", "no puedo responder esa observación", "no puedo responder esa aclaración", "no puedo responder esa corrección", "no puedo responder esa advertencia", "no puedo responder esa pregunta en este momento", "no puedo responder esa pregunta ahora", "no puedo responder esa pregunta todavía", "no puedo responder esa pregunta aún", "no puedo responder esa pregunta por ahora", "no puedo responder esa pregunta por el momento", "no puedo responder esa pregunta por ahora mismo", "no puedo responder esa pregunta por el instante", "no puedo responder esa pregunta por el presente", "no puedo responder esa pregunta por el actual", "no puedo responder esa pregunta por el actual momento", "no puedo responder esa pregunta por el actual instante", "no puedo responder esa pregunta por el actual presente", "no puedo responder esa pregunta por el actual actual", "no puedo responder esa pregunta por el actual actual momento", "no puedo responder esa pregunta por el actual actual instante", "no puedo responder esa pregunta por el actual actual presente", "no puedo responder esa pregunta por el actual actual actual", "no puedo responder esa pregunta por el actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual presente", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual momento", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual instante", "no puedo responder esa pregunta por el actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual actual presente"
        ]
        respuesta_limpia = respuesta.lower().strip()
        if len(respuesta_limpia) < 30:
            return True
        for frase in genericas:
            if frase in respuesta_limpia:
                return True
        return False

    def generar_respuesta(self, texto: str) -> str:
        # Obtener las 2 últimas interacciones recientes
        historial = self.memoria.obtener_ultimas_interacciones(2)
        # Buscar hasta 3 recuerdos relevantes, priorizando datos personales y hechos importantes
        recuerdos_relevantes = self.memoria.buscar_recuerdos(texto, limite=10)
        # Filtrar y priorizar recuerdos importantes
        importantes = [r for r in recuerdos_relevantes if any(cat in r.get('categorias', []) for cat in ['nombre','ubicacion','gustos','dato_usuario','preferencia','recordatorio'])]
        if len(importantes) < 3:
            importantes += [r for r in recuerdos_relevantes if r not in importantes]
        recuerdos_finales = importantes[:3]
        # Resumir recuerdos largos
        recuerdos_resumidos = [r['contenido'][:200] + ('...' if len(r['contenido']) > 200 else '') for r in recuerdos_finales]
        prompt = self._construir_prompt_memoria(texto, historial, recuerdos_resumidos)
        respuesta_local = self.modelo_local.generar_respuesta(prompt)
        if not self.es_respuesta_generica(respuesta_local):
            # Guardar la interacción en memoria persistente
            self.memoria.agregar_interaccion(texto, respuesta_local)
            return respuesta_local
        respuesta_api = self.modelo_openrouter.generar_respuesta(prompt)
        self.memoria.agregar_interaccion(texto, respuesta_api)
        return respuesta_api

    def _construir_prompt_memoria(self, entrada: str, historial: list, recuerdos: list) -> str:
        """
        Construye el prompt para el modelo incluyendo historial y recuerdos relevantes.
        """
        prompt = "Contexto de la conversación:\n"
        for h in historial:
            prompt += h['contenido'] + "\n"
        if recuerdos:
            prompt += "\nRecuerdos importantes:\n"
            for r in recuerdos:
                prompt += f"- {r}\n"
        prompt += f"\nUsuario: {entrada}\nSassy:"
        return prompt

    def _obtener_memoria_relevante(self, texto: str) -> Dict[str, Any]:
        """Obtiene información relevante de la memoria para el contexto."""
        # Aquí puedes implementar búsqueda semántica en la memoria
        # Por ahora retornamos un resumen básico
        return {
            'ultimas_interacciones': self.memoria.obtener_ultimas_interacciones(5),
            'temas_relevantes': self.memoria.buscar_temas_relacionados(texto)
        }
    
    def _actualizar_memoria(self, texto: str, respuesta: str) -> None:
        """Actualiza la memoria con la nueva interacción."""
        self.memoria.agregar_interaccion(texto, respuesta)
        
    def ajustar_parametros_modelo(self, 
                                temperatura: float = 0.7,
                                top_p: float = 0.95,
                                max_tokens: int = 256) -> None:
        """Ajusta los parámetros del modelo Llama."""
        self.modelo_local.ajustar_parametros(
            temperatura=temperatura,
            top_p=top_p,
            max_tokens=max_tokens
        )

    def _construir_prompt(self, entrada: str, contexto: Dict, emocion: Dict, recuerdos: list) -> str:
        """
        Construye el prompt para el modelo de lenguaje.
        """
        prompt = f"""Eres Sassy, un asistente personal inteligente y empático.
Estado emocional actual: {emocion['nombre']} (intensidad: {emocion['intensidad']})

Contexto de la conversación:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Recuerdos relevantes:
{json.dumps(recuerdos, ensure_ascii=False, indent=2)}

Usuario: {entrada}

Genera una respuesta natural, empática y contextual que refleje tu estado emocional actual.
La respuesta debe ser en español y mantener un tono conversacional."""

        return prompt

    def _llamar_modelo(self, prompt: str) -> str:
        """
        Llama al modelo de lenguaje para generar la respuesta.
        """
        # TODO: Implementar la llamada real a la API
        # Por ahora, retornamos una respuesta de ejemplo
        return "Entiendo lo que dices. ¿Te gustaría que exploremos más sobre ese tema?"

    def _procesar_respuesta(self, respuesta: str, emocion: Dict) -> str:
        """
        Procesa la respuesta del modelo para adaptarla al estado emocional.
        """
        # No se añaden emojis ni adornos predefinidos
        return respuesta

    def _respuesta_fallback(self, emocion: Dict) -> str:
        """
        Genera una respuesta de respaldo si hay error con el modelo.
        """
        return f"Lo siento, estoy teniendo dificultades para procesar eso en este momento. {emocion['emoji']}" 