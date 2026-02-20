# ui/layout/menubar.py

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QInputDialog
from PySide6.QtCore import QObject, Signal, QSettings

from ui.layout.manage_data_dialog import ManageDataDialog
import os

class MenuBar(QObject):
    data_updated = Signal()   # 👈 NUEVA SEÑAL
    
    def __init__(self, window, controller):
        super().__init__()
        self.window = window
        self.controller = controller
        self.menubar = window.menuBar()


        # Config settings (NO Paths)
        self.settings = QSettings("BotRPA", "Config")

        self._build()

    # ==================================================
    # BUILD MENU
    # ==================================================
    def _build(self):
        # ================== CONFIG ==================
        config_menu = self.menubar.addMenu("⚙️ Configuración")

        # ---- Mostrar Navegador ----
        self.browser_action = QAction("🌐 Mostrar Navegador", self.window)
        self.browser_action.setCheckable(True)
        self.browser_action.setChecked(self.controller.show_browser)
        self.browser_action.toggled.connect(self.on_toggle_browser)
        config_menu.addAction(self.browser_action)

        # ---- Guardado automático ----
        self.save_data_action = QAction("💾 Guardado automático de datos", self.window)
        self.save_data_action.setCheckable(True)

        saved_value = self.settings.value("auto_save_data", False, type=bool)
        self.save_data_action.setChecked(saved_value)
        self.save_data_action.toggled.connect(self.on_toggle_save_data)

        config_menu.addAction(self.save_data_action)

        # ================== DATOS PERSONALIZADOS ==================
        data_menu = self.menubar.addMenu("🗂 Datos Personalizados")

        add_ubicacion_action = QAction("➕ Agregar Ubicación", self.window)
        add_ubicacion_action.triggered.connect(self.add_ubicacion)
        data_menu.addAction(add_ubicacion_action)

        add_aseguradora_action = QAction("➕ Agregar Aseguradora", self.window)
        add_aseguradora_action.triggered.connect(self.add_aseguradora)
        data_menu.addAction(add_aseguradora_action)

        manage_action = QAction("🗑 Administrar / Borrar Datos", self.window)
        manage_action.triggered.connect(self.manage_data)
        data_menu.addAction(manage_action)

        # ================== APP ==================
        app_menu = self.menubar.addMenu("📦 Aplicación")

        about_action = QAction("❓ Acerca de", self.window)
        about_action.triggered.connect(self.show_about)
        app_menu.addAction(about_action)

        # ---- Reset Total / Borrar Caché ----
        reset_action = QAction("🧹 Reset total (Borrar caché)", self.window)
        reset_action.triggered.connect(self.reset_app_data)
        app_menu.addAction(reset_action)



    # ==================================================
    # CONFIG TOGGLES
    # ==================================================
    def on_toggle_browser(self, checked: bool):
        reply = QMessageBox.warning(
            self.window,
            "Configuración de navegador",
            "⚠️ El cambio se aplicará en el próximo login.\n\n"
            "¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.controller.set_show_browser(checked)
        else:
            self._restore_browser_check()

    def on_toggle_save_data(self, checked: bool):
        self.settings.setValue("auto_save_data", checked)

        QMessageBox.information(
            self.window,
            "Configuración actualizada",
            f"💾 Guardado automático: {'Activado' if checked else 'Desactivado'}",
        )

    def _restore_browser_check(self):
        self.browser_action.blockSignals(True)
        self.browser_action.setChecked(self.controller.show_browser)
        self.browser_action.blockSignals(False)

    # ==================================================
    # AGREGAR UBICACION
    # ==================================================
    def add_ubicacion(self):
        text, ok = QInputDialog.getText(
            self.window,
            "Nueva Ubicación",
            "Ingrese nombre de ubicación:",
        )

        if not ok or not text.strip():
            return

        text = text.strip()
        ubicaciones = self.settings.value("custom_ubicaciones", [], type=list)

        if not isinstance(ubicaciones, list):
            ubicaciones = [ubicaciones]

        if text in ubicaciones:
            QMessageBox.warning(self.window, "Duplicado", "⚠ Ya existe esa ubicación")
            return

        ubicaciones.append(text)
        self.settings.setValue("custom_ubicaciones", ubicaciones)
        self.data_updated.emit()   # 👈 AVISA A LA GUI
        
        QMessageBox.information(
            self.window,
            "Guardado",
            "✅ Ubicación agregada correctamente",
        )

    # ==================================================
    # AGREGAR ASEGURADORA
    # ==================================================
    def add_aseguradora(self):
        text, ok = QInputDialog.getText(
            self.window,
            "Nueva Aseguradora",
            "Ingrese nombre de aseguradora:",
        )

        if not ok or not text.strip():
            return

        text = text.strip()
        aseguradoras = self.settings.value("custom_aseguradoras", [], type=list)

        if not isinstance(aseguradoras, list):
            aseguradoras = [aseguradoras]

        if text in aseguradoras:
            QMessageBox.warning(self.window, "Duplicado", "⚠ Ya existe esa aseguradora")
            return

        aseguradoras.append(text)
        self.settings.setValue("custom_aseguradoras", aseguradoras)
        self.data_updated.emit()
        
        QMessageBox.information(
            self.window,
            "Guardado",
            "✅ Aseguradora agregada correctamente",
        )

    # ==================================================
    # ADMINISTRAR / BORRAR INDIVIDUAL
    # ==================================================
    def manage_data(self):
        ubicaciones = self.settings.value("custom_ubicaciones", [], type=list)
        aseguradoras = self.settings.value("custom_aseguradoras", [], type=list)

        if not isinstance(ubicaciones, list):
            ubicaciones = [ubicaciones]

        if not isinstance(aseguradoras, list):
            aseguradoras = [aseguradoras]

        if not ubicaciones and not aseguradoras:
            QMessageBox.information(
                self.window,
                "Sin datos",
                "No hay datos personalizados guardados.",
            )
            return

        dialog = ManageDataDialog(ubicaciones, aseguradoras, self.window)

        if dialog.exec():
            item = dialog.get_selected()

            if not item:
                return

            reply = QMessageBox.question(
                self.window,
                "Confirmar eliminación",
                f"¿Deseas eliminar:\n\n{item}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

            if item.startswith("📍 "):
                nombre = item.replace("📍 ", "")
                ubicaciones.remove(nombre)
                self.settings.setValue("custom_ubicaciones", ubicaciones)
                self.data_updated.emit()
            elif item.startswith("🏢 "):
                nombre = item.replace("🏢 ", "")
                aseguradoras.remove(nombre)
                self.settings.setValue("custom_aseguradoras", aseguradoras)
                self.data_updated.emit()

            QMessageBox.information(
                self.window,
                "Eliminado",
                "🗑 Dato eliminado correctamente",
            )

    # ==================================================
    # ABOUT
    # ==================================================
    def show_about(self):
        QMessageBox.about(
            self.window,
            "Acerca de",
            "🤖 Bot de Automatización v4.0\n\n"
            "Arquitectura desacoplada\n"
            "Controller + Worker + Playwright\n\n"
            "© 2026",
        )
        
    def reset_app_data(self):
        reply = QMessageBox.warning(
            self.window,
            "Reset total",
            "⚠ Esto eliminará TODA la configuración guardada.\n\n"
            "La aplicación quedará como recién instalada.\n\n"
            "¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        #       🔥 Borrar Configuración
        QSettings("BotRPA", "Config").clear()
        QSettings("BotRPA", "Paths").clear()

        QMessageBox.information(
            self.window,
            "Reset completado",
            "✅ Datos eliminados correctamente.\n\n"
            "La aplicación se reiniciará."
        )

        # 🔄 Reinicio automático (Windows y Linux)
        os.execl(sys.executable, sys.executable, *sys.argv)
