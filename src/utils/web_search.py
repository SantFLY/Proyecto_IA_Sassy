"""
Módulo de búsqueda web para Sassy usando DuckDuckGo.
"""
import requests

def buscar_duckduckgo(query):
    """Realiza una búsqueda en DuckDuckGo y retorna el mejor resultado posible."""
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
        "skip_disambig": 1
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("AbstractText"):
            return data["AbstractText"] + (f"\nMás info: {data['AbstractURL']}" if data.get("AbstractURL") else "")
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"] + (f"\nMás info: {topic['FirstURL']}" if topic.get("FirstURL") else "")
            # Si no hay texto, mostrar el primer enlace
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("FirstURL"):
                    return f"No encontré un resumen, pero aquí tienes un enlace relevante:\n{topic['FirstURL']}"
        # Si no hay nada, intenta mostrar el primer resultado de 'Results'
        if data.get("Results"):
            for result in data["Results"]:
                if result.get("FirstURL"):
                    return f"No encontré un resumen, pero aquí tienes un enlace relevante:\n{result['FirstURL']}"
        return "No se encontraron resultados relevantes en la web."
    except Exception as e:
        return f"Error al buscar en la web: {e}" 