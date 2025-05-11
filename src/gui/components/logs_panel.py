from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTextEdit, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from datetime import datetime

class LogEntry(QFrame):
    def __init__(self, timestamp, level, message, parent=None):
        super().__init__(parent)
        self.setObjectName("logEntry")
        
        # Definir colores según el nivel
        colors = {
            "INFO": "#0078D4",
            "WARNING": "#FFB900",
            "ERROR": "#E81123",
            "DEBUG": "#107C10"
        }
        color = colors.get(level, "#0078D4")
        
        self.setStyleSheet(f"""
            #logEntry {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                margin: 2px 0;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Timestamp
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            min-width: 150px;
        """)
        layout.addWidget(time_label)
        
        # Nivel
        level_label = QLabel(level)
        level_label.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
            font-weight: bold;
            min-width: 80px;
        """)
        layout.addWidget(level_label)
        
        # Mensaje
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            color: white;
            font-size: 14px;
        """)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addStretch()

class LogsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.todos_los_logs = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Registros del Sistema")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Controles de filtrado
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")
        controls_frame.setStyleSheet("""
            #controlsFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(10)
        
        # Filtro de texto
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Buscar en logs...")
        self.filtro.setStyleSheet("""
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
        self.filtro.textChanged.connect(self.filtrar_logs)
        
        # Filtro de nivel
        self.nivel_filtro = QComboBox()
        self.nivel_filtro.addItems(["Todos", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.nivel_filtro.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
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
                border: none;
                border-radius: 6px;
                selection-background-color: #0078D4;
            }
        """)
        self.nivel_filtro.currentTextChanged.connect(self.filtrar_logs)
        
        controls_layout.addWidget(self.filtro)
        controls_layout.addWidget(self.nivel_filtro)
        
        layout.addWidget(controls_frame)
        
        # Área de logs
        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setSpacing(4)
        self.logs_layout.setAlignment(Qt.AlignTop)
        
        # Scroll area para los logs
        scroll_area = QFrame()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setStyleSheet("""
            #scrollArea {
                background-color: rgba(255,255,255,0.13);
                border-radius: 16px;
                border: 1px solid rgba(0,0,0,0.07);
            }
        """)
        
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.addWidget(self.logs_container)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(scroll_area)
        
    def filtrar_logs(self):
        # Limpiar logs actuales de forma segura
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        texto_filtro = self.filtro.text().lower()
        nivel_filtro = self.nivel_filtro.currentText()
        
        # Si no hay logs, mostrar mensaje
        if not self.todos_los_logs:
            no_logs = QLabel("No hay logs disponibles")
            no_logs.setStyleSheet("""
                color: rgba(255, 255, 255, 0.5);
                font-size: 14px;
                padding: 20px;
            """)
            no_logs.setAlignment(Qt.AlignCenter)
            self.logs_layout.addWidget(no_logs)
            return
            
        for log in self.todos_los_logs:
            # Soporte para logs en formato string (simulados)
            if isinstance(log, str):
                if texto_filtro and texto_filtro not in log.lower():
                    continue
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                entry = LogEntry(timestamp, "INFO", log)
                self.logs_layout.addWidget(entry)
                continue
                
            # Soporte para logs en formato dict
            if not all(k in log for k in ("timestamp", "nivel", "mensaje")):
                continue
                
            if nivel_filtro != "Todos" and log['nivel'] != nivel_filtro:
                continue
                
            if texto_filtro and texto_filtro not in log['mensaje'].lower():
                continue
                
            # Crear entrada de log
            timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            entry = LogEntry(timestamp, log['nivel'], log['mensaje'])
            self.logs_layout.addWidget(entry)
            
        # Agregar espacio flexible al final
        self.logs_layout.addStretch() 