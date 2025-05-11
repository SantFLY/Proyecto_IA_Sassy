from src.autonomia.aprendizaje import SistemaAprendizaje

class AprendizajeAdapter:
    def __init__(self):
        self.aprendizaje = SistemaAprendizaje()
        self.activo = True

    def estado(self):
        """Devuelve True si el sistema de aprendizaje está activo, False si no."""
        return self.activo

    def activar(self):
        """Activa el sistema de aprendizaje."""
        self.activo = True

    def desactivar(self):
        """Desactiva el sistema de aprendizaje."""
        self.activo = False

    def iniciar_ciclo(self):
        """Inicia un ciclo de aprendizaje manualmente."""
        if hasattr(self.aprendizaje, 'ejecutar_aprendizaje_continuo'):
            return self.aprendizaje.ejecutar_aprendizaje_continuo()
        return None

    def obtener_sugerencias(self, tipo='general'):
        """Devuelve sugerencias de optimización actuales."""
        if hasattr(self.aprendizaje, 'sugerir_mejoras'):
            return self.aprendizaje.sugerir_mejoras(tipo)
        return []

    def obtener_logs(self):
        """Devuelve los logs del sistema de aprendizaje."""
        return ["[Aprendizaje] Sin logs disponibles (simulado)"] 