from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class StatusCard(QFrame):
    def __init__(self, title, status, icon="", parent=None):
        super().__init__(parent)
        self.setObjectName("statusCard")
        self.setStyleSheet("""
            #statusCard {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid rgba(0,0,0,0.07);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Título
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        # Estado
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet("""
            color: #0078D4;
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(self.status_label)
        
    def update_status(self, status, color="#0078D4"):
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: 14px;
            font-weight: 600;
        """)

class EstadoPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Estado del Sistema")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Grid de tarjetas de estado
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Crear tarjetas de estado
        self.antivirus_card = StatusCard("Antivirus", "Desactivado", "🛡️")
        self.firewall_card = StatusCard("Firewall", "Desactivado", "🔒")
        self.proactividad_card = StatusCard("Sistema Proactivo", "Desactivado", "⚡")
        self.aprendizaje_card = StatusCard("Aprendizaje", "Desactivado", "🧠")
        
        # Agregar tarjetas al grid
        grid.addWidget(self.antivirus_card, 0, 0)
        grid.addWidget(self.firewall_card, 0, 1)
        grid.addWidget(self.proactividad_card, 1, 0)
        grid.addWidget(self.aprendizaje_card, 1, 1)
        
        layout.addLayout(grid)
        
        # Sección de recursos del sistema
        resources_frame = QFrame()
        resources_frame.setObjectName("resourcesFrame")
        resources_frame.setStyleSheet("""
            #resourcesFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        resources_layout = QVBoxLayout(resources_frame)
        
        resources_title = QLabel("Recursos del Sistema")
        resources_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        resources_layout.addWidget(resources_title)
        
        # Grid de recursos
        resources_grid = QGridLayout()
        resources_grid.setSpacing(15)
        
        # Crear tarjetas de recursos
        self.cpu_card = StatusCard("CPU", "0%", "💻")
        self.memoria_card = StatusCard("Memoria", "0%", "📊")
        self.disco_card = StatusCard("Disco", "0%", "💾")
        self.red_card = StatusCard("Red", "0 Mbps", "🌐")
        
        # Agregar tarjetas al grid
        resources_grid.addWidget(self.cpu_card, 0, 0)
        resources_grid.addWidget(self.memoria_card, 0, 1)
        resources_grid.addWidget(self.disco_card, 1, 0)
        resources_grid.addWidget(self.red_card, 1, 1)
        
        resources_layout.addLayout(resources_grid)
        layout.addWidget(resources_frame)
        
        # Espacio flexible al final
        layout.addStretch()
        
    def actualizar_estado(self, componente, estado):
        if componente == 'antivirus':
            self.antivirus_card.update_status(
                "Activo" if estado else "Desactivado",
                "#4CAF50" if estado else "#F44336"
            )
        elif componente == 'firewall':
            self.firewall_card.update_status(
                "Activo" if estado else "Desactivado",
                "#4CAF50" if estado else "#F44336"
            )
        elif componente == 'proactividad':
            self.proactividad_card.update_status(
                "Activo" if estado else "Desactivado",
                "#4CAF50" if estado else "#F44336"
            )
        elif componente == 'aprendizaje':
            self.aprendizaje_card.update_status(
                "Activo" if estado else "Desactivado",
                "#4CAF50" if estado else "#F44336"
            ) 