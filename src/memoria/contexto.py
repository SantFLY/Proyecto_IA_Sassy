"""
Módulo de contexto conversacional para Sassy.
Mantiene el estado y contexto de la conversación actual.
"""

from collections import deque
from datetime import datetime

# Aquí se manejará el contexto de la conversación actual, historial, etc.

class ContextoConversacional:
    def __init__(self, max_historial=10):
        """Inicializa el contexto conversacional."""
        self.historial = deque(maxlen=max_historial)
        self.tema_actual = None
        self.ultima_interaccion = None
        self.estado_emocional = "neutral"
        self.confianza = 0.5  # Nivel de confianza en la comprensión del contexto

    def actualizar_contexto(self, entrada_usuario, respuesta_asistente):
        """Actualiza el contexto con la nueva interacción."""
        timestamp = datetime.now().isoformat()
        
        # Guardar la interacción en el historial
        self.historial.append({
            'timestamp': timestamp,
            'usuario': entrada_usuario,
            'asistente': respuesta_asistente
        })
        
        # Actualizar última interacción
        self.ultima_interaccion = {
            'timestamp': timestamp,
            'entrada': entrada_usuario,
            'respuesta': respuesta_asistente
        }
        
        # Actualizar tema actual basado en la entrada
        self._actualizar_tema(entrada_usuario)
        
        # Actualizar estado emocional
        self._actualizar_estado_emocional(entrada_usuario, respuesta_asistente)

    def _actualizar_tema(self, entrada):
        """Actualiza el tema actual de la conversación."""
        # Aquí se podría implementar un análisis más sofisticado del tema
        palabras_clave = entrada.lower().split()
        if len(palabras_clave) > 0:
            self.tema_actual = palabras_clave[0]

    def _actualizar_estado_emocional(self, entrada, respuesta):
        """Actualiza el estado emocional basado en la interacción."""
        # Aquí se podría implementar un análisis de sentimiento más sofisticado
        palabras_positivas = {'gracias', 'genial', 'excelente', 'bueno', 'me gusta'}
        palabras_negativas = {'no', 'mal', 'error', 'problema', 'fallo'}
        
        entrada_lower = entrada.lower()
        if any(palabra in entrada_lower for palabra in palabras_positivas):
            self.estado_emocional = "positivo"
        elif any(palabra in entrada_lower for palabra in palabras_negativas):
            self.estado_emocional = "negativo"
        else:
            self.estado_emocional = "neutral"

    def obtener_contexto(self):
        """Obtiene el contexto actual de la conversación."""
        return {
            'tema': self.tema_actual,
            'estado_emocional': self.estado_emocional,
            'confianza': self.confianza,
            'ultima_interaccion': self.ultima_interaccion,
            'historial_reciente': list(self.historial)
        }

    def obtener_historial(self, limite=5):
        """Obtiene el historial reciente de la conversación."""
        return list(self.historial)[-limite:]

    def limpiar_contexto(self):
        """Limpia el contexto actual."""
        self.historial.clear()
        self.tema_actual = None
        self.ultima_interaccion = None
        self.estado_emocional = "neutral"
        self.confianza = 0.5 