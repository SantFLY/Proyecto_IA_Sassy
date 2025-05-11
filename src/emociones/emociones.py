"""
Sistema de emociones evolutivo para Sassy.
Gestiona el estado emocional y su evolución basado en interacciones y contexto.
"""

from typing import Dict, List, Optional
import random
import time
from datetime import datetime
import json
import os

class EstadoEmocional:
    def __init__(self, nombre: str, intensidad: float = 0.5, emoji: str = "😐"):
        self.nombre = nombre
        self.intensidad = intensidad
        self.emoji = emoji
        self.timestamp = time.time()
        self.duracion = 0  # Duración en segundos
        self.transiciones = []  # Historial de transiciones

    def actualizar(self, nueva_intensidad: float):
        self.intensidad = max(0.0, min(1.0, nueva_intensidad))
        self.timestamp = time.time()

    def transicionar(self, nuevo_estado: str, intensidad: float):
        self.transiciones.append({
            'de': self.nombre,
            'a': nuevo_estado,
            'intensidad': intensidad,
            'timestamp': time.time()
        })

class GestorEmociones:
    def __init__(self):
        self.estado_actual = EstadoEmocional("neutral")
        self.historial_emocional = []
        self.patrones_emocionales = {}
        self.ultima_actualizacion = time.time()
        self.cargar_estado()

    def cargar_estado(self):
        """Carga el estado emocional desde archivo si existe."""
        try:
            if os.path.exists('data/estado_emocional.json'):
                with open('data/estado_emocional.json', 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.estado_actual = EstadoEmocional(
                        datos['nombre'],
                        datos['intensidad'],
                        datos['emoji']
                    )
                    self.historial_emocional = datos.get('historial', [])
                    self.patrones_emocionales = datos.get('patrones', {})
        except Exception as e:
            print(f"Error al cargar estado emocional: {e}")

    def guardar_estado(self):
        """Guarda el estado emocional actual."""
        try:
            os.makedirs('data', exist_ok=True)
            datos = {
                'nombre': self.estado_actual.nombre,
                'intensidad': self.estado_actual.intensidad,
                'emoji': self.estado_actual.emoji,
                'historial': self.historial_emocional,
                'patrones': self.patrones_emocionales
            }
            with open('data/estado_emocional.json', 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar estado emocional: {e}")

    def analizar_entrada(self, texto: str, contexto: Dict = None) -> Dict:
        """
        Analiza la entrada para determinar el impacto emocional.
        Aquí se puede integrar con APIs de análisis de sentimiento.
        """
        # TODO: Integrar con API de análisis de sentimiento
        impacto = {
            'tipo': 'neutral',
            'intensidad': 0.5,
            'confianza': 0.7
        }
        return impacto

    def actualizar_emocion(self, entrada: str, contexto: Dict = None):
        """
        Actualiza el estado emocional basado en la entrada y el contexto.
        """
        impacto = self.analizar_entrada(entrada, contexto)
        
        # Calcular nueva intensidad
        nueva_intensidad = (self.estado_actual.intensidad + impacto['intensidad']) / 2
        
        # Transición suave entre estados
        if impacto['confianza'] > 0.6:
            self.estado_actual.transicionar(impacto['tipo'], nueva_intensidad)
            self.estado_actual = EstadoEmocional(impacto['tipo'], nueva_intensidad)
        
        # Actualizar historial
        self.historial_emocional.append({
            'estado': self.estado_actual.nombre,
            'intensidad': self.estado_actual.intensidad,
            'timestamp': time.time(),
            'entrada': entrada
        })
        
        # Limitar tamaño del historial
        if len(self.historial_emocional) > 1000:
            self.historial_emocional = self.historial_emocional[-1000:]
        
        self.guardar_estado()

    def obtener_emocion(self) -> Dict:
        """
        Retorna el estado emocional actual con su representación.
        """
        return {
            'nombre': self.estado_actual.nombre,
            'intensidad': self.estado_actual.intensidad,
            'emoji': self.estado_actual.emoji,
            'timestamp': self.estado_actual.timestamp
        }

    def obtener_historial_reciente(self, limite: int = 10) -> List[Dict]:
        """
        Retorna el historial emocional reciente.
        """
        return self.historial_emocional[-limite:]

    def analizar_patrones(self):
        """
        Analiza patrones en el historial emocional para aprendizaje.
        """
        # Implementación mínima: retorna un resumen de emociones
        resumen = {}
        for estado in self.historial_emocional:
            nombre = estado['nombre'] if isinstance(estado, dict) and 'nombre' in estado else str(estado)
            resumen[nombre] = resumen.get(nombre, 0) + 1
        return resumen

    def reset(self):
        """
        Reinicia el estado emocional a neutral.
        """
        self.estado_actual = EstadoEmocional("neutral")
        self.guardar_estado()

# Métodos para cambiar, detectar y expresar emociones 