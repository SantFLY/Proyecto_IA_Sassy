import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.gui.main_window import SassyMainWindow
from src.config.modelo_config import MODELO_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sassy.log'),
        logging.StreamHandler()
    ]
)

def main():
    try:
        # Crear directorio de logs si no existe
        os.makedirs('logs', exist_ok=True)
        
        # Verificar que el modelo existe
        if not os.path.exists(MODELO_CONFIG['ruta_modelo']):
            logging.error(f"No se encontró el modelo en: {MODELO_CONFIG['ruta_modelo']}")
            print(f"Error: No se encontró el modelo en: {MODELO_CONFIG['ruta_modelo']}")
            print("Por favor, asegúrate de que el modelo está en la carpeta 'models'")
            return
            
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Crear ventana principal
        window = SassyMainWindow()
        window.show()
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}")
        print(f"Error al iniciar la aplicación: {e}")
        return

if __name__ == '__main__':
    main() 