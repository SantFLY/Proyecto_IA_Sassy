from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from ..adapters.chat_adapter import ChatAdapter

class ChatWorker(QThread):
    respuesta_lista = Signal(str)
    
    def __init__(self, mensaje, chat_adapter):
        super().__init__()
        self.mensaje = mensaje
        self.chat_adapter = chat_adapter
        
    def run(self):
        respuesta = self.chat_adapter.procesar_mensaje(self.mensaje)
        self.respuesta_lista.emit(respuesta)

class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.chat_adapter = ChatAdapter()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Logo/avatar de Sassy
        avatar = QLabel()
        avatar_pixmap = QPixmap("src/gui/resources/bombilla.png")
        avatar.setPixmap(avatar_pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)

        # Título
        title = QLabel("Chat con Sassy")
        title.setStyleSheet("color: #222; font-size: 22px; font-weight: bold; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Contenedor principal con fondo
        main_container = QFrame()
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet("""
            #mainContainer {
                background-color: rgba(255, 255, 255, 0.13);
                border-radius: 18px;
                border: 1.5px solid rgba(0,0,0,0.09);
            }
        """)
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(12)
        container_layout.setContentsMargins(24, 24, 24, 24)

        # Área de chat con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(260)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Contenedor de mensajes
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(10)
        self.messages_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.messages_container)
        container_layout.addWidget(scroll_area)

        # Input y botón
        input_container = QFrame()
        input_container.setStyleSheet("background: transparent;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe un mensaje...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.9);
                border: 1.5px solid #0078D4;
                border-radius: 8px;
                padding: 10px 14px;
                color: #222;
                font-size: 15px;
            }
        """)
        send_button = QPushButton("Enviar")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                color: white;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #106EBE
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        container_layout.addWidget(input_container)
        layout.addWidget(main_container)

        # Conectar señales
        send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def add_message(self, sender, message):
        bubble = QFrame()
        bubble.setStyleSheet(f"""
            QFrame {{
                background-color: {'#0078D4' if sender == 'Tú' else 'rgba(255,255,255,0.85)'};
                color: {'white' if sender == 'Tú' else '#222'};
                border-radius: 12px;
                padding: 10px 16px;
                margin-left: {0 if sender == 'Tú' else 40}px;
                margin-right: {40 if sender == 'Tú' else 0}px;
                max-width: 70%;
            }}
        """)
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        sender_label = QLabel(sender)
        sender_label.setStyleSheet("font-size: 12px; color: #888; font-weight: bold;")
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(sender_label)
        layout.addWidget(message_label)
        self.messages_layout.addWidget(bubble)
        self.messages_container.update()
        self.messages_container.adjustSize()

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            # Mostrar mensaje del usuario
            self.add_message("Tú", message)
            self.message_input.clear()
            
            # Deshabilitar input mientras se procesa
            self.message_input.setEnabled(False)
            
            # Crear y conectar worker
            self.worker = ChatWorker(message, self.chat_adapter)
            self.worker.respuesta_lista.connect(self.handle_response)
            self.worker.start()
            
    def handle_response(self, respuesta):
        # Mostrar respuesta de Sassy
        self.add_message("Sassy", respuesta)
        # Rehabilitar input
        self.message_input.setEnabled(True)
        self.message_input.setFocus() 