from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QFileDialog, QComboBox, QTextEdit
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Signal, QSettings, Qt
from .styles import get_combined_styles
from tools.utilidedes import cargar_aseguradoras

class HomeView(QWidget):
    # ---------- señales ----------
    logout_requested = Signal()
    start_requested = Signal(dict)
    pause_requested = Signal()
    resume_requested = Signal()
    stop_requested = Signal()

    def __init__(self, username: str, aseguradoras: list):
        super().__init__()
        self.aseguradoras = aseguradoras

        self.settings = QSettings("BotRPA", "Paths")
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

        
        # --------- selectora ----------
        self.ubicaciones = ["NORDELTA GENERALGENERAL", "NORDELTA", "PUERTOS", "DALVIAN"]
        self.combo_ubicacion = QComboBox()
        self.combo_ubicacion.setEditable(False)
        self.combo_ubicacion.setPlaceholderText("Seleccionar ubicaciones")
        model = QStandardItemModel()

        # placeholder visual (no check, no select)
        placeholder = QStandardItem("Seleccionar ubicaciones")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        # items con checkbox
        for u in self.ubicaciones:
            item = QStandardItem(u)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            model.appendRow(item)

        self.combo_ubicacion.setModel(model)
        self.combo_ubicacion.setCurrentIndex(0)
        
        # --------- selectora asegurador ----------
        self.combo_asegurador = QComboBox()
        self.combo_asegurador.setEditable(False)
        self.combo_asegurador.setPlaceholderText("Seleccionar aseguradora")
        model = QStandardItemModel()        

        placeholder = QStandardItem("Seleccionar aseguradora")
        placeholder.setEnabled(False)
        model.appendRow(placeholder)

        # items con checkbox
        for a in self.aseguradoras:
            item = QStandardItem(a)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            model.appendRow(item)
        
        self.combo_asegurador.setModel(model)
        self.combo_asegurador.setCurrentIndex(0)






        # addWIdget
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

        self.btn_logs = QPushButton("Limpiar Log")
        self.btn_logs.clicked.connect(self.clear_logs)
        
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setObjectName("logs_box")

        content_logs = QHBoxLayout()
        content_logs.addWidget(logs_title)
        content_logs.addStretch()
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

    # ==================================================
    # BOT CONTROLS
    # ==================================================
    def on_start_pause_clicked(self):
        # ▶ Iniciar
        if not self.bot_running:
            ubicaciones = self.get_selected_ubicaciones()
            aseguradoras = self.get_selected_seguro()
            
            polizas = self.settings.value("polizas")
            pago = self.settings.value("pagos")
            excel = self.settings.value("excel")
            guardado = self.settings.value("guardado")

            if not ubicaciones or not aseguradoras:
                self.status_label.setText("⚠ Seleccione ubicación y aseguradora")
                return

            self.bot_running = True
            self.bot_paused = False
            self.btn_start.setText("⏸   Pausar")
            self.btn_stop.setEnabled(True)
            self.status_label.setText("Estado: Ejecutando")

            # self.start_requested.emit(ubicaciones,aseguradoras)
            self.start_requested.emit({
                "ubicaciones": ubicaciones,
                "aseguradoras": aseguradoras,
                "polizas_ubicacion": polizas,
                "pago_ubicacion": pago,
                "excel_ubicacion": excel,
                "guardado_ubicacion": guardado,

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
    # LOGOUT
    # ==================================================
    def on_logout_clicked(self):
        self.btn_logout.setEnabled(False)
        self.btn_logout.setText("⏳ Cerrando sesión...")
        self.logout_requested.emit()


    def clear_logs(self):
        self.logs.clear()

    # ==================================================
    # selectores
    # ==================================================

    def get_selected_ubicaciones(self):
        model = self.combo_ubicacion.model()
        seleccionadas = []

        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.checkState() == Qt.Checked:
                seleccionadas.append(item.text())

        return seleccionadas

    def get_selected_seguro(self):
        model = self.combo_asegurador.model()
        seleccionadas_aseguradoras = []

        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.checkState() == Qt.Checked:
                seleccionadas_aseguradoras.append(item.text())

        return seleccionadas_aseguradoras



    # ==================================================
    # selectores de direciones
    # ==================================================

    
    def select_path(self, key, label):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if path:
            label.setText(path)
            self.settings.setValue(key, path)

    def _load_saved_paths(self):
        paths = {
            "polizas": self.label_polizas,
            "pagos": self.label_pagos,
            "excel": self.label_excel,
            "guardado": self.label_guardado,
        }

        for key, label in paths.items():
            value = self.settings.value(key)
            if value:
                label.setText(value)

