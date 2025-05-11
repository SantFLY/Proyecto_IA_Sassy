import random
import re
from src.memoria.memoria import MemoriaContextual
from src.memoria.contexto import ContextoConversacional

class ResponseGenerator:
    def __init__(self, memoria, contexto, emociones):
        self.memoria = memoria
        self.contexto = contexto
        self.emociones = emociones

    def generar_respuesta(self, entrada):
        contexto_actual = self.contexto.obtener_contexto()
        recuerdos = self.memoria.buscar_recuerdos(entrada, limite=5)
        if recuerdos:
            # Reformular el recuerdo más relevante
            recuerdo = recuerdos[0]['contenido']
            respuesta = self._parafrasear_recuerdo(recuerdo, entrada)
            return respuesta
        # Si no hay recuerdos, pedir al usuario que le enseñe
        return self._preguntar_aprendizaje(entrada)

    def _parafrasear_recuerdo(self, recuerdo, entrada):
        # Reformulación simple: adapta el recuerdo al contexto de la pregunta
        if re.search(r'como me llamo|cual es mi nombre', entrada.lower()):
            if 'nombre' in recuerdo.lower():
                return f"Según lo que me enseñaste, tu nombre es {recuerdo.split(':')[-1].strip()}"
        if re.search(r'donde vivo|en que ciudad', entrada.lower()):
            if 'ciudad' in recuerdo.lower() or 'vivo en' in recuerdo.lower():
                return f"Recuerdo que me dijiste que vives en {recuerdo.split(':')[-1].strip()}"
        if re.search(r'cumpleaños|cuando naci', entrada.lower()):
            if 'cumpleaños' in recuerdo.lower() or 'nací' in recuerdo.lower():
                return f"Me enseñaste que tu cumpleaños es {recuerdo.split(':')[-1].strip()}"
        # Parafraseo genérico
        return f"Recuerdo que me contaste: {recuerdo}"

    def _preguntar_aprendizaje(self, entrada):
        # Si no sabe la respuesta, pide al usuario que le enseñe
        return f"No tengo esa información aún. ¿Me lo puedes enseñar?" 