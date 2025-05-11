def get_modern_theme(dark_mode=True):
    if dark_mode:
        return """
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }
            
            QMainWindow {
                background-color: #1E1E1E;
            }
            
            QMenuBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                padding: 5px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QMenu {
                background-color: #2D2D2D;
                border: none;
                border-radius: 8px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                height: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.3);
                min-width: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QToolTip {
                background-color: #2D2D2D;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            
            QMessageBox {
                background-color: #1E1E1E;
            }
            
            QMessageBox QLabel {
                color: white;
            }
            
            QMessageBox QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #106EBE;
            }
            
            QMessageBox QPushButton:pressed {
                background-color: #005A9E;
            }
        """
    else:
        return """
            QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            
            QMainWindow {
                background-color: #FFFFFF;
            }
            
            QMenuBar {
                background-color: rgba(0, 0, 0, 0.05);
                border: none;
                padding: 5px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                height: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(0, 0, 0, 0.2);
                min-width: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QToolTip {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                padding: 5px;
            }
            
            QMessageBox {
                background-color: #FFFFFF;
            }
            
            QMessageBox QLabel {
                color: #000000;
            }
            
            QMessageBox QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #106EBE;
            }
            
            QMessageBox QPushButton:pressed {
                background-color: #005A9E;
            }
        """ 