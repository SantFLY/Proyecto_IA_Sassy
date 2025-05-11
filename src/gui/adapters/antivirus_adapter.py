from src.proteccion.antivirus import AntivirusSassy

class AntivirusAdapter:
    def __init__(self):
        self.antivirus = AntivirusSassy()

    def estado(self):
        """Devuelve True si el antivirus está activo, False si no."""
        return self.antivirus.activo if hasattr(self.antivirus, 'activo') else True

    def activar(self):
        """Activa el antivirus."""
        if hasattr(self.antivirus, 'activar'):
            self.antivirus.activar()
        else:
            self.antivirus.activo = True

    def desactivar(self):
        """Desactiva el antivirus."""
        if hasattr(self.antivirus, 'desactivar'):
            self.antivirus.desactivar()
        else:
            self.antivirus.activo = False

    def escanear(self):
        """Inicia un escaneo completo del sistema."""
        return self.antivirus.ejecutar_escaneo()

    def poner_en_cuarentena(self, archivo):
        """Pone un archivo en cuarentena."""
        return self.antivirus.poner_en_cuarentena(archivo)

    def limpiar_alertas(self):
        """Limpia las alertas actuales."""
        if hasattr(self.antivirus, 'limpiar_alertas'):
            self.antivirus.limpiar_alertas()

    def obtener_alertas(self):
        """Devuelve una lista de alertas actuales."""
        if hasattr(self.antivirus, 'obtener_alertas'):
            return self.antivirus.obtener_alertas()
        elif hasattr(self.antivirus, 'mostrar_alertas'):
            return self.antivirus.mostrar_alertas()
        return []

    def obtener_logs(self):
        """Devuelve los logs del antivirus o un log simulado si no existe."""
        if hasattr(self.antivirus, 'obtener_logs'):
            return self.antivirus.obtener_logs()
        # Log simulado
        return [f"[Antivirus] {a['mensaje'] if isinstance(a, dict) and 'mensaje' in a else a}" for a in self.obtener_alertas()] 