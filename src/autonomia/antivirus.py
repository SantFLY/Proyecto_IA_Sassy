from typing import List, Dict, Optional
import os
import hashlib
import logging

class AntivirusSassy:
    def __init__(self):
        self.archivos_cuarentena = []
        self.alertas = []
        self.hashes_maliciosos = set()  # Aquí se cargarían hashes conocidos

    def escanear_archivo(self, ruta: str) -> Dict:
        """Escanea un archivo y detecta si es sospechoso por hash"""
        try:
            hash_archivo = self._calcular_hash(ruta)
            if hash_archivo in self.hashes_maliciosos:
                self.alertas.append(f"Archivo malicioso detectado: {ruta}")
                return {"sospechoso": True, "hash": hash_archivo}
            return {"sospechoso": False, "hash": hash_archivo}
        except Exception as e:
            logging.error(f"Error al escanear archivo {ruta}: {e}")
            return {"sospechoso": None, "error": str(e)}

    def escanear_directorio(self, ruta: str) -> List[Dict]:
        """Escanea todos los archivos de un directorio"""
        resultados = []
        for root, _, files in os.walk(ruta):
            for file in files:
                resultado = self.escanear_archivo(os.path.join(root, file))
                resultados.append({"archivo": os.path.join(root, file), **resultado})
        return resultados

    def poner_en_cuarentena(self, ruta: str):
        """Simula poner un archivo en cuarentena"""
        self.archivos_cuarentena.append(ruta)
        logging.info(f"Archivo puesto en cuarentena: {ruta}")

    def mostrar_alertas(self) -> List[str]:
        """Devuelve las alertas de seguridad recientes"""
        return self.alertas

    def _calcular_hash(self, ruta: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        sha256 = hashlib.sha256()
        with open(ruta, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest() 