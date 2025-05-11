"""
Módulo para escanear y detectar aplicaciones instaladas en el sistema (como en 'Aplicaciones instaladas' de Windows).
"""

import os
import winreg
import unicodedata
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

class AppScanner:
    def __init__(self):
        """Inicializa el escáner de aplicaciones."""
        self.apps_cache = {}
        self.normalized_cache = {}
        self._scan_installed_apps()

    def _normalize(self, text: str) -> str:
        """Normaliza el texto: minúsculas, sin tildes, sin caracteres especiales."""
        if not text:
            return ""
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        text = ''.join(c for c in text if c.isalnum() or c.isspace())
        return text.strip()

    def _scan_installed_apps(self):
        """Escanea las aplicaciones instaladas leyendo el registro de Windows."""
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        for root, path in reg_paths:
            self._scan_registry_apps(root, path)
        # Construir caché normalizada
        for key, info in self.apps_cache.items():
            norm = self._normalize(key)
            self.normalized_cache[norm] = info

    def _scan_registry_apps(self, root, path):
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name = self._get_reg_value(subkey, "DisplayName")
                            display_icon = self._get_reg_value(subkey, "DisplayIcon")
                            install_location = self._get_reg_value(subkey, "InstallLocation")
                            uninstall_string = self._get_reg_value(subkey, "UninstallString")
                            if display_name:
                                exe_path = None
                                if display_icon and os.path.exists(display_icon.split(",")[0]):
                                    exe_path = display_icon.split(",")[0]
                                elif install_location and os.path.exists(install_location):
                                    for file in os.listdir(install_location):
                                        if file.lower().endswith('.exe'):
                                            exe_path = os.path.join(install_location, file)
                                            break
                                self.apps_cache[display_name] = {
                                    "name": display_name,
                                    "exe_path": exe_path,
                                    "uninstall": uninstall_string
                                }
                    except Exception:
                        continue
        except Exception:
            pass

    def _get_reg_value(self, key, value):
        try:
            return winreg.QueryValueEx(key, value)[0]
        except Exception:
            return None

    def _similarity_ratio(self, a: str, b: str) -> float:
        """Calcula la similitud entre dos strings."""
        return SequenceMatcher(None, a, b).ratio()

    def find_app(self, app_name: str) -> Tuple[Dict, List[str]]:
        """
        Busca una aplicación por nombre y retorna coincidencias similares.
        
        Args:
            app_name: Nombre de la aplicación a buscar
            
        Returns:
            Tuple con (info de la app, lista de apps similares)
        """
        norm_query = self._normalize(app_name)
        # Buscar coincidencia exacta normalizada
        if norm_query in self.normalized_cache:
            return self.normalized_cache[norm_query], []
        # Buscar coincidencias parciales y similares
        similar_apps = []
        for norm_name, info in self.normalized_cache.items():
            if norm_query in norm_name:
                similar_apps.append((norm_name, 1.0))
            else:
                similarity = self._similarity_ratio(norm_query, norm_name)
                if similarity > 0.6:
                    similar_apps.append((norm_name, similarity))
        similar_apps.sort(key=lambda x: x[1], reverse=True)
        if len(similar_apps) > 10:
            return None, [self.normalized_cache[app[0]]["name"] for app in similar_apps[:10]]
        if similar_apps:
            best_match = similar_apps[0][0]
            return self.normalized_cache[best_match], [self.normalized_cache[app[0]]["name"] for app in similar_apps[1:4]]
        return None, []

    def get_all_apps(self) -> List[str]:
        """
        Retorna la lista de todas las aplicaciones encontradas.
        
        Returns:
            Lista de nombres de aplicaciones
        """
        return [info["name"] for info in self.apps_cache.values() if info["exe_path"]] 