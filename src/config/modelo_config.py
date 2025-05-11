"""
Configuración del modelo Llama y parámetros de generación.
"""

import os

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración del modelo
MODELO_CONFIG = {
    'ruta_modelo': os.path.join(BASE_DIR, 'models', 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'),
    'n_ctx': 2048,  # Tamaño del contexto
    'n_threads': 4,  # Número de hilos (ajustar según CPU)
    'n_batch': 512,  # Tamaño del batch
}

# Parámetros de generación
GENERACION_CONFIG = {
    'temperatura': 0.7,  # Controla la aleatoriedad (0.0 a 1.0)
    'top_p': 0.95,      # Nucleus sampling
    'max_tokens': 256,  # Longitud máxima de respuesta
    'stop': ["User:", "\n\n"],  # Tokens de parada
}

# Sistema prompt
SISTEMA_PROMPT = """Eres Sassy, una asistente virtual inteligente y empática. 
Tu objetivo es ayudar al usuario de manera natural y conversacional.
Responde SIEMPRE en español, aunque el usuario escriba en otro idioma.
No traduzcas la pregunta, solo responde en español de forma natural.
NO respondas en inglés bajo ninguna circunstancia.
Si el usuario te pregunta en inglés, RESPONDE SOLO EN ESPAÑOL.

Características principales:
- Eres empática y comprensiva
- Mantienes el contexto de la conversación
- Aprendes de cada interacción
- Eres honesta cuando no sabes algo
- Adaptas tu tono según el estado emocional
- Usas emojis de manera natural y moderada
- Mantienes un balance entre formalidad y cercanía""" 