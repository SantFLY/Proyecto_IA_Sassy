"""
Módulo de embeddings y relaciones semánticas para Sassy.
Utiliza sentence-transformers para generar embeddings semánticos.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
from datetime import datetime

class GestorEmbeddings:
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.recuerdos = []
        self._cargar_o_crear_index()
    
    def _cargar_o_crear_index(self):
        """Carga o crea el índice FAISS para búsqueda rápida."""
        self.index_path = 'data/embeddings_index.pkl'
        if not os.path.exists(self.index_path) or os.path.getsize(self.index_path) == 0:
            print('[Embeddings] Archivo de índice no existe o está vacío. Creando nuevo índice.')
            self.index = {}
            with open(self.index_path, 'wb') as f:
                pickle.dump(self.index, f)
            return
        try:
            with open(self.index_path, 'rb') as f:
                self.index = pickle.load(f)
        except (EOFError, pickle.UnpicklingError, Exception) as e:
            print(f'[Embeddings] Error al cargar el índice: {e}. Se creará uno nuevo.')
            self.index = {}
            with open(self.index_path, 'wb') as f:
                pickle.dump(self.index, f)
        self.recuerdos = []
    
    def _guardar_index(self):
        """Guarda el índice y los recuerdos en disco."""
        os.makedirs('data', exist_ok=True)
        with open('data/embeddings_index.pkl', 'wb') as f:
            pickle.dump(self.index, f)
        with open('data/embeddings_recuerdos.pkl', 'wb') as f:
            pickle.dump(self.recuerdos, f)
    
    def agregar_recuerdo(self, contenido, tipo="general", contexto=""):
        """Agrega un nuevo recuerdo al sistema de embeddings."""
        embedding = self.model.encode([contenido])[0]
        self.index.add(np.array([embedding], dtype=np.float32))
        self.recuerdos.append({
            'contenido': contenido,
            'tipo': tipo,
            'contexto': contexto,
            'fecha': datetime.now().isoformat()
        })
        self._guardar_index()
    
    def buscar_similar(self, consulta, k=5):
        """Busca recuerdos similares usando embeddings semánticos."""
        query_embedding = self.model.encode([consulta])[0]
        D, I = self.index.search(np.array([query_embedding], dtype=np.float32), k)
        
        resultados = []
        for i, (distancia, idx) in enumerate(zip(D[0], I[0])):
            if idx < len(self.recuerdos):
                recuerdo = self.recuerdos[idx]
                resultados.append({
                    'contenido': recuerdo['contenido'],
                    'tipo': recuerdo['tipo'],
                    'contexto': recuerdo['contexto'],
                    'fecha': recuerdo['fecha'],
                    'relevancia': 1.0 / (1.0 + distancia)  # Normalizar relevancia
                })
        
        return sorted(resultados, key=lambda x: x['relevancia'], reverse=True) 