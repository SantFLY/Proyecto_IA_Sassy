from src.autonomia.proactividad import SistemaProactivo

class ProactividadAdapter:
    def __init__(self):
        self.proactivo = SistemaProactivo()
        self.activo = True

    def estado(self):
        """Devuelve True si el sistema proactivo está activo, False si no."""
        return self.activo

    def activar(self):
        """Activa el sistema proactivo."""
        self.activo = True

    def desactivar(self):
        """Desactiva el sistema proactivo."""
        self.activo = False

    def ejecutar_accion(self, accion):
        """Ejecuta una acción proactiva específica."""
        if hasattr(self.proactivo, 'ejecutar_acciones_proactivas'):
            return self.proactivo.ejecutar_acciones_proactivas()
        return {"resultado": f"Acción '{accion}' ejecutada (simulado)"}

    def obtener_sugerencias(self):
        """Devuelve sugerencias proactivas actuales."""
        if hasattr(self.proactivo, 'sugerir_acciones'):
            return self.proactivo.sugerir_acciones([])
        return []

    def obtener_logs(self):
        """Devuelve los logs del sistema proactivo."""
        return ["[Proactividad] Sin logs disponibles (simulado)"] 