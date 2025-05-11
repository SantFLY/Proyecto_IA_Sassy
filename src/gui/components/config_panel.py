from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QCheckBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import webbrowser

class ConfigOption(QFrame):
    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.setObjectName("configOption")
        self.setStyleSheet("""
            #configOption {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        # Descripción
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Contenedor para el control
        self.control_container = QWidget()
        self.control_layout = QHBoxLayout(self.control_container)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.control_container)
        
    def add_control(self, control):
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
        if isinstance(control, (QHBoxLayout, QVBoxLayout)):
            container = QWidget()
            container.setLayout(control)
            self.control_layout.addWidget(container)
        else:
            self.control_layout.addWidget(control)

class ConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.controls = {}  # Diccionario para almacenar referencias a los controles
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Configuración")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Contenedor principal con fondo
        main_container = QFrame()
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet("""
            #mainContainer {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(16)
        container_layout.setContentsMargins(16, 16, 16, 16)
        
        # Opciones de configuración
        self.modo_oscuro_cb = self.add_config_option(container_layout, "Modo Oscuro", "checkbox")
        self.notificaciones_cb = self.add_config_option(container_layout, "Notificaciones", "checkbox")
        self.idioma_cb = self.add_config_option(container_layout, "Idioma", "combobox", ["Español", "English"])
        self.tamano_fuente_cb = self.add_config_option(container_layout, "Tamaño de Fuente", "combobox", ["Pequeño", "Mediano", "Grande"])
        
        layout.addWidget(main_container)
        layout.addStretch()
        
        # Créditos y Discord
        creditos = QLabel("Desarrollado por <b>Santiago Polanco</b><br>Comunidad y soporte: <a href='https://discord.gg/455MNAMXdz'>Olimpo (Discord)</a>")
        creditos.setOpenExternalLinks(True)
        creditos.setFont(QFont('Segoe UI', 11))
        creditos.setAlignment(Qt.AlignCenter)
        layout.addWidget(creditos)
        
    def add_config_option(self, layout, title, type, options=None):
        option_frame = QFrame()
        option_frame.setObjectName("optionFrame")
        option_frame.setStyleSheet("""
            #optionFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        option_layout = QHBoxLayout(option_frame)
        option_layout.setContentsMargins(8, 8, 8, 8)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)
        option_layout.addWidget(title_label)
        
        # Control según el tipo
        if type == "checkbox":
            control = QCheckBox()
            control.setStyleSheet("""
                QCheckBox {
                    color: white;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078D4;
                    border: 2px solid #0078D4;
                    border-radius: 4px;
                }
            """)
        elif type == "combobox" and options:
            control = QComboBox()
            control.addItems(options)
            control.setStyleSheet("""
                QComboBox {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: white;
                    min-width: 120px;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #2D2D2D;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    selection-background-color: #0078D4;
                    color: white;
                }
            """)
        
        option_layout.addWidget(control)
        layout.addWidget(option_frame)
        
        # Guardar referencia al control
        self.controls[title.lower().replace(" ", "_")] = control
        return control 