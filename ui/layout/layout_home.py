# ui/layout/layout_home.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QFileDialog, QComboBox, QTextEdit, QDialog
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Signal, QSettings, Qt
from .styles import get_combined_styles
from tools.utilidedes import cargar_aseguradoras

from bot.config.settings import (
    DEFAULT_UBICACIONES,
    DEFAULT_ASEGURADORAS
)

class HomeView(QWidget):
    # ---------- señales ----------
    logout_requested = Signal()
    start_requested = Signal(dict)
    pause_requested = Signal()
    resume_requested = Signal()
    stop_requested = Signal()

    def __init__(self, username: str):
        super().__init__()

        self.settings = QSettings("BotRPA", "Paths")
        self.config_settings = QSettings("BotRPA", "Config")
        self.auto_save_enabled = self.config_settings.value(
            "auto_save_data", False, type=bool
        )
        self.setObjectName("app_widget")

        self.bot_running = False
        self.bot_paused = False

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ================= HEADER =================
        header = QWidget()
        header.setObjectName("app_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        self.user_label = QLabel(f"Usuario: {username}")
        self.user_label.setObjectName("user_label")

        self.status_label = QLabel("Estado: Idle")
        self.status_label.setObjectName("status_label")

        header_layout.addWidget(self.user_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        # ================= CONTROL PANEL =================
        control_card = QWidget()
        control_card.setObjectName("control_card")
        control_layout = QHBoxLayout(control_card)
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(15, 15, 15, 15)

        # ---------- botones ----------
        self.btn_start = QPushButton("▶  Iniciar")
        self.btn_start.clicked.connect(self.on_start_pause_clicked)

        self.btn_stop = QPushButton("⏹   Detener")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.on_stop_clicked)

        self.btn_logout = QPushButton("Cerrar sesión")
        self.btn_logout.clicked.connect(self.on_logout_clicked)

        # --------- selectora ubicaciones ----------
        custom_ubicaciones = self.config_settings.value("custom_ubicaciones", [], type=list)
        if not isinstance(custom_ubicaciones, list):
            custom_ubicaciones = [custom_ubicaciones]

        self.ubicaciones = list(dict.fromkeys(DEFAULT_UBICACIONES + custom_ubicaciones))

        self.combo_ubicacion = QComboBox()
        self.combo_ubicacion.setEditable(False)
        self.combo_ubicacion.setPlaceholderText("Seleccionar ubicaciones")
        model = QStandardItemModel()
        placeholder = QStandardItem("Seleccionar ubicaciones")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        for u in self.ubicaciones:
            item = QStandardItem(u)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            model.appendRow(item)

        self.combo_ubicacion.setModel(model)
        self.combo_ubicacion.setCurrentIndex(0)

        # --------- selectora aseguradoras ----------
        custom_aseguradoras = self.config_settings.value("custom_aseguradoras", [], type=list)
        if not isinstance(custom_aseguradoras, list):
            custom_aseguradoras = [custom_aseguradoras]

        self.aseguradoras = list(dict.fromkeys(DEFAULT_ASEGURADORAS + custom_aseguradoras))

        self.combo_asegurador = QComboBox()
        self.combo_asegurador.setEditable(False)
        self.combo_asegurador.setPlaceholderText("Seleccionar aseguradora")
        model = QStandardItemModel()
        placeholder = QStandardItem("Seleccionar aseguradora")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        for a in self.aseguradoras:
            item = QStandardItem(a)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            model.appendRow(item)

        self.combo_asegurador.setModel(model)
        self.combo_asegurador.setCurrentIndex(0)

        # add widgets al control
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.combo_ubicacion)
        control_layout.addWidget(self.combo_asegurador)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_logout)

        # ================= PATHS =================
        paths_card = QWidget()
        paths_card.setObjectName("paths_card")
        paths_layout = QVBoxLayout()
        paths_layout.setSpacing(10)
        paths_layout.setContentsMargins(15, 15, 15, 15)

        def path_row(title_text, label, btn):
            w = QWidget()
            l = QHBoxLayout()
            l.setContentsMargins(0, 0, 0, 0)
            title = QLabel(title_text)
            title.setObjectName("path_title")
            label.setObjectName("path_label")
            btn.setObjectName("path_btn")
            l.addWidget(title)
            l.addWidget(label, 1)
            l.addWidget(btn)
            w.setLayout(l)
            return w

        self.label_polizas = QLabel("No seleccionada")
        self.label_pagos = QLabel("No seleccionada")
        self.label_excel = QLabel("No seleccionado")
        self.label_guardado = QLabel("No seleccionado")

        self.btn_polizas = QPushButton("Explorar")
        self.btn_pagos = QPushButton("Explorar")
        self.btn_excel = QPushButton("Explorar")
        self.btn_guardado = QPushButton("Explorar")

        paths_layout.addWidget(path_row("📂 Pólizas PDF:", self.label_polizas, self.btn_polizas))
        self.btn_polizas.clicked.connect(lambda: self.select_path("polizas", self.label_polizas))

        paths_layout.addWidget(path_row("📂 Pagos PDF (Opcional):", self.label_pagos, self.btn_pagos))
        self.btn_pagos.clicked.connect(lambda: self.select_path("pagos", self.label_pagos))

        paths_layout.addWidget(path_row("📊 Excel:", self.label_excel, self.btn_excel))
        self.btn_excel.clicked.connect(lambda: self.select_path("excel", self.label_excel))

        paths_layout.addWidget(path_row("📂 Guardado:", self.label_guardado, self.btn_guardado))
        self.btn_guardado.clicked.connect(lambda: self.select_path("guardado", self.label_guardado))

        paths_card.setLayout(paths_layout)

        # ================= LOGS =================
        logs_card = QWidget()
        logs_card.setObjectName("logs_card")
        logs_layout = QVBoxLayout()
        logs_layout.setContentsMargins(15, 15, 15, 15)

        logs_title = QLabel("Logs del sistema")
        logs_title.setObjectName("logs_title")

        self.btn_clear_data = QPushButton("🧹 Borrar datos guardados")
        self.btn_clear_data.clicked.connect(self.clear_saved_data)

        self.btn_logs = QPushButton("Limpiar Log")
        self.btn_logs.clicked.connect(self.clear_logs)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setObjectName("logs_box")

        content_logs = QHBoxLayout()
        content_logs.addWidget(logs_title)
        content_logs.addStretch()
        content_logs.addWidget(self.btn_clear_data)
        content_logs.addWidget(self.btn_logs)

        logs_layout.addLayout(content_logs)
        logs_layout.addWidget(self.logs)
        logs_card.setLayout(logs_layout)

        # ================= layout =================
        main_layout.addWidget(header)
        main_layout.addWidget(control_card)
        main_layout.addWidget(paths_card)
        main_layout.addWidget(logs_card, 1)

        self.setStyleSheet(get_combined_styles())

        # 🔥 Restaurar datos si está activado
        self._load_saved_paths()
        self._load_saved_selections()

    # ==================================================
    # BOT CONTROLS
    # ==================================================
    def on_start_pause_clicked(self):
        ubicaciones = self.get_selected_ubicaciones()
        aseguradoras = self.get_selected_seguro()

        # validar ubicación obligatoria
        if not ubicaciones:
            self.status_label.setText("⚠ Seleccione al menos una ubicación")
            return

        if not aseguradoras:
            self.status_label.setText("⚠ Seleccione al menos una aseguradora")
            return

        if not self.bot_running:
            if self.auto_save_enabled:
                self.settings.setValue("ubicaciones_seleccionadas", ubicaciones)
                self.settings.setValue("aseguradoras_seleccionadas", aseguradoras)

            self.bot_running = True
            self.btn_start.setText("⏸   Pausar")
            self.btn_stop.setEnabled(True)
            self.status_label.setText("Estado: Ejecutando")

            self.start_requested.emit({
                "ubicaciones": ubicaciones,
                "aseguradoras": aseguradoras,
                "polizas_ubicacion": self.settings.value("polizas"),
                "pago_ubicacion": self.settings.value("pagos"),
                "excel_ubicacion": self.settings.value("excel"),
                "guardado_ubicacion": self.settings.value("guardado"),
            })
            return

        # ⏸ Pausar
        if self.bot_running and not self.bot_paused:
            self.bot_paused = True
            self.btn_start.setText("▶  Reanudar")
            self.status_label.setText("Estado: Pausado")
            self.pause_requested.emit()
            return

        # ▶ Reanudar
        if self.bot_running and self.bot_paused:
            self.bot_paused = False
            self.btn_start.setText("⏸   Pausar")
            self.status_label.setText("Estado: Ejecutando")
            self.resume_requested.emit()

    def on_stop_clicked(self):
        self.reset_bot_ui()
        self.stop_requested.emit()

    def reset_bot_ui(self):
        self.bot_running = False
        self.bot_paused = False
        self.btn_start.setText("▶  Iniciar")
        self.btn_stop.setEnabled(False)
        self.status_label.setText("Estado: Detenido")

    # ==================================================
    # CLEAR DATA
    # ==================================================
    def clear_saved_data(self):
        reply = QMessageBox.warning(
            self,
            "Borrar datos",
            "⚠ ¿Deseas borrar todos los datos guardados?\n\n"
            "Se eliminarán paths y selecciones.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.settings.clear()

        # Reset labels
        self.label_polizas.setText("No seleccionada")
        self.label_pagos.setText("No seleccionada")
        self.label_excel.setText("No seleccionado")
        self.label_guardado.setText("No seleccionado")

        # Reset checkboxes
        for combo in [self.combo_ubicacion, self.combo_asegurador]:
            model = combo.model()
            for i in range(model.rowCount()):
                item = model.item(i)
                if item and item.isCheckable():
                    item.setCheckState(Qt.Unchecked)

        QMessageBox.information(self, "Datos borrados", "✅ Datos eliminados correctamente")

    # ==================================================
    # LOGOUT
    # ==================================================
    def on_logout_clicked(self):
        self.btn_logout.setEnabled(False)
        self.btn_logout.setText("⏳ Cerrando sesión...")
        self.logout_requested.emit()

    def clear_logs(self):
        self.logs.clear()

    # ==================================================
    # HELPERS
    # ==================================================
    def get_selected_ubicaciones(self):
        model = self.combo_ubicacion.model()
        return [
            model.item(i).text()
            for i in range(model.rowCount())
            if model.item(i) and model.item(i).checkState() == Qt.Checked
        ]

    def get_selected_seguro(self):
        model = self.combo_asegurador.model()
        return [
            model.item(i).text()
            for i in range(model.rowCount())
            if model.item(i) and model.item(i).checkState() == Qt.Checked
        ]

    # ==================================================
    # PATHS
    # ==================================================
    def select_path(self, key, label):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if path:
            label.setText(path)
            if self.auto_save_enabled:
                self.settings.setValue(key, path)

    def _load_saved_paths(self):
        if not self.auto_save_enabled:
            return
        for key, label in {
            "polizas": self.label_polizas,
            "pagos": self.label_pagos,
            "excel": self.label_excel,
            "guardado": self.label_guardado,
        }.items():
            value = self.settings.value(key)
            if value:
                label.setText(value)

    def _load_saved_selections(self):
        if not self.auto_save_enabled:
            return
        ubicaciones = self.settings.value("ubicaciones_seleccionadas", [])
        aseguradoras = self.settings.value("aseguradoras_seleccionadas", [])

        if isinstance(ubicaciones, str):
            ubicaciones = [ubicaciones]
        if isinstance(aseguradoras, str):
            aseguradoras = [aseguradoras]

        for combo, saved in [
            (self.combo_ubicacion, ubicaciones),
            (self.combo_asegurador, aseguradoras),
        ]:
            model = combo.model()
            for i in range(model.rowCount()):
                item = model.item(i)
                if item and item.text() in saved:
                    item.setCheckState(Qt.Checked)

    # ==================================================
    # RECARGAR DATOS PERSONALIZADOS (DESDE MENUBAR)
    # ==================================================
    def reload_custom_data(self):
        # guardar selección actual para no perder checks
        selected_ubicaciones = self.get_selected_ubicaciones()
        selected_aseguradoras = self.get_selected_seguro()

        # recargar settings
        self.config_settings = QSettings("BotRPA", "Config")

        # -------- UBICACIONES --------
        custom_ubicaciones = self.config_settings.value("custom_ubicaciones", [], type=list)
        if not isinstance(custom_ubicaciones, list):
            custom_ubicaciones = [custom_ubicaciones]

        self.ubicaciones = list(dict.fromkeys(DEFAULT_UBICACIONES + custom_ubicaciones))

        model = QStandardItemModel()
        placeholder = QStandardItem("Seleccionar ubicaciones")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        for u in self.ubicaciones:
            item = QStandardItem(u)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(
                Qt.Checked if u in selected_ubicaciones else Qt.Unchecked,
                Qt.CheckStateRole,
            )
            model.appendRow(item)

        self.combo_ubicacion.setModel(model)
        self.combo_ubicacion.setCurrentIndex(0)

        # -------- ASEGURADORAS --------
        custom_aseguradoras = self.config_settings.value("custom_aseguradoras", [], type=list)
        if not isinstance(custom_aseguradoras, list):
            custom_aseguradoras = [custom_aseguradoras]

        self.aseguradoras = list(dict.fromkeys(DEFAULT_ASEGURADORAS + custom_aseguradoras))

        model = QStandardItemModel()
        placeholder = QStandardItem("Seleccionar aseguradora")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        for a in self.aseguradoras:
            item = QStandardItem(a)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(
                Qt.Checked if a in selected_aseguradoras else Qt.Unchecked,
                Qt.CheckStateRole,
            )
            model.appendRow(item)

        self.combo_asegurador.setModel(model)
        self.combo_asegurador.setCurrentIndex(0)

    # ==================================================
    # ALERTAS
    # ==================================================
    def show_poliza_alert(self, mensaje: str):
        QMessageBox.information(self, "Póliza terminada", mensaje)

    def show_persona_no_encontrada(self, dni: str, poliza: str, nombre: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Persona no encontrada")
        dialog.setObjectName("persona_alert_box")
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 🔴 Título principal
        label_title = QLabel("⚠ Persona no encontrada")
        label_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #d9534f;")

        label_poliza = QLabel(f"Póliza: {poliza}")
        label_poliza.setObjectName("persona_alert_poliza")

        label_nombre = QLabel(nombre)
        label_nombre.setObjectName("persona_alert_nombre")

        label_dni = QLabel(f"DNI: {dni}")
        label_dni.setStyleSheet("color: #777; font-size: 13px;")

        btn_ok = QPushButton("Cerrar")
        btn_ok.clicked.connect(dialog.accept)

        layout.addWidget(label_title)
        layout.addWidget(label_poliza)
        layout.addWidget(label_nombre)
        layout.addWidget(label_dni)
        layout.addSpacing(10)
        layout.addWidget(btn_ok)

        dialog.exec()

        self.status_label.setText("⚠ Persona no encontrada")
        self.logs.append(
            f"Persona no encontrada | DNI: {dni} | Póliza: {poliza} | {nombre}"
        )

