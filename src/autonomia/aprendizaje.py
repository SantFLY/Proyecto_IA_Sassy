from typing import Dict, Any, List, Optional, Tuple
import json
from pathlib import Path
import logging
from datetime import datetime
import difflib
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SistemaAprendizaje:
    def __init__(self):
        self.ruta_base = Path("data/aprendizaje")
        self.ruta_base.mkdir(parents=True, exist_ok=True)
        self.experiencias = self._cargar_experiencias()
        self.vectorizer = TfidfVectorizer()
        self._entrenar_vectorizer()
        
    def _cargar_experiencias(self) -> Dict:
        """Carga las experiencias guardadas"""
        try:
            with open(self.ruta_base / "experiencias.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def guardar_experiencia(self, tipo: str, entrada: str, accion: str, resultado: Any, exito: bool):
        """Guarda una nueva experiencia de aprendizaje"""
        timestamp = datetime.now().isoformat()
        experiencia = {
            "tipo": tipo,
            "entrada": entrada,
            "accion": accion,
            "resultado": str(resultado),
            "exito": exito,
            "timestamp": timestamp,
            "patrones": self._extraer_patrones(entrada)
        }
        
        if tipo not in self.experiencias:
            self.experiencias[tipo] = []
            
        self.experiencias[tipo].append(experiencia)
        self._guardar_experiencias()
        self._entrenar_vectorizer()  # Reentrenar con la nueva experiencia
        
    def _extraer_patrones(self, texto: str) -> Dict[str, Any]:
        """Extrae patrones del texto de entrada"""
        palabras = texto.lower().split()
        return {
            "longitud": len(texto),
            "num_palabras": len(palabras),
            "palabras_clave": [p for p in palabras if len(p) > 3],
            "tiene_numeros": any(c.isdigit() for c in texto),
            "tiene_simbolos": any(not c.isalnum() for c in texto)
        }
        
    def _entrenar_vectorizer(self):
        """Entrena el vectorizador con todas las experiencias"""
        textos = []
        for tipo in self.experiencias:
            for exp in self.experiencias[tipo]:
                textos.append(exp["entrada"])
                
        if textos:
            self.vectorizer.fit(textos)
            
    def _guardar_experiencias(self):
        """Guarda todas las experiencias en el archivo"""
        try:
            with open(self.ruta_base / "experiencias.json", "w", encoding="utf-8") as f:
                json.dump(self.experiencias, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error al guardar experiencias: {e}")
            
    def buscar_experiencias_similares(self, tipo: str, entrada: str, umbral_similitud: float = 0.7) -> List[Dict]:
        """Busca experiencias similares a la entrada actual"""
        if tipo not in self.experiencias or not self.experiencias[tipo]:
            return []
            
        # Vectorizar la entrada actual
        try:
            entrada_vector = self.vectorizer.transform([entrada])
            experiencias_vectores = self.vectorizer.transform([exp["entrada"] for exp in self.experiencias[tipo]])
            
            # Calcular similitud
            similitudes = cosine_similarity(entrada_vector, experiencias_vectores)[0]
            
            # Filtrar por umbral y ordenar
            experiencias_similares = []
            for i, similitud in enumerate(similitudes):
                if similitud >= umbral_similitud:
                    exp = self.experiencias[tipo][i].copy()
                    exp["similitud"] = float(similitud)
                    experiencias_similares.append(exp)
                    
            return sorted(experiencias_similares, key=lambda x: x["similitud"], reverse=True)[:5]
            
        except Exception as e:
            logging.error(f"Error al buscar experiencias similares: {e}")
            return []
            
    def analizar_patrones(self, tipo: str) -> Dict[str, Any]:
        """Analiza patrones en las experiencias de un tipo específico"""
        if tipo not in self.experiencias or not self.experiencias[tipo]:
            return {}
            
        experiencias = self.experiencias[tipo]
        
        # Análisis básico
        exito_total = sum(1 for exp in experiencias if exp["exito"])
        total = len(experiencias)
        
        # Análisis de patrones
        patrones = defaultdict(list)
        for exp in experiencias:
            for key, value in exp.get("patrones", {}).items():
                patrones[key].append(value)
                
        # Calcular estadísticas
        estadisticas = {
            "total_experiencias": total,
            "tasa_exito": exito_total / total if total > 0 else 0,
            "ultima_experiencia": experiencias[-1] if experiencias else None,
            "patrones": {
                key: {
                    "promedio": np.mean(values) if isinstance(values[0], (int, float)) else None,
                    "min": min(values) if isinstance(values[0], (int, float)) else None,
                    "max": max(values) if isinstance(values[0], (int, float)) else None
                }
                for key, values in patrones.items()
            }
        }
        
        return estadisticas
        
    def sugerir_mejoras(self, tipo: str) -> List[str]:
        """Sugiere mejoras basadas en el análisis de experiencias"""
        patrones = self.analizar_patrones(tipo)
        sugerencias = []
        
        if not patrones:
            return sugerencias
            
        # Analizar tasa de éxito
        if patrones["tasa_exito"] < 0.5:
            sugerencias.append(f"La tasa de éxito para {tipo} es baja ({patrones['tasa_exito']:.2%}). Considera revisar la lógica de ejecución.")
            
        # Analizar patrones de longitud
        if "longitud" in patrones["patrones"]:
            longitudes = patrones["patrones"]["longitud"]
            if longitudes["promedio"] < 10:
                sugerencias.append(f"Las entradas para {tipo} son muy cortas. Considera pedir más detalles al usuario.")
                
        # Analizar palabras clave
        if "palabras_clave" in patrones["patrones"]:
            palabras = patrones["patrones"]["palabras_clave"]
            if palabras["promedio"] < 2:
                sugerencias.append(f"Las entradas para {tipo} tienen pocas palabras clave. Considera mejorar la detección de intención.")
                
        return sugerencias
        
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema de aprendizaje"""
        total_experiencias = sum(len(exps) for exps in self.experiencias.values())
        total_tipos = len(self.experiencias)
        
        return {
            "total_experiencias": total_experiencias,
            "total_tipos_acciones": total_tipos,
            "tipos_mas_usados": sorted(
                [(tipo, len(exps)) for tipo, exps in self.experiencias.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "ultima_actualizacion": datetime.now().isoformat()
        }

    def ejecutar_aprendizaje_continuo(self):
        """Realiza aprendizaje automático continuo en segundo plano: reentrena el vectorizador y optimiza la base de experiencias."""
        self._entrenar_vectorizer()
        self._guardar_experiencias()
        logging.info("[APRENDIZAJE] Aprendizaje continuo ejecutado y optimizado.") 