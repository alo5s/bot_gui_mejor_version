# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from ui.layout.menubar import MenuBar

def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Bot RPA")
    window.resize(900, 600)

    window.show()  # Mostrar ventana rápido

    # Inicializar controlador y menubar después de renderizar la ventana
    QTimer.singleShot(0, lambda: init_controller(window))

    sys.exit(app.exec())

def init_controller(window):
    from controller.app_controller import AppController
    controller = AppController(window)
    window.menu = MenuBar(window, controller)

if __name__ == "__main__":
    main()
