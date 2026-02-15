from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QHBoxLayout
)


class ManageDataDialog(QDialog):
    def __init__(self, ubicaciones, aseguradoras, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Administrar Datos")
        self.setMinimumWidth(400)

        self.selected_item = None

        layout = QVBoxLayout(self)

        label = QLabel("Selecciona el dato que deseas eliminar:")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Cargar datos
        for u in ubicaciones:
            self.list_widget.addItem(f"📍 {u}")

        for a in aseguradoras:
            self.list_widget.addItem(f"🏢 {a}")

        # Botones
        btn_layout = QHBoxLayout()

        self.delete_btn = QPushButton("🗑 Eliminar")
        self.cancel_btn = QPushButton("Cancelar")

        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.delete_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_selected(self):
        item = self.list_widget.currentItem()
        if item:
            return item.text()
        return None

