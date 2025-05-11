import requests
import os
from typing import Optional
from dotenv import load_dotenv

class ModeloOpenRouter:
    def __init__(self, api_key: Optional[str] = None, model: str = "mistralai/mistral-7b-instruct"):
        # Cargar variables de entorno desde .env si existe
        load_dotenv()
        
        # Obtener la clave API de las variables de entorno o del parámetro
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No se encontró la clave API de OpenRouter. "
                "Por favor, configura la variable de entorno OPENROUTER_API_KEY "
                "o proporciona la clave al inicializar la clase."
            )
            
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = (
            "Eres Sassy, una asistente virtual inteligente y empática. "
            "Responde SIEMPRE en español, aunque el usuario escriba en otro idioma. "
            "No traduzcas la pregunta, solo responde en español de forma natural. "
            "NO respondas en inglés bajo ninguna circunstancia. "
            "Si el usuario te pregunta en inglés, RESPONDE SOLO EN ESPAÑOL. "
            "EJEMPLO: Si te preguntan 'How are you?', responde 'Estoy bien, ¿y tú?'. "
            "EJEMPLO: Si te preguntan 'What is your name?', responde 'Me llamo Sassy, ¿y tú?'. "
            "EJEMPLO: Si te preguntan 'Can you help me?', responde 'Claro, ¿en qué puedo ayudarte?'. "
            "Mantén un tono amigable pero profesional. "
            "Usa emojis ocasionalmente para hacer la conversación más natural. "
            "Sé concisa pero completa en tus respuestas. "
            "Si no sabes algo, admítelo honestamente."
        )

    def generar_respuesta(self, prompt: str, contexto: Optional[dict] = None, max_tokens: int = 256) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[ERROR OpenRouter]: {e}")
            return "Lo siento, tuve un problema para responder (OpenRouter). ¿Puedes intentarlo de nuevo?" 