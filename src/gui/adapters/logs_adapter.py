from .antivirus_adapter import AntivirusAdapter
from .firewall_adapter import FirewallAdapter
from .proactividad_adapter import ProactividadAdapter
from .aprendizaje_adapter import AprendizajeAdapter
from .memoria_adapter import MemoriaAdapter

class LogsAdapter:
    def __init__(self):
        self.antivirus = AntivirusAdapter()
        self.firewall = FirewallAdapter()
        self.proactivo = ProactividadAdapter()
        self.aprendizaje = AprendizajeAdapter()
        self.memoria = MemoriaAdapter()

    def obtener_todos_los_logs(self):
        """Devuelve todos los logs de todos los sistemas en una lista unificada."""
        logs = []
        logs += self.antivirus.obtener_logs()
        logs += self.firewall.obtener_logs()
        logs += self.proactivo.obtener_logs()
        logs += self.aprendizaje.obtener_logs()
        logs += self.memoria.obtener_logs()
        return logs

    def obtener_logs_por_sistema(self, sistema):
        """Devuelve los logs de un sistema específico ('antivirus', 'firewall', etc)."""
        if sistema == 'antivirus':
            return self.antivirus.obtener_logs()
        elif sistema == 'firewall':
            return self.firewall.obtener_logs()
        elif sistema == 'proactivo':
            return self.proactivo.obtener_logs()
        elif sistema == 'aprendizaje':
            return self.aprendizaje.obtener_logs()
        elif sistema == 'memoria':
            return self.memoria.obtener_logs()
        return [] 