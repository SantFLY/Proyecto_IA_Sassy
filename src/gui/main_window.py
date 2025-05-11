import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMenuBar, 
    QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QAction
from .theme import get_modern_theme
from .components.chat_panel import ChatPanel
from .components.estado_panel import EstadoPanel
from .components.control_panel import ControlPanel
from .components.config_panel import ConfigPanel
from .components.logs_panel import LogsPanel
from .components.about_panel import AboutPanel
from .adapters.antivirus_adapter import AntivirusAdapter
from .adapters.firewall_adapter import FirewallAdapter
from .adapters.proactividad_adapter import ProactividadAdapter
from .adapters.aprendizaje_adapter import AprendizajeAdapter
from .adapters.memoria_adapter import MemoriaAdapter
from .adapters.logs_adapter import LogsAdapter
from .components.notification import NotificationWidget

class SassyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sassy - Interfaz Gráfica")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.dark_mode = False
        self.setStyleSheet(get_modern_theme(self.dark_mode))

        # Adaptadores backend
        self.antivirus_adapter = AntivirusAdapter()
        self.firewall_adapter = FirewallAdapter()
        self.proactividad_adapter = ProactividadAdapter()
        self.aprendizaje_adapter = AprendizajeAdapter()
        self.memoria_adapter = MemoriaAdapter()
        self.logs_adapter = LogsAdapter()

        # Widget central con layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Barra superior con logo y menú
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        
        # Logo pequeño
        logo_label = QLabel()
        logo_pixmap = QPixmap("src/gui/resources/bombilla.png")
        logo_label.setPixmap(logo_pixmap.scaled(QSize(32, 32), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(logo_label)
        
        # Menú superior
        self.menu_bar = QMenuBar()
        self._crear_menus()
        top_layout.addWidget(self.menu_bar)
        top_layout.addStretch()
        
        main_layout.addWidget(top_bar)

        # Stack de páginas
        self.page_stack = QStackedWidget()
        
        # Crear páginas
        self.welcome_page = self._create_welcome_page()
        self.chat_page = ChatPanel()
        self.estado_page = EstadoPanel()
        self.control_page = ControlPanel()
        self.config_page = ConfigPanel()
        self.logs_page = LogsPanel()
        self.about_page = AboutPanel()

        # Agregar páginas al stack
        self.page_stack.addWidget(self.welcome_page)
        self.page_stack.addWidget(self.chat_page)
        self.page_stack.addWidget(self.estado_page)
        self.page_stack.addWidget(self.control_page)
        self.page_stack.addWidget(self.config_page)
        self.page_stack.addWidget(self.logs_page)
        self.page_stack.addWidget(self.about_page)

        main_layout.addWidget(self.page_stack)

        # Estado de funciones
        self.funciones = {
            'antivirus': self.antivirus_adapter.estado(),
            'firewall': self.firewall_adapter.estado(),
            'proactivo': self.proactividad_adapter.estado(),
            'aprendizaje': self.aprendizaje_adapter.estado(),
            'notificaciones': True
        }

        # Conectar panel de control con acciones reales
        self.control_page.escanear.connect(self.antivirus_adapter.escanear)
        self.control_page.cuarentena.connect(lambda: self.antivirus_adapter.poner_en_cuarentena("archivo_sospechoso"))
        self.control_page.limpiar.connect(self.antivirus_adapter.limpiar_alertas)
        self.control_page.whitelist.connect(lambda: self.show_notification("Función de whitelist ejecutada."))
        self.control_page.bloquear_ip.connect(self._bloquear_ip)
        self.control_page.desbloquear_ip.connect(self._desbloquear_ip)
        self.control_page.accion_proactiva.connect(self._ejecutar_accion_proactiva)
        self.control_page.ciclo_aprendizaje.connect(self._iniciar_ciclo_aprendizaje)

        # Actualizar panel de estado con el estado real
        self._actualizar_estado_panel()

        self.logs_timer = QTimer(self)
        self.logs_timer.timeout.connect(self._actualizar_logs_panel)
        self.logs_timer.start(3000)  # Actualiza cada 3 segundos

        # Sincronizar configuración inicial
        self.config_page.modo_oscuro_cb.setChecked(self.dark_mode)
        self.config_page.notificaciones_cb.setChecked(self.funciones['notificaciones'])
        self.config_page.modo_oscuro_cb.stateChanged.connect(lambda v: self.modo_oscuro_action.setChecked(bool(v)))
        self.config_page.notificaciones_cb.stateChanged.connect(lambda v: self.notificaciones_action.setChecked(bool(v)))
        self.modo_oscuro_action.toggled.connect(self.config_page.modo_oscuro_cb.setChecked)
        self.notificaciones_action.toggled.connect(self.config_page.notificaciones_cb.setChecked)
        self.modo_oscuro_action.toggled.connect(self._toggle_modo_oscuro)
        self.notificaciones_action.toggled.connect(lambda v: self._toggle_funcion('notificaciones', v))

        # Mostrar la pantalla de chat al iniciar
        self.page_stack.setCurrentWidget(self.chat_page)

    def _create_welcome_page(self):
        welcome = QWidget()
        layout = QVBoxLayout(welcome)
        
        # Logo grande centrado
        logo_label = QLabel()
        logo_pixmap = QPixmap("src/gui/resources/bombilla.png")
        logo_label.setPixmap(logo_pixmap.scaled(QSize(200, 200), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Mensaje de bienvenida
        welcome_label = QLabel("Bienvenido a Sassy")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        layout.addStretch()
        return welcome

    def _crear_menus(self):
        menu_funciones = self.menu_bar.addMenu("Funciones")
        self.antivirus_action = QAction("Antivirus", self, checkable=True, checked=self.antivirus_adapter.estado())
        self.firewall_action = QAction("Firewall", self, checkable=True, checked=self.firewall_adapter.estado())
        self.proactivo_action = QAction("Sistema Proactivo", self, checkable=True, checked=self.proactividad_adapter.estado())
        self.aprendizaje_action = QAction("Aprendizaje", self, checkable=True, checked=self.aprendizaje_adapter.estado())
        self.notificaciones_action = QAction("Notificaciones", self, checkable=True, checked=True)
        
        menu_funciones.addAction(self.antivirus_action)
        menu_funciones.addAction(self.firewall_action)
        menu_funciones.addAction(self.proactivo_action)
        menu_funciones.addAction(self.aprendizaje_action)
        menu_funciones.addAction(self.notificaciones_action)
        
        self.antivirus_action.toggled.connect(lambda v: self._toggle_funcion('antivirus', v))
        self.firewall_action.toggled.connect(lambda v: self._toggle_funcion('firewall', v))
        self.proactivo_action.toggled.connect(lambda v: self._toggle_funcion('proactivo', v))
        self.aprendizaje_action.toggled.connect(lambda v: self._toggle_funcion('aprendizaje', v))
        self.notificaciones_action.toggled.connect(lambda v: self._toggle_funcion('notificaciones', v))

        menu_apariencia = self.menu_bar.addMenu("Apariencia")
        self.modo_oscuro_action = QAction("Modo oscuro", self, checkable=True, checked=False)
        menu_apariencia.addAction(self.modo_oscuro_action)
        self.modo_oscuro_action.toggled.connect(self._toggle_modo_oscuro)

        # Menú de navegación
        menu_navegacion = self.menu_bar.addMenu("Navegación")
        chat_action = QAction("Chat", self)
        estado_action = QAction("Estado", self)
        control_action = QAction("Control", self)
        config_action = QAction("Configuración", self)
        logs_action = QAction("Logs", self)
        about_action = QAction("Acerca de", self)
        
        menu_navegacion.addAction(chat_action)
        menu_navegacion.addAction(estado_action)
        menu_navegacion.addAction(control_action)
        menu_navegacion.addAction(config_action)
        menu_navegacion.addAction(logs_action)
        menu_navegacion.addAction(about_action)
        
        chat_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.chat_page))
        estado_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.estado_page))
        control_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.control_page))
        config_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.config_page))
        logs_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.logs_page))
        about_action.triggered.connect(lambda: self.page_stack.setCurrentWidget(self.about_page))

    def _toggle_funcion(self, nombre, valor):
        self.funciones[nombre] = valor
        if nombre == 'antivirus':
            if valor:
                self.antivirus_adapter.activar()
            else:
                self.antivirus_adapter.desactivar()
        elif nombre == 'firewall':
            if valor:
                self.firewall_adapter.activar()
            else:
                self.firewall_adapter.desactivar()
        elif nombre == 'proactivo':
            if valor:
                self.proactividad_adapter.activar()
            else:
                self.proactividad_adapter.desactivar()
        elif nombre == 'aprendizaje':
            if valor:
                self.aprendizaje_adapter.activar()
            else:
                self.aprendizaje_adapter.desactivar()
        self.show_notification(f"{'Activada' if valor else 'Desactivada'} la función: {nombre.capitalize()}")
        self._actualizar_estado_panel()

    def _toggle_modo_oscuro(self, valor):
        self.dark_mode = valor
        self.setStyleSheet(get_modern_theme(self.dark_mode))
        self.config_page.modo_oscuro_cb.setChecked(valor)

    def _actualizar_estado_panel(self):
        self.estado_page.actualizar_estado('antivirus', self.antivirus_adapter.estado())
        self.estado_page.actualizar_estado('firewall', self.firewall_adapter.estado())
        self.estado_page.actualizar_estado('proactividad', self.proactividad_adapter.estado())
        self.estado_page.actualizar_estado('aprendizaje', self.aprendizaje_adapter.estado())

    def _actualizar_logs_panel(self):
        logs = self.logs_adapter.obtener_todos_los_logs()
        self.logs_page.todos_los_logs = logs
        self.logs_page.filtrar_logs()
        alertas = self.antivirus_adapter.obtener_alertas()
        if alertas:
            for alerta in alertas[-3:]:
                self.show_notification(f"⚠️ ALERTA: {alerta['mensaje']}", duracion=5000)
        self._actualizar_estado_panel()

    def show_notification(self, mensaje, duracion=3000):
        notif = NotificationWidget(mensaje, duracion, self)
        notif.move(self.geometry().center().x() - notif.width() // 2, 80)
        notif.show()

    def _bloquear_ip(self, ip):
        if ip:
            self.firewall_adapter.bloquear_ip(ip)
            self.show_notification(f"IP {ip} bloqueada.")
            
    def _desbloquear_ip(self, ip):
        if ip:
            self.firewall_adapter.desbloquear_ip(ip)
            self.show_notification(f"IP {ip} desbloqueada.")
            
    def _ejecutar_accion_proactiva(self, accion):
        if accion:
            self.proactividad_adapter.ejecutar_accion(accion)
            self.show_notification(f"Acción proactiva '{accion}' ejecutada.")
            
    def _iniciar_ciclo_aprendizaje(self):
        self.aprendizaje_adapter.iniciar_ciclo()
        self.show_notification("Ciclo de aprendizaje iniciado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SassyMainWindow()
    window.show()
    sys.exit(app.exec()) 