"""
Módulo de búsqueda web combinada para Sassy.
Intenta buscar información en varias fuentes (Google Custom Search API, Wikipedia) y devuelve el primer resultado útil.
"""

import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

def buscar_wikipedia(query):
    try:
        # Buscar el título real del artículo
        url_api = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={query.replace(' ', '%20')}&format=json"
        resp_api = requests.get(url_api, timeout=5)
        if resp_api.status_code == 200:
            data_api = resp_api.json()
            if 'query' in data_api and 'search' in data_api['query'] and len(data_api['query']['search']) > 0:
                title = data_api['query']['search'][0]['title']
                url_summary = f"https://es.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
                resp = requests.get(url_summary, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'extract' in data and data['extract']:
                        enlace = f"https://es.wikipedia.org/wiki/{title.replace(' ', '_')}"
                        return f"{data['extract']}\nEnlace: {enlace} (Fuente: Wikipedia)"
    except Exception:
        pass
    return None

def buscar_google_api(query):
    try:
        url = (
            f"https://www.googleapis.com/customsearch/v1?q={query.replace(' ', '+')}"
            f"&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&num=1"
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                titulo = item.get('title', '')
                snippet = item.get('snippet', '')
                link = item.get('link', '')
                texto = f"{titulo}\n{snippet}\nURL: {link} (Fuente: Google API)"
                if len(texto) > 30:
                    return texto
    except Exception:
        pass
    return None

def simplificar_consulta(query):
    palabras = query.split()
    palabras_utiles = [p for p in palabras if p.lower() not in {"cómo", "por", "qué", "es", "de", "la", "el", "los", "las", "sobre", "para", "en", "del", "un", "una", "y", "a", "con", "más", "menos", "que", "funciona", "importante", "hechos", "sorprendentes", "interesantes", "información", "confiable", "artículos", "noticias", "recientes", "frases", "célebres", "ejemplos", "prácticos"}]
    return ' '.join(palabras_utiles) if palabras_utiles else query

def buscar_multiweb(query, extra_info=False):
    """Busca en varias fuentes y devuelve el primer resultado útil y, si extra_info=True, el contenido extendido."""
    consulta_simple = simplificar_consulta(query)
    # 1. Google Custom Search API
    resultado = None
    extra = ""
    res = buscar_google_api(consulta_simple)
    if res and len(res) > 30:
        resultado = res
        # Intentar obtener contenido extendido de la URL
        if extra_info and "URL: " in res:
            url = ""
            for l in res.split("\n"):
                if l.startswith("URL: "):
                    url = l[5:].split()[0]
            if url:
                extra = obtener_contenido_url(url)
        if resultado and (not extra_info):
            return resultado
        if resultado and extra_info:
            return resultado, extra
    # 2. Wikipedia
    res = buscar_wikipedia(consulta_simple)
    if res:
        resultado = res
        # Intentar obtener más texto útil del artículo
        if extra_info and "Enlace: " in res:
            url = ""
            for l in res.split("\n"):
                if l.startswith("Enlace: "):
                    url = l[8:].split()[0]
            if url:
                extra = obtener_contenido_url(url)
        if resultado and (not extra_info):
            return resultado
        if resultado and extra_info:
            return resultado, extra
    if extra_info:
        return None, ""
    return None

def obtener_contenido_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=7)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Extraer los párrafos más largos
        parrafos = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 60]
        texto = '\n'.join(parrafos)
        return texto.strip()
    except Exception:
        return "" 