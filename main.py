# main.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from controller.app_controller import AppController
from ui.layout.menubar import MenuBar

def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Bot RPA")
    window.resize(900, 600)

    # controller = AppController(window)
    controller = AppController(window)
    window.menu = MenuBar(window, controller)


    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

