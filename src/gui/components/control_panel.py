from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QGridLayout, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class ControlButton(QPushButton):
    def __init__(self, text, icon="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}")
        self.setObjectName("controlButton")
        self.setStyleSheet("""
            #controlButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
            }
            #controlButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            #controlButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)

class ControlPanel(QWidget):
    # Señales
    escanear = Signal()
    cuarentena = Signal()
    limpiar = Signal()
    whitelist = Signal()
    bloquear_ip = Signal(str)
    desbloquear_ip = Signal(str)
    accion_proactiva = Signal(str)
    ciclo_aprendizaje = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        title = QLabel("Panel de Control")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # Sección de Antivirus
        antivirus_frame = QFrame()
        antivirus_frame.setObjectName("sectionFrame")
        antivirus_frame.setStyleSheet("""
            #sectionFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        antivirus_layout = QVBoxLayout(antivirus_frame)
        
        # Título de sección
        section_title = QLabel("Antivirus")
        section_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        antivirus_layout.addWidget(section_title)
        
        # Grid de botones
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Botones de antivirus
        self.escanear_btn = ControlButton("Escanear Sistema", "🔍")
        self.cuarentena_btn = ControlButton("Poner en Cuarentena", "🚫")
        self.limpiar_btn = ControlButton("Limpiar Alertas", "🧹")
        self.whitelist_btn = ControlButton("Gestionar Whitelist", "✅")
        
        grid.addWidget(self.escanear_btn, 0, 0)
        grid.addWidget(self.cuarentena_btn, 0, 1)
        grid.addWidget(self.limpiar_btn, 1, 0)
        grid.addWidget(self.whitelist_btn, 1, 1)
        
        antivirus_layout.addLayout(grid)
        layout.addWidget(antivirus_frame)

        # Sección de Firewall
        firewall_frame = QFrame()
        firewall_frame.setObjectName("sectionFrame")
        firewall_frame.setStyleSheet("""
            #sectionFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        firewall_layout = QVBoxLayout(firewall_frame)
        
        # Título de sección
        section_title = QLabel("Firewall")
        section_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        firewall_layout.addWidget(section_title)
        
        # Input y botones de firewall
        input_layout = QHBoxLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Ingrese una dirección IP")
        self.ip_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        
        self.bloquear_btn = ControlButton("Bloquear IP", "🔒")
        self.desbloquear_btn = ControlButton("Desbloquear IP", "🔓")
        
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(self.bloquear_btn)
        input_layout.addWidget(self.desbloquear_btn)
        
        firewall_layout.addLayout(input_layout)
        layout.addWidget(firewall_frame)

        # Sección de Sistema Proactivo
        proactivo_frame = QFrame()
        proactivo_frame.setObjectName("sectionFrame")
        proactivo_frame.setStyleSheet("""
            #sectionFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        proactivo_layout = QVBoxLayout(proactivo_frame)
        
        # Título de sección
        section_title = QLabel("Sistema Proactivo")
        section_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        proactivo_layout.addWidget(section_title)
        
        # Botones de sistema proactivo
        self.proactivo_btn = ControlButton("Ejecutar Acción Proactiva", "⚡")
        proactivo_layout.addWidget(self.proactivo_btn)
        
        layout.addWidget(proactivo_frame)

        # Sección de Aprendizaje
        aprendizaje_frame = QFrame()
        aprendizaje_frame.setObjectName("sectionFrame")
        aprendizaje_frame.setStyleSheet("""
            #sectionFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        aprendizaje_layout = QVBoxLayout(aprendizaje_frame)
        
        # Título de sección
        section_title = QLabel("Sistema de Aprendizaje")
        section_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        aprendizaje_layout.addWidget(section_title)
        
        # Botón de aprendizaje
        self.aprendizaje_btn = ControlButton("Iniciar Ciclo de Aprendizaje", "🧠")
        aprendizaje_layout.addWidget(self.aprendizaje_btn)
        
        layout.addWidget(aprendizaje_frame)

        # Conectar señales
        self.escanear_btn.clicked.connect(self.escanear.emit)
        self.cuarentena_btn.clicked.connect(self.cuarentena.emit)
        self.limpiar_btn.clicked.connect(self.limpiar.emit)
        self.whitelist_btn.clicked.connect(self.whitelist.emit)
        self.bloquear_btn.clicked.connect(lambda: self.bloquear_ip.emit(self.ip_input.text()))
        self.desbloquear_btn.clicked.connect(lambda: self.desbloquear_ip.emit(self.ip_input.text()))
        self.proactivo_btn.clicked.connect(lambda: self.accion_proactiva.emit("default"))
        self.aprendizaje_btn.clicked.connect(self.ciclo_aprendizaje.emit) 