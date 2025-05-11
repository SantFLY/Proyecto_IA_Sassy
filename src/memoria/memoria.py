"""
Módulo de memoria contextual para Sassy.
Integra almacenamiento SQLite con búsqueda semántica.
"""

import sqlite3
import os
from datetime import datetime
from .embeddings import GestorEmbeddings
import json
import threading
from src.utils.web_multi_search import buscar_multiweb, obtener_contenido_url
from src.utils.nutricion_monitor import NutricionMonitor
import queue
import time
from typing import List, Dict

class MemoriaContextual:
    def __init__(self, db_path='data/memoria.db', nutricion_activa=True):
        self.db_path = db_path
        self.embeddings = GestorEmbeddings()
        self._asegurar_db()
        self._nutricion_en_curso = False
        self._monitor_nutricion = None
        self._cola_nutricion = queue.Queue()
        self.nutricion_activa = nutricion_activa
        self.recuerdos = []
        self.nutrir_memoria_inicial()
        if nutricion_activa:
            self.iniciar_nutricion_automatica()
        self.cargar_recuerdos()

    def _asegurar_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS recuerdos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT,
                        contenido TEXT,
                        contexto TEXT,
                        fecha TEXT,
                        relevancia REAL DEFAULT 1.0,
                        categorias TEXT,
                        metadata TEXT
                    )''')
        conn.commit()
        conn.close()

    def guardar_recuerdo(self, contenido, tipo="general", contexto="", categorias=None, metadata=None):
        """Guarda un recuerdo tanto en SQLite como en el sistema de embeddings. Detecta y clasifica datos personales, temas, preferencias, comandos, etc."""
        # Clasificación automática
        categorias = categorias or []
        if any(x in contenido.lower() for x in ["me llamo", "mi nombre es", "soy "]):
            tipo = "dato_usuario"
            categorias.append("nombre")
        if any(x in contenido.lower() for x in ["vivo en", "ciudad", "país", "pais"]):
            tipo = "dato_usuario"
            categorias.append("ubicacion")
        if any(x in contenido.lower() for x in ["cumpleaños", "nací", "naci", "fecha de nacimiento"]):
            tipo = "dato_usuario"
            categorias.append("cumpleaños")
        if any(x in contenido.lower() for x in ["me gusta", "prefiero", "odio", "amo", "favorito"]):
            tipo = "preferencia"
            categorias.append("gustos")
        if any(x in contenido.lower() for x in ["recuerda que", "no olvides que"]):
            tipo = "recordatorio"
            categorias.append("recordatorio")
        if any(x in contenido.lower() for x in ["comando", "ejecuta", "haz", "abre", "cierra"]):
            tipo = "comando"
            categorias.append("comando")
        # Guardar en SQLite
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO recuerdos (tipo, contenido, contexto, fecha, categorias, metadata) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tipo, 
            contenido, 
            json.dumps(contexto),
            datetime.now().isoformat(),
            json.dumps(categorias or []),
            json.dumps(metadata or {})
        ))
        conn.commit()
        conn.close()
        # Guardar en embeddings
        self.embeddings.agregar_recuerdo(contenido, tipo, contexto)
        recuerdo = {
            'contenido': contenido,
            'tipo': tipo,
            'timestamp': time.time(),
            'contexto': contexto or {},
            'categorias': categorias
        }
        self.recuerdos.append(recuerdo)
        if len(self.recuerdos) > 1000:
            self.recuerdos.pop(0)
        if len(self.recuerdos) % 100 == 0:
            self.guardar_recuerdos()

    def buscar_recuerdos(self, consulta, limite=10, tipo=None):
        """Busca recuerdos usando búsqueda semántica y filtros."""
        # Primero buscar por embeddings
        resultados_embeddings = self.embeddings.buscar_similar(consulta, limite)
        
        # Luego buscar en SQLite por palabras clave
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = "SELECT contenido, fecha, relevancia, categorias FROM recuerdos WHERE contenido LIKE ?"
        params = [f"%{consulta}%"]
        
        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)
            
        query += " ORDER BY relevancia DESC, fecha DESC LIMIT ?"
        params.append(limite)
        
        c.execute(query, params)
        resultados_sqlite = c.fetchall()
        conn.close()

        # Combinar y ordenar resultados
        resultados_combinados = []
        
        # Agregar resultados de embeddings
        for r in resultados_embeddings:
            resultados_combinados.append({
                'contenido': r['contenido'],
                'fecha': r['fecha'],
                'relevancia': r['relevancia'],
                'categorias': json.loads(r.get('categorias', '[]')),
                'fuente': 'semantica'
            })
        
        # Agregar resultados de SQLite
        for r in resultados_sqlite:
            resultados_combinados.append({
                'contenido': r[0],
                'fecha': r[1],
                'relevancia': r[2],
                'categorias': json.loads(r[3]),
                'fuente': 'textual'
            })
        
        # Ordenar por relevancia y eliminar duplicados
        resultados_combinados.sort(key=lambda x: x['relevancia'], reverse=True)
        resultados_unicos = []
        contenidos_vistos = set()
        
        for r in resultados_combinados:
            if r['contenido'] not in contenidos_vistos:
                resultados_unicos.append(r)
                contenidos_vistos.add(r['contenido'])
        
        # Buscar en los recuerdos recientes
        for recuerdo in reversed(self.recuerdos):
            if tipo and recuerdo['tipo'] != tipo:
                continue
            if consulta in recuerdo['contenido'].lower():
                resultados_unicos.append(recuerdo)
                if len(resultados_unicos) >= limite:
                    break
        
        return resultados_unicos[:limite]

    def actualizar_relevancia(self, id_recuerdo, nueva_relevancia):
        """Actualiza la relevancia de un recuerdo específico."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE recuerdos SET relevancia = ? WHERE id = ?", 
                 (nueva_relevancia, id_recuerdo))
        conn.commit()
        conn.close()

    def agregar_categoria(self, id_recuerdo, categoria):
        """Agrega una categoría a un recuerdo existente."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT categorias FROM recuerdos WHERE id = ?", (id_recuerdo,))
        categorias_actuales = json.loads(c.fetchone()[0] or '[]')
        if categoria not in categorias_actuales:
            categorias_actuales.append(categoria)
            c.execute("UPDATE recuerdos SET categorias = ? WHERE id = ?",
                     (json.dumps(categorias_actuales), id_recuerdo))
            conn.commit()
        conn.close()

    def buscar_por_categoria(self, categoria, limite=5):
        """Busca recuerdos por categoría específica."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT contenido, fecha, relevancia 
            FROM recuerdos 
            WHERE categorias LIKE ? 
            ORDER BY relevancia DESC, fecha DESC 
            LIMIT ?
        """, (f"%{categoria}%", limite))
        resultados = c.fetchall()
        conn.close()
        return resultados

    def ultimos_recuerdos(self, limite=5):
        """Obtiene los últimos recuerdos almacenados."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT contenido, fecha, relevancia, categorias 
            FROM recuerdos 
            ORDER BY fecha DESC 
            LIMIT ?
        """, (limite,))
        resultados = c.fetchall()
        conn.close()
        return [{
            'contenido': r[0],
            'fecha': r[1],
            'relevancia': r[2],
            'categorias': json.loads(r[3])
        } for r in resultados]

    def nutrir_memoria_inicial(self):
        """Nutre la base de datos con recuerdos iniciales si está vacía."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM recuerdos")
        cantidad = c.fetchone()[0]
        conn.close()
        if cantidad > 0:
            return  # Ya hay recuerdos
        # Recuerdos iniciales
        recuerdos = [
            {"contenido": "Mi color favorito es el azul", "tipo": "preferencia", "categorias": ["colores", "gustos"]},
            {"contenido": "Me gusta la pizza con extra queso", "tipo": "preferencia", "categorias": ["comida", "gustos"]},
            {"contenido": "Mi hobby es aprender cosas nuevas sobre inteligencia artificial", "tipo": "personalidad", "categorias": ["hobbies", "ia"]},
            {"contenido": "Puedes preguntarme la hora o la fecha en cualquier momento", "tipo": "ayuda", "categorias": ["comandos", "ayuda"]},
            {"contenido": "Recuerda que siempre puedes decir 'salir' para terminar la conversación", "tipo": "ayuda", "categorias": ["comandos", "ayuda"]},
            {"contenido": "La curiosidad es el motor del aprendizaje", "tipo": "motivacional", "categorias": ["frases", "motivacion"]},
            {"contenido": "¿Sabías que el cerebro humano tiene más conexiones que estrellas hay en la galaxia?", "tipo": "dato_curioso", "categorias": ["curiosidades"]},
            {"contenido": "Puedo ayudarte a buscar información en internet si lo necesitas", "tipo": "ayuda", "categorias": ["comandos", "ayuda"]},
            {"contenido": "Me esfuerzo por aprender de cada conversación contigo", "tipo": "personalidad", "categorias": ["ia", "aprendizaje"]},
            {"contenido": "Si me dices 'recuerda que...' guardaré esa información para ti", "tipo": "ayuda", "categorias": ["comandos", "memoria"]}
        ]
        for r in recuerdos:
            self.guardar_recuerdo(
                r["contenido"],
                tipo=r.get("tipo", "general"),
                categorias=r.get("categorias", []),
                contexto="nutricion_inicial"
            )

    def nutrir_memoria_desde_internet(self):
        # Temas priorizados
        temas_prioridad = [
            "programación", "python", "javascript", "inteligencia artificial", "machine learning", "desarrollo de videojuegos", "videojuegos", "historia de los videojuegos", "cultura gamer", "Colombia", "historia de Colombia", "expresiones colombianas", "modismos colombianos", "idioma español", "expresiones en español", "frases célebres en español", "cultura colombiana", "comida colombiana", "lugares turísticos de Colombia", "personajes históricos de Colombia", "expresiones populares", "slang español", "slang colombiano"
        ]
        temas_secundarios = [
            "frases motivacionales", "datos curiosos de ciencia", "curiosidades sobre tecnología", "consejos de productividad", "beneficios de la meditación", "cómo organizar tu día", "historia universal", "arte moderno", "salud y bienestar", "cultura general", "recetas fáciles", "emociones humanas", "inventos que cambiaron el mundo", "descubrimientos científicos recientes", "biografías de personajes famosos", "eventos históricos importantes"
        ]
        variaciones = [
            "curiosidades de {}", "datos interesantes de {}", "información sobre {}", "consejos de {}", "ejemplos de {}", "beneficios de {}", "importancia de {}", "historia de {}", "frases célebres de {}", "cómo se usa {}", "tutorial de {}", "mejores prácticas de {}", "expresiones de {}", "slang de {}", "cultura de {}", "impacto de {}", "personajes de {}", "hechos históricos de {}"
        ]
        # Consultas únicas y priorizadas
        consultas = set()
        for tema in temas_prioridad:
            for variacion in variaciones:
                consulta = variacion.format(tema).lower().strip()
                consultas.add(consulta)
        for tema in temas_secundarios:
            for variacion in variaciones[:6]:  # Menos variaciones para secundarios
                consulta = variacion.format(tema).lower().strip()
                consultas.add(consulta)
        consultas = list(consultas)
        total_consultas = len(consultas)
        
        # Crear monitor solo si no existe
        if not hasattr(self, '_monitor_nutricion') or self._monitor_nutricion is None:
            monitor = NutricionMonitor(total_consultas)
            self._monitor_nutricion = monitor
        else:
            monitor = self._monitor_nutricion

        def nutricion_worker():
            recuerdos_guardados = set()
            contador = 0
            for consulta in consultas:
                fuente = "-"
                mensaje = ""
                texto = ""
                try:
                    resultado, extra = buscar_multiweb(consulta, extra_info=True)
                    # Filtro: solo guardar si es útil, largo y no contiene errores
                    if resultado and len(resultado) > 80 and not any(x in resultado.lower() for x in ["error", "sin resultado", "ver más en wikipedia", "ver mas en wikipedia"]):
                        # Añadir contenido extra si está disponible
                        if extra and len(extra) > 100:
                            resultado += f"\n\n[Contenido extendido:]\n{extra[:1200]}..."
                        if resultado not in recuerdos_guardados:
                            self.guardar_recuerdo(
                                resultado,
                                tipo="nutricion_web",
                                categorias=["internet", "auto_nutricion"],
                                contexto="nutricion_automatica",
                                metadata={"fuente_detectada": True, "consulta": consulta}
                            )
                            recuerdos_guardados.add(resultado)
                            contador += 1
                            fuente = "multiweb"
                            mensaje = f"✔ Recuerdo guardado de: {consulta}"
                            texto = resultado
                        else:
                            mensaje = f"(Duplicado) {consulta}"
                    else:
                        mensaje = f"Sin resultado: {consulta}"
                except Exception as e:
                    mensaje = f"[ERROR] {e}"
                self._cola_nutricion.put((contador, fuente, mensaje, texto))
                if monitor.cerrado:
                    return
            self._cola_nutricion.put((contador, "-", "Nutrición completada", ""))
            print(f"\nResumen de nutrición: {contador} recuerdos útiles guardados de {total_consultas} consultas.")
            self._nutricion_en_curso = False

        def actualizar_monitor():
            try:
                while True:
                    item = self._cola_nutricion.get_nowait()
                    monitor.actualizar(*item)
            except queue.Empty:
                pass
            if not monitor.cerrado:
                monitor.programar_actualizacion(actualizar_monitor, 100)
            else:
                self._monitor_nutricion = None  # Limpiar referencia al cerrar

        # Iniciar el worker y el monitor
        monitor.programar_actualizacion(actualizar_monitor, 100)
        threading.Thread(target=nutricion_worker, daemon=True).start()

    def iniciar_nutricion_automatica(self):
        """Lanza la nutrición automática en un hilo en segundo plano, solo si no está ya en curso."""
        if hasattr(self, '_nutricion_en_curso') and self._nutricion_en_curso:
            return
        self._nutricion_en_curso = True
        if hasattr(self, '_monitor_nutricion') and self._monitor_nutricion:
            try:
                self._monitor_nutricion.root.destroy()
            except Exception:
                pass
        self._monitor_nutricion = None
        self.nutrir_memoria_desde_internet()

    def guardar_recuerdos(self):
        """Guarda los recuerdos en disco."""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/recuerdos.json', 'w', encoding='utf-8') as f:
                json.dump(self.recuerdos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar recuerdos: {e}")

    def cargar_recuerdos(self):
        """Carga los recuerdos desde disco."""
        try:
            if os.path.exists('data/recuerdos.json'):
                with open('data/recuerdos.json', 'r', encoding='utf-8') as f:
                    self.recuerdos = json.load(f)
        except Exception as e:
            print(f"Error al cargar recuerdos: {e}")

    def guardar_estado_final(self):
        """Guarda el estado final de la memoria y embeddings en disco."""
        # Guardar embeddings y recuerdos en disco
        if hasattr(self.embeddings, '_guardar_index'):
            self.embeddings._guardar_index()
        self.guardar_recuerdos() 

    def obtener_ultimas_interacciones(self, n=5):
        """Devuelve las últimas n interacciones guardadas en la memoria."""
        return self.recuerdos[-n:] if hasattr(self, 'recuerdos') else []

    def buscar_temas_relacionados(self, texto, n=3):
        """Devuelve una lista de temas relacionados encontrados en los recuerdos."""
        temas = set()
        for recuerdo in self.recuerdos[-50:]:
            for palabra in texto.lower().split():
                if palabra in recuerdo['contenido'].lower():
                    temas.add(palabra)
        return list(temas)[:n]

    def agregar_interaccion(self, entrada, respuesta):
        """Guarda la interacción usuario-asistente como recuerdo, detectando temas y datos personales automáticamente."""
        # Detectar si la entrada contiene datos personales o temas importantes
        self.guardar_recuerdo(f"Usuario: {entrada}", tipo="interaccion", categorias=["usuario"])
        self.guardar_recuerdo(f"Sassy: {respuesta}", tipo="interaccion", categorias=["asistente"])
        # Guardar inmediatamente en disco para persistencia
        self.recuerdos = self.recuerdos[-500:]  # Limitar a los últimos 500 recuerdos para eficiencia
        self.guardar_recuerdos() 