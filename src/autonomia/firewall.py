from typing import List, Dict, Optional
import psutil
import logging
import subprocess
import platform
import requests
import geoip2.database
from pathlib import Path

class FirewallSassy:
    def __init__(self):
        self.reglas = []  # Lista de reglas de firewall
        self.conexiones_bloqueadas = set()
        self.alertas = []
        self.lista_negra_ips = set()
        self.geoip_reader = self._cargar_geoip()
        self.sistema = platform.system().lower()

    def _cargar_geoip(self):
        # Descarga o usa una base de datos GeoLite2 local (debes descargarla y poner la ruta correcta)
        ruta = Path('data/GeoLite2-City.mmdb')
        if ruta.exists():
            return geoip2.database.Reader(str(ruta))
        return None

    def actualizar_lista_negra(self, url: str = "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"):
        """Descarga una lista negra pública de IPs"""
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line and not line.startswith("#"):
                        self.lista_negra_ips.add(line.strip())
        except Exception as e:
            logging.error(f"Error al actualizar lista negra: {e}")

    def monitorear_conexiones(self) -> List[Dict]:
        """Monitorea las conexiones de red activas y detecta actividad sospechosa"""
        conexiones = []
        for conn in psutil.net_connections():
            info = {
                "pid": conn.pid,
                "laddr": str(conn.laddr) if conn.laddr else None,
                "raddr": str(conn.raddr) if conn.raddr else None,
                "status": conn.status,
                "type": conn.type,
                "sospechosa": False,
                "pais": None
            }
            # Detección de IP sospechosa
            if conn.raddr:
                ip = conn.raddr.ip if hasattr(conn.raddr, 'ip') else str(conn.raddr[0])
                if ip in self.lista_negra_ips:
                    info["sospechosa"] = True
                    self.alertas.append(f"Conexión sospechosa detectada: {ip}")
                # GeoIP
                if self.geoip_reader:
                    try:
                        geo = self.geoip_reader.city(ip)
                        info["pais"] = geo.country.name
                        # Ejemplo: marcar conexiones a países de riesgo
                        if geo.country.iso_code in ["RU", "CN", "KP", "IR"]:
                            info["sospechosa"] = True
                            self.alertas.append(f"Conexión a país de riesgo: {ip} ({geo.country.name})")
                    except Exception:
                        pass
            conexiones.append(info)
        return conexiones

    def agregar_regla(self, regla: Dict):
        """Agrega una nueva regla de firewall"""
        self.reglas.append(regla)
        # Aplicar la regla en el sistema operativo
        self._aplicar_regla_sistema(regla)

    def bloquear_conexion(self, ip: str, puerto: Optional[int] = None):
        """Bloquea una IP (y opcionalmente un puerto) usando el firewall del sistema"""
        self.conexiones_bloqueadas.add((ip, puerto))
        if self.sistema == "windows":
            cmd = ["netsh", "advfirewall", "firewall", "add", "rule", "name=SassyBlock", "dir=in", "action=block", f"remoteip={ip}"]
            if puerto:
                cmd += [f"localport={puerto}", "protocol=TCP"]
            try:
                subprocess.run(cmd, check=True)
                logging.info(f"Conexión bloqueada en Windows: IP={ip}, puerto={puerto}")
            except Exception as e:
                logging.error(f"Error al bloquear conexión en Windows: {e}")
        elif self.sistema == "linux":
            # Preparado para Linux (iptables)
            cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
            if puerto:
                cmd += ["--dport", str(puerto)]
            try:
                subprocess.run(cmd, check=True)
                logging.info(f"Conexión bloqueada en Linux: IP={ip}, puerto={puerto}")
            except Exception as e:
                logging.error(f"Error al bloquear conexión en Linux: {e}")
        else:
            logging.warning("Sistema operativo no soportado para bloqueo real de conexiones.")

    def _aplicar_regla_sistema(self, regla: Dict):
        """Aplica una regla personalizada en el firewall del sistema"""
        # Ejemplo: bloquear una IP
        if regla.get("accion") == "bloquear_ip" and "ip" in regla:
            self.bloquear_conexion(regla["ip"], regla.get("puerto"))

    def mostrar_reglas(self) -> List[Dict]:
        """Devuelve la lista de reglas actuales"""
        return self.reglas

    def mostrar_alertas(self) -> List[str]:
        """Devuelve las alertas de seguridad recientes"""
        return self.alertas 