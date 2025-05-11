from src.autonomia.firewall import FirewallSassy

class FirewallAdapter:
    def __init__(self):
        self.firewall = FirewallSassy()
        self.activo = True

    def estado(self):
        """Devuelve True si el firewall está activo, False si no."""
        return self.activo

    def activar(self):
        """Activa el firewall."""
        self.activo = True

    def desactivar(self):
        """Desactiva el firewall."""
        self.activo = False

    def bloquear_ip(self, ip):
        """Bloquea una IP específica."""
        return self.firewall.bloquear_conexion(ip)

    def desbloquear_ip(self, ip):
        """Desbloquea una IP específica."""
        if hasattr(self.firewall, 'conexiones_bloqueadas'):
            self.firewall.conexiones_bloqueadas = {c for c in self.firewall.conexiones_bloqueadas if c[0] != ip}
        return True

    def obtener_reglas(self):
        """Devuelve las reglas activas del firewall."""
        if hasattr(self.firewall, 'mostrar_reglas'):
            return self.firewall.mostrar_reglas()
        return []

    def obtener_logs(self):
        """Devuelve los logs del firewall."""
        if hasattr(self.firewall, 'mostrar_alertas'):
            return [f"[Firewall] {a}" for a in self.firewall.mostrar_alertas()]
        return [] 