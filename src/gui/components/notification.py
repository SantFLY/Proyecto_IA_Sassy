from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.QtGui import QFont

class NotificationWidget(QWidget):
    def __init__(self, mensaje, duracion=3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(350)
        layout = QVBoxLayout(self)
        self.label = QLabel(mensaje)
        self.label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.label.setStyleSheet("background: #23272e; color: #ffffff; border-radius: 8px; padding: 16px;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.finished.connect(self._start_timer)
        self.anim.start()
        self.duracion = duracion

    def _start_timer(self):
        QTimer.singleShot(self.duracion, self.hide_notification)

    def hide_notification(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.close)
        self.anim.start() 