from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path
import logging
from datetime import datetime

class AnalizadorIntencion:
    def __init__(self, modelo_local):
        self.modelo = modelo_local
        self.acciones_conocidas = self._cargar_acciones_conocidas()
        self.historial_analisis = []
        self.umbral_confianza = 0.7
        
    def _cargar_acciones_conocidas(self) -> Dict:
        """Carga las acciones conocidas desde un archivo JSON"""
        try:
            with open(Path("data/acciones_conocidas.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def analizar_mensaje(self, mensaje: str) -> Tuple[str, Dict]:
        """
        Analiza el mensaje del usuario y determina la intención y los parámetros.
        Retorna: (tipo_accion, parametros)
        """
        # Obtener contexto del historial
        contexto = self._obtener_contexto()
        
        prompt = f"""Analiza el siguiente mensaje y determina la intención del usuario.\n\nMensaje del usuario: {mensaje}\n"""
        try:
            respuesta = self.modelo.generar_respuesta(prompt)
            # No intentar decodificar como JSON, solo texto plano
            # Si quieres extraer una intención, puedes hacer un parseo simple aquí
            # Por ahora, siempre devolvemos 'desconocido' y el mensaje original
            return "desconocido", {"mensaje": mensaje, "respuesta_modelo": respuesta}
        except Exception as e:
            logging.error(f"Error en análisis de mensaje: {e}")
            return "desconocido", {"mensaje": mensaje, "error": str(e)}
            
    def _validar_resultado(self, resultado: Dict) -> bool:
        """Valida que el resultado del análisis sea correcto"""
        campos_requeridos = ["tipo_accion", "parametros", "confianza", "requiere_confirmacion"]
        return all(campo in resultado for campo in campos_requeridos)
        
    def _obtener_contexto(self) -> str:
        """Obtiene el contexto de la conversación reciente"""
        if not self.historial_analisis:
            return "No hay contexto previo"
            
        # Tomar los últimos 3 análisis
        contexto = []
        for analisis in self.historial_analisis[-3:]:
            contexto.append(f"Mensaje: {analisis['mensaje']}")
            contexto.append(f"Acción: {analisis['tipo_accion']}")
            contexto.append(f"Razón: {analisis.get('razon', 'No especificada')}")
            
        return "\n".join(contexto)
        
    def _guardar_analisis(self, mensaje: str, resultado: Dict):
        """Guarda el análisis en el historial"""
        self.historial_analisis.append({
            "timestamp": datetime.now().isoformat(),
            "mensaje": mensaje,
            **resultado
        })
        
        # Mantener solo los últimos 10 análisis
        if len(self.historial_analisis) > 10:
            self.historial_analisis = self.historial_analisis[-10:]
            
    def es_accion_conocida(self, tipo_accion: str) -> bool:
        """Verifica si el tipo de acción es conocido"""
        return tipo_accion in self.acciones_conocidas
        
    def obtener_detalles_accion(self, tipo_accion: str) -> Optional[Dict]:
        """Obtiene los detalles de una acción conocida"""
        return self.acciones_conocidas.get(tipo_accion)
        
    def sugerir_acciones_similares(self, tipo_accion: str) -> List[str]:
        """Sugiere acciones similares a la solicitada"""
        if tipo_accion in self.acciones_conocidas:
            return []
            
        # Buscar acciones que contengan palabras similares
        sugerencias = []
        palabras = tipo_accion.lower().split("_")
        
        for accion in self.acciones_conocidas:
            if any(palabra in accion.lower() for palabra in palabras):
                sugerencias.append(accion)
                
        return sugerencias[:3]  # Retornar máximo 3 sugerencias 