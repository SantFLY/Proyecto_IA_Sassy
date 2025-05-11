import sys
import os
from contextlib import contextmanager
from llama_cpp import Llama
from typing import Dict, Any, Optional
import json

@contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class ModeloLlama:
    def __init__(
        self,
        model_path: str = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        n_ctx: int = 2048,
        n_threads: int = 4,
        n_batch: int = 64,
        temperatura: float = 0.7,
        top_p: float = 0.95,
        max_tokens: int = 256
    ):
        """Inicializa el modelo Mistral Instruct con configuración optimizada para español y eficiencia."""
        abs_model_path = os.path.abspath(model_path)
        with suppress_stdout_stderr():
            self.model = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_batch=n_batch,
                verbose=False
            )
        self.temperatura = temperatura
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.system_prompt = (
            "Eres Sassy, una asistente virtual inteligente y empática. "
            "Tu objetivo es ayudar al usuario de manera natural y conversacional. "
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

    def generar_respuesta(
        self,
        prompt: str,
        contexto: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Genera una respuesta usando el modelo Llama."""
        prompt_completo = self._construir_prompt(prompt, contexto)
        try:
            respuesta = self.model(
                prompt_completo,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperatura,
                top_p=self.top_p,
                stop=["User:", "\n\n"],
                echo=False
            )
            return respuesta['choices'][0]['text'].strip()
        except Exception as e:
            print(f"[ERROR Llama]: {e}")
            return "Lo siento, tuve un problema para responder. ¿Puedes intentarlo de nuevo?"

    def _construir_prompt(
        self,
        prompt: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construye el prompt completo con el contexto y fuerza el español con ejemplos claros."""
        prompt_completo = f"{self.system_prompt}\n\n"
        if contexto:
            if 'memoria' in contexto:
                prompt_completo += f"Contexto de memoria: {json.dumps(contexto['memoria'], ensure_ascii=False)}\n"
            if 'emociones' in contexto:
                prompt_completo += f"Estado emocional: {json.dumps(contexto['emociones'], ensure_ascii=False)}\n"
        prompt_completo += f"User: {prompt}\nSassy:"
        return prompt_completo

    def ajustar_parametros(
        self,
        temperatura: float = 0.7,
        top_p: float = 0.95,
        max_tokens: int = 256
    ) -> None:
        """Ajusta los parámetros de generación del modelo."""
        self.temperatura = temperatura
        self.top_p = top_p
        self.max_tokens = max_tokens 