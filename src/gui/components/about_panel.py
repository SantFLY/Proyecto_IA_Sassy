from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import webbrowser

class AboutPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Acerca de Sassy")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Logo y descripción
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_frame.setStyleSheet("""
            #infoFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("src/gui/resources/bombilla.png")
        logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        info_layout.addWidget(logo_label)
        
        # Información
        info_container = QWidget()
        info_container_layout = QVBoxLayout(info_container)
        info_container_layout.setSpacing(10)
        
        # Versión
        version_label = QLabel("Versión 1.0.0")
        version_label.setStyleSheet("""
            color: #0078D4;
            font-size: 18px;
            font-weight: bold;
        """)
        info_container_layout.addWidget(version_label)
        
        # Descripción
        desc_label = QLabel(
            "Sassy es un sistema de seguridad inteligente que combina antivirus, "
            "firewall y capacidades de aprendizaje automático para proteger tu sistema "
            "de manera proactiva."
        )
        desc_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            line-height: 1.5;
        """)
        desc_label.setWordWrap(True)
        info_container_layout.addWidget(desc_label)
        
        # Características
        features_label = QLabel("Características principales:")
        features_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
        """)
        info_container_layout.addWidget(features_label)
        
        features = [
            "🛡️ Antivirus con detección en tiempo real",
            "🔒 Firewall inteligente",
            "⚡ Sistema proactivo de seguridad",
            "🧠 Aprendizaje automático",
            "📊 Monitoreo de recursos",
            "🔔 Notificaciones en tiempo real"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("""
                color: white;
                font-size: 14px;
                margin-left: 10px;
            """)
            info_container_layout.addWidget(feature_label)
        
        info_container_layout.addStretch()
        info_layout.addWidget(info_container)
        
        layout.addWidget(info_frame)
        
        # Enlaces y contacto
        links_frame = QFrame()
        links_frame.setObjectName("linksFrame")
        links_frame.setStyleSheet("""
            #linksFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        links_layout = QHBoxLayout(links_frame)
        links_layout.setSpacing(10)
        
        # Botones de enlaces
        self.github_btn = QPushButton("GitHub")
        self.docs_btn = QPushButton("Documentación")
        self.support_btn = QPushButton("Soporte")
        
        for btn in [self.github_btn, self.docs_btn, self.support_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
            """)
            links_layout.addWidget(btn)
        
        links_layout.addStretch()
        layout.addWidget(links_frame)
        
        # Créditos
        credits_label = QLabel("© 2024 Sassy Security. Todos los derechos reservados.")
        credits_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
        """)
        credits_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits_label)
        
        # Conectar señales
        self.github_btn.clicked.connect(lambda: webbrowser.open("https://github.com/sassy"))
        self.docs_btn.clicked.connect(lambda: webbrowser.open("https://docs.sassy.com"))
        self.support_btn.clicked.connect(lambda: webbrowser.open("https://support.sassy.com")) 