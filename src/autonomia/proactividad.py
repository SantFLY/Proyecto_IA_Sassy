from typing import Dict, List, Optional, Tuple
import psutil
import time
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
import numpy as np
from collections import deque
from .firewall import FirewallSassy

class SistemaProactivo:
    def __init__(self):
        self.umbrales = {
            "cpu": 80,  # Porcentaje
            "memoria": 85,  # Porcentaje
            "disco": 90,  # Porcentaje
            "red": 1000000,  # Bytes por segundo
            "temperatura": 80,  # Grados Celsius
            "bateria": 20  # Porcentaje
        }
        self.alertas_activas = set()
        self.historial_alertas = self._cargar_historial()
        self.historial_metricas = {
            "cpu": deque(maxlen=60),  # 1 minuto de historial
            "memoria": deque(maxlen=60),
            "disco": deque(maxlen=60),
            "red": deque(maxlen=60),
            "temperatura": deque(maxlen=60),
            "bateria": deque(maxlen=60)
        }
        self.tendencias = {}
        self._calcular_tendencias()
        # Inicializar firewall avanzado
        self.firewall = FirewallSassy()
        self.firewall.actualizar_lista_negra()
        
    def _cargar_historial(self) -> Dict:
        """Carga el historial de alertas"""
        try:
            with open(Path("data/historial_alertas.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _guardar_historial(self):
        """Guarda el historial de alertas"""
        try:
            with open(Path("data/historial_alertas.json"), "w", encoding="utf-8") as f:
                json.dump(self.historial_alertas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error al guardar historial de alertas: {e}")
            
    def _obtener_temperatura(self) -> Optional[float]:
        """Obtiene la temperatura del sistema si está disponible"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Tomar la temperatura más alta
                return max(temp.current for temp in temps.get('coretemp', []))
        except:
            pass
        return None
        
    def _obtener_bateria(self) -> Optional[float]:
        """Obtiene el nivel de batería si está disponible"""
        try:
            bateria = psutil.sensors_battery()
            if bateria:
                return bateria.percent
        except:
            pass
        return None
        
    def _calcular_tendencias(self):
        """Calcula las tendencias de las métricas"""
        for metrica, valores in self.historial_metricas.items():
            if len(valores) > 1:
                x = np.arange(len(valores))
                y = np.array(valores)
                z = np.polyfit(x, y, 1)
                self.tendencias[metrica] = {
                    "pendiente": z[0],
                    "prediccion_5min": z[0] * 5 + z[1] if len(valores) > 5 else None
                }
                
    def monitorear_sistema(self) -> List[Dict]:
        """Monitorea el sistema y retorna alertas si es necesario (incluye seguridad)"""
        alertas = []
        
        # Monitoreo de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.historial_metricas["cpu"].append(cpu_percent)
        if cpu_percent > self.umbrales["cpu"]:
            alertas.append({
                "tipo": "cpu",
                "mensaje": f"Uso de CPU alto: {cpu_percent}%",
                "valor": cpu_percent,
                "umbral": self.umbrales["cpu"],
                "tendencia": self.tendencias.get("cpu", {}).get("prediccion_5min")
            })
            
        # Monitoreo de memoria
        memoria = psutil.virtual_memory()
        self.historial_metricas["memoria"].append(memoria.percent)
        if memoria.percent > self.umbrales["memoria"]:
            alertas.append({
                "tipo": "memoria",
                "mensaje": f"Uso de memoria alto: {memoria.percent}%",
                "valor": memoria.percent,
                "umbral": self.umbrales["memoria"],
                "tendencia": self.tendencias.get("memoria", {}).get("prediccion_5min")
            })
            
        # Monitoreo de disco
        disco = psutil.disk_usage('/')
        self.historial_metricas["disco"].append(disco.percent)
        if disco.percent > self.umbrales["disco"]:
            alertas.append({
                "tipo": "disco",
                "mensaje": f"Espacio en disco bajo: {disco.percent}%",
                "valor": disco.percent,
                "umbral": self.umbrales["disco"],
                "tendencia": self.tendencias.get("disco", {}).get("prediccion_5min")
            })
            
        # Monitoreo de red
        red_antes = psutil.net_io_counters()
        time.sleep(1)
        red_despues = psutil.net_io_counters()
        bytes_por_segundo = (red_despues.bytes_sent + red_despues.bytes_recv - 
                           red_antes.bytes_sent - red_antes.bytes_recv)
        self.historial_metricas["red"].append(bytes_por_segundo)
        
        if bytes_por_segundo > self.umbrales["red"]:
            alertas.append({
                "tipo": "red",
                "mensaje": f"Actividad de red alta: {bytes_por_segundo/1000000:.2f} MB/s",
                "valor": bytes_por_segundo,
                "umbral": self.umbrales["red"],
                "tendencia": self.tendencias.get("red", {}).get("prediccion_5min")
            })
            
        # Monitoreo de temperatura
        temp = self._obtener_temperatura()
        if temp is not None:
            self.historial_metricas["temperatura"].append(temp)
            if temp > self.umbrales["temperatura"]:
                alertas.append({
                    "tipo": "temperatura",
                    "mensaje": f"Temperatura alta: {temp}°C",
                    "valor": temp,
                    "umbral": self.umbrales["temperatura"],
                    "tendencia": self.tendencias.get("temperatura", {}).get("prediccion_5min")
                })
                
        # Monitoreo de batería
        bateria = self._obtener_bateria()
        if bateria is not None:
            self.historial_metricas["bateria"].append(bateria)
            if bateria < self.umbrales["bateria"]:
                alertas.append({
                    "tipo": "bateria",
                    "mensaje": f"Batería baja: {bateria}%",
                    "valor": bateria,
                    "umbral": self.umbrales["bateria"],
                    "tendencia": self.tendencias.get("bateria", {}).get("prediccion_5min")
                })
                
        # Actualizar tendencias
        self._calcular_tendencias()
        
        # Monitoreo de seguridad (firewall)
        conexiones = self.firewall.monitorear_conexiones()
        for conn in conexiones:
            if conn.get("sospechosa"):
                alerta = {
                    "tipo": "seguridad",
                    "mensaje": f"Conexión sospechosa detectada: {conn.get('raddr')} (País: {conn.get('pais')})",
                    "valor": conn.get("raddr"),
                    "umbral": None,
                    "tendencia": None
                }
                alertas.append(alerta)
        
        # Añadir alertas del firewall
        for alerta_fw in self.firewall.mostrar_alertas():
            alertas.append({
                "tipo": "seguridad",
                "mensaje": alerta_fw,
                "valor": None,
                "umbral": None,
                "tendencia": None
            })
        
        # Registrar alertas en el historial
        for alerta in alertas:
            self._registrar_alerta(alerta)
            
        return alertas
        
    def _registrar_alerta(self, alerta: Dict):
        """Registra una alerta en el historial"""
        timestamp = datetime.now().isoformat()
        if alerta["tipo"] not in self.historial_alertas:
            self.historial_alertas[alerta["tipo"]] = []
            
        self.historial_alertas[alerta["tipo"]].append({
            **alerta,
            "timestamp": timestamp
        })
        self._guardar_historial()
        
    def sugerir_acciones(self, alertas: List[Dict]) -> List[str]:
        """Sugiere acciones basadas en las alertas activas, incluyendo seguridad"""
        sugerencias = []
        
        for alerta in alertas:
            tipo = alerta["tipo"]
            valor = alerta["valor"]
            tendencia = alerta.get("tendencia")
            
            if tipo == "cpu":
                if tendencia and tendencia > valor:
                    sugerencias.append("⚠️ El uso de CPU está aumentando. ¿Quieres que analice qué procesos están consumiendo más CPU?")
                else:
                    sugerencias.append("¿Quieres que analice qué procesos están consumiendo más CPU?")
                    
            elif tipo == "memoria":
                if tendencia and tendencia > valor:
                    sugerencias.append("⚠️ El uso de memoria está aumentando. ¿Quieres que busque aplicaciones que consuman mucha memoria?")
                else:
                    sugerencias.append("¿Quieres que busque aplicaciones que consuman mucha memoria?")
                    
            elif tipo == "disco":
                if tendencia and tendencia > valor:
                    sugerencias.append("⚠️ El espacio en disco está disminuyendo rápidamente. ¿Quieres que busque archivos grandes para liberar espacio?")
                else:
                    sugerencias.append("¿Quieres que busque archivos grandes para liberar espacio?")
                    
            elif tipo == "red":
                if tendencia and tendencia > valor:
                    sugerencias.append("⚠️ La actividad de red está aumentando. ¿Quieres que analice qué aplicaciones están usando más ancho de banda?")
                else:
                    sugerencias.append("¿Quieres que analice qué aplicaciones están usando más ancho de banda?")
                    
            elif tipo == "temperatura":
                if tendencia and tendencia > valor:
                    sugerencias.append("⚠️ La temperatura está aumentando. ¿Quieres que busque procesos que estén generando calor?")
                else:
                    sugerencias.append("¿Quieres que busque procesos que estén generando calor?")
                    
            elif tipo == "bateria":
                if tendencia and tendencia < valor:
                    sugerencias.append("⚠️ La batería se está agotando rápidamente. ¿Quieres que busque aplicaciones que consuman mucha batería?")
                else:
                    sugerencias.append("¿Quieres que busque aplicaciones que consuman mucha batería?")
                    
            elif tipo == "seguridad":
                sugerencias.append(f"⚠️ Alerta de seguridad: {alerta['mensaje']} ¿Deseas bloquear la IP o investigar el proceso?")
                
        return sugerencias
        
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        return {
            "cpu": {
                "actual": psutil.cpu_percent(interval=1),
                "tendencia": self.tendencias.get("cpu", {}).get("pendiente")
            },
            "memoria": {
                "actual": psutil.virtual_memory().percent,
                "tendencia": self.tendencias.get("memoria", {}).get("pendiente")
            },
            "disco": {
                "actual": psutil.disk_usage('/').percent,
                "tendencia": self.tendencias.get("disco", {}).get("pendiente")
            },
            "red": {
                "bytes_enviados": psutil.net_io_counters().bytes_sent,
                "bytes_recibidos": psutil.net_io_counters().bytes_recv,
                "tendencia": self.tendencias.get("red", {}).get("pendiente")
            },
            "temperatura": {
                "actual": self._obtener_temperatura(),
                "tendencia": self.tendencias.get("temperatura", {}).get("pendiente")
            },
            "bateria": {
                "actual": self._obtener_bateria(),
                "tendencia": self.tendencias.get("bateria", {}).get("pendiente")
            }
        }
        
    def predecir_problemas(self) -> List[Dict]:
        """Predice posibles problemas basados en las tendencias"""
        predicciones = []
        
        for metrica, tendencia in self.tendencias.items():
            if tendencia["pendiente"] > 0:  # Tendencia creciente
                valor_actual = self.historial_metricas[metrica][-1]
                prediccion = tendencia["prediccion_5min"]
                
                if prediccion and prediccion > self.umbrales[metrica]:
                    predicciones.append({
                        "tipo": metrica,
                        "mensaje": f"Se predice que {metrica} alcanzará {prediccion:.1f} en 5 minutos",
                        "valor_actual": valor_actual,
                        "valor_predicho": prediccion,
                        "umbral": self.umbrales[metrica]
                    })
                    
        return predicciones

    def ejecutar_acciones_proactivas(self):
        """Monitorea el sistema y toma acciones automáticas si detecta alertas críticas."""
        alertas = self.monitorear_sistema()
        for alerta in alertas:
            if alerta['tipo'] == 'seguridad':
                # Bloquear IP sospechosa automáticamente si es posible
                ip = alerta.get('valor')
                if ip:
                    # Extraer solo la IP si viene en formato addr(ip='...', port=...)
                    if isinstance(ip, str) and "ip='" in ip:
                        import re
                        match = re.search(r"ip='([0-9.]+)'", ip)
                        if match:
                            ip = match.group(1)
                    elif hasattr(ip, 'ip'):
                        ip = ip.ip
                    self.firewall.bloquear_conexion(ip)
                    logging.warning(f"[PROACTIVO] IP bloqueada automáticamente: {ip}")
            elif alerta['tipo'] == 'cpu':
                procesos = [(p.pid, p.name(), p.cpu_percent()) for p in psutil.process_iter(['pid', 'name'])]
                procesos.sort(key=lambda x: x[2], reverse=True)
                if procesos and procesos[0][2] > self.umbrales['cpu']:
                    pid = procesos[0][0]
                    try:
                        psutil.Process(pid).terminate()
                        logging.warning(f"[PROACTIVO] Proceso de alto consumo terminado automáticamente: {procesos[0][1]} (PID: {pid})")
                    except Exception as e:
                        logging.error(f"[PROACTIVO] Error al terminar proceso: {e}")
            elif alerta['tipo'] == 'memoria':
                logging.warning("[PROACTIVO] Uso de memoria alto. Sugerencia: Cierra aplicaciones no utilizadas para liberar memoria.")
            elif alerta['tipo'] == 'disco':
                logging.warning("[PROACTIVO] Espacio en disco bajo. Sugerencia: Elimina archivos grandes o innecesarios.")
            elif alerta['tipo'] == 'red':
                logging.warning("[PROACTIVO] Actividad de red alta. Sugerencia: Revisa aplicaciones que consumen mucho ancho de banda.")
            elif alerta['tipo'] == 'temperatura':
                logging.warning("[PROACTIVO] Temperatura alta. Sugerencia: Cierra aplicaciones exigentes o mejora la ventilación.")
            elif alerta['tipo'] == 'bateria':
                logging.warning("[PROACTIVO] Batería baja. Sugerencia: Activa el modo de ahorro de energía.")

    def _registrar_alerta(self, alerta: Dict):
        """Registra una alerta en el historial"""
        timestamp = datetime.now().isoformat()
        if alerta["tipo"] not in self.historial_alertas:
            self.historial_alertas[alerta["tipo"]] = []
            
        self.historial_alertas[alerta["tipo"]].append({
            **alerta,
            "timestamp": timestamp
        })
        self._guardar_historial() 