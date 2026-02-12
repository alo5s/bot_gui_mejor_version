# ui/layout/menubar.py

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

class MenuBar:
    def __init__(self, window, controller):
        self.window = window
        self.controller = controller
        self.menubar = window.menuBar()
        self._build()

    def _build(self):
        config_menu = self.menubar.addMenu("⚙️ Configuración")
        
        self.browser_action = QAction("🌐 Mostrar Navegador", self.window)
        self.browser_action.setCheckable(True)
        self.browser_action.setChecked(self.controller.show_browser)
        self.browser_action.toggled.connect(self.on_toggle_browser)
        config_menu.addAction(self.browser_action)


        app_menu = self.menubar.addMenu("📦 Aplicación")

        about_action = QAction("❓ Ayuda", self.window)
        about_action.triggered.connect(self.show_about)
        app_menu.addAction(about_action)


    def on_toggle_browser(self, checked: bool):
        reply = QMessageBox.warning(
            self.window,
            "Configuración de navegador",
            "⚠️ El cambio se aplicará en el próximo login.\n\n"
            "¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.controller.set_show_browser(checked)
        else:
            self._restore_check()


    def _restore_check(self):
        self.browser_action.blockSignals(True)
        self.browser_action.setChecked(self.controller.show_browser)
        self.browser_action.blockSignals(False)

    def show_about(self):
        QMessageBox.about(
            self.window,
            "Acerca de",
            "🤖 Bot de Automatización v4.0\n\n"
            "Arquitectura con Controller\n"
            "Playwright desacoplado del GUI\n\n"
            "© 2025"
        )


