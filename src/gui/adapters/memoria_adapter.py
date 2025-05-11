from src.memoria.memoria import MemoriaContextual

class MemoriaAdapter:
    def __init__(self):
        self.memoria = MemoriaContextual()

    def obtener_recuerdos(self):
        """Devuelve todos los recuerdos almacenados."""
        if hasattr(self.memoria, 'obtener_recuerdos'):
            return self.memoria.obtener_recuerdos()
        return []

    def agregar_recuerdo(self, texto, contexto=None):
        """Agrega un nuevo recuerdo con texto y contexto opcional."""
        if hasattr(self.memoria, 'agregar_recuerdo'):
            return self.memoria.agregar_recuerdo(texto, contexto)
        return None

    def buscar_recuerdos(self, palabra_clave):
        """Busca recuerdos que contengan la palabra clave."""
        if hasattr(self.memoria, 'buscar_recuerdos'):
            return self.memoria.buscar_recuerdos(palabra_clave)
        # Búsqueda básica si no existe el método
        recuerdos = self.obtener_recuerdos()
        return [r for r in recuerdos if palabra_clave.lower() in str(r).lower()]

    def obtener_logs(self):
        """Devuelve los logs de la memoria/contexto o un log simulado si no existe."""
        if hasattr(self.memoria, 'obtener_logs'):
            return self.memoria.obtener_logs()
        return ["[Memoria] Sin logs disponibles (simulado)"] 